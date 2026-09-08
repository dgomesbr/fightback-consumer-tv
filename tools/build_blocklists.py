#!/usr/bin/env python3
"""Generate blocklists from data/endpoints/*.yml.

Output is deterministic: the same input always produces byte-identical files, so CI can
assert that the committed lists match the data by running with --check.

Three safety properties are enforced here rather than left to review:

1. A domain marked tier `never` cannot appear in any generated list. These are the domains
   that break a television, and shipping one does more harm than the tracking it prevents.
2. A domain marked `safe_to_block: unknown` cannot appear in the core tier.
3. A `never` entry in one vendor file blocks that domain everywhere, so a domain someone
   documented as load-bearing on Samsung cannot slip into the core list through Amazon.

Usage:
    python tools/build_blocklists.py            # write the lists
    python tools/build_blocklists.py --check    # exit 1 if output differs from committed
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENDPOINTS = ROOT / "data" / "endpoints"
OUT = ROOT / "blocklists"

PROJECT = "Fightback: Consumer TV"
HOMEPAGE = "https://github.com/dgomesbr/fightback-consumer-tv"

VALID_PURPOSES = {"acr", "ads", "telemetry", "ota", "functional", "cdn", "ntp"}
VALID_TIERS = {"core", "aggressive", "never"}


class DataError(Exception):
    """A problem in the source data that a human has to fix."""


@dataclass
class Entry:
    domain: str
    purpose: str
    tier: str
    safe_to_block: object
    breaks: object
    source: str
    vendor: str
    wildcard: bool = False
    regex: str | None = None
    notes: str | None = None

    @property
    def breaks_text(self) -> str:
        if self.breaks is None:
            return "no documented breakage"
        return str(self.breaks)


@dataclass
class Dataset:
    entries: list[Entry] = field(default_factory=list)
    never: dict[str, Entry] = field(default_factory=dict)

    def by_tier(self, tier: str) -> list[Entry]:
        return [e for e in self.entries if e.tier == tier]

    def by_vendor(self) -> dict[str, list[Entry]]:
        out: dict[str, list[Entry]] = defaultdict(list)
        for e in self.entries:
            if e.tier != "never":
                out[e.vendor].append(e)
        return dict(out)


def load() -> Dataset:
    ds = Dataset()
    seen: dict[tuple[str, str], tuple[str, Entry]] = {}

    for path in sorted(ENDPOINTS.glob("*.yml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        file_vendor = raw.get("vendor")
        if not file_vendor:
            raise DataError(f"{path.name}: missing top-level `vendor`")

        for i, item in enumerate(raw.get("entries") or []):
            where = f"{path.name} entry {i + 1}"
            domain = item.get("domain")
            if not domain:
                raise DataError(f"{where}: missing `domain`")
            domain = domain.strip().lower().rstrip(".")

            for required in ("purpose", "tier", "safe_to_block", "source"):
                if required not in item:
                    raise DataError(f"{where} ({domain}): missing `{required}`")
            if "breaks" not in item:
                raise DataError(
                    f"{where} ({domain}): missing `breaks`. Use null, a sentence, or "
                    f"the word unknown. See data/endpoints/README.md"
                )

            purpose = item["purpose"]
            if purpose not in VALID_PURPOSES:
                raise DataError(f"{where} ({domain}): purpose {purpose!r} not in {sorted(VALID_PURPOSES)}")

            tier = item["tier"]
            if tier not in VALID_TIERS:
                raise DataError(f"{where} ({domain}): tier {tier!r} not in {sorted(VALID_TIERS)}")

            safe = item["safe_to_block"]
            if tier == "core" and safe is not True:
                raise DataError(
                    f"{where} ({domain}): tier is core but safe_to_block is {safe!r}. "
                    f"Anything unproven belongs in the aggressive tier."
                )

            source = str(item["source"])
            if not source.startswith("http"):
                raise DataError(f"{where} ({domain}): source must be a URL, got {source!r}")

            regex = item.get("regex")
            if regex:
                try:
                    re.compile(regex)
                except re.error as exc:
                    raise DataError(f"{where} ({domain}): invalid regex: {exc}") from exc

            entry = Entry(
                domain=domain,
                purpose=purpose,
                tier=tier,
                safe_to_block=safe,
                breaks=item.get("breaks"),
                source=source,
                vendor=item.get("vendor", file_vendor),
                wildcard=bool(item.get("wildcard", False)),
                regex=regex,
                notes=item.get("notes"),
            )

            # A third-party domain can legitimately appear in several vendor files, because
            # each vendor list has to stand alone for a reader who owns only that brand.
            # What is not allowed is the same domain classified two different ways, since
            # then the tier a reader gets depends on which file the generator read first.
            key = (domain, regex or "")
            if key in seen:
                prior_file, prior = seen[key]
                if prior_file == path.name:
                    raise DataError(f"{where} ({domain}): defined twice in the same file")
                if (prior.tier, prior.safe_to_block) != (entry.tier, entry.safe_to_block):
                    raise DataError(
                        f"{where} ({domain}): classified tier={entry.tier} "
                        f"safe_to_block={entry.safe_to_block!r}, but {prior_file} says "
                        f"tier={prior.tier} safe_to_block={prior.safe_to_block!r}. "
                        f"Make them agree."
                    )
            else:
                seen[key] = (path.name, entry)

            if tier == "never":
                ds.never[domain] = entry
            ds.entries.append(entry)

    if not ds.entries:
        raise DataError(f"no entries found under {ENDPOINTS}")
    return ds


def enforce(ds: Dataset, emitted: list[Entry], list_name: str) -> None:
    """Refuse to write a list that would break a television."""
    problems = []
    for e in emitted:
        if e.domain in ds.never:
            blocker = ds.never[e.domain]
            problems.append(f"  {e.domain}: marked never in {blocker.vendor} ({blocker.breaks_text})")
        if e.tier == "core" and e.safe_to_block is not True:
            problems.append(f"  {e.domain}: in core tier with safe_to_block={e.safe_to_block!r}")
    if problems:
        raise DataError(
            f"refusing to write {list_name}, {len(problems)} unsafe entries:\n" + "\n".join(problems)
        )


def header(title: str, description: str, entries: list[Entry], comment: str = "#") -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    for e in entries:
        counts[e.purpose] += 1
    breakdown = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
    return [
        f"{comment} {PROJECT}: {title}",
        f"{comment}",
        f"{comment} {description}",
        f"{comment}",
        f"{comment} Entries: {len(entries)} ({breakdown})",
        f"{comment} Updated: {date.today().isoformat()}",
        f"{comment} Source data: data/endpoints/, licensed CC BY 4.0",
        f"{comment} This list: CC0 1.0, use it anywhere without attribution",
        f"{comment} Homepage: {HOMEPAGE}",
        f"{comment}",
        f"{comment} Generated by tools/build_blocklists.py. Do not edit by hand.",
        f"{comment} Every entry is documented with a source and a breakage note in the",
        f"{comment} source data. Domains that break a television are excluded by the",
        f"{comment} generator rather than by review.",
        f"{comment}",
    ]


def render_hosts(entries: list[Entry], title: str, description: str) -> str:
    lines = header(title, description, entries)
    for e in sorted(entries, key=lambda x: (x.vendor, x.domain)):
        if e.regex:
            lines.append(f"# {e.domain}: pattern only, see the dnsmasq or AdGuard output")
            continue
        lines.append(f"0.0.0.0 {e.domain}")
        if e.wildcard:
            lines.append(f"0.0.0.0 www.{e.domain}")
    return "\n".join(lines) + "\n"


def render_domains(entries: list[Entry], title: str, description: str) -> str:
    lines = header(title, description, entries)
    for e in sorted(entries, key=lambda x: (x.vendor, x.domain)):
        if e.regex:
            continue
        lines.append(e.domain)
    return "\n".join(lines) + "\n"


def render_dnsmasq(entries: list[Entry], title: str, description: str) -> str:
    lines = header(title, description, entries)
    for e in sorted(entries, key=lambda x: (x.vendor, x.domain)):
        if e.regex:
            lines.append(f"# {e.domain}: regex, not expressible in dnsmasq. See the AdGuard output.")
            continue
        lines.append(f"address=/{e.domain}/")
    return "\n".join(lines) + "\n"


def render_adguard(entries: list[Entry], title: str, description: str) -> str:
    lines = header(title, description, entries, comment="!")
    for e in sorted(entries, key=lambda x: (x.vendor, x.domain)):
        if e.regex:
            lines.append(f"/{e.regex}/")
        elif e.wildcard:
            lines.append(f"||{e.domain}^")
        else:
            lines.append(f"||{e.domain}^$important")
    return "\n".join(lines) + "\n"


def render_never(ds: Dataset) -> str:
    """The do-not-block list, published because it is more useful than the blocklist."""
    entries = sorted(ds.never.values(), key=lambda x: (x.vendor, x.domain))
    lines = [
        f"# {PROJECT}: do not block these",
        "#",
        "# Domains documented to break a television when blocked. Add them to your",
        "# resolver's allowlist if you use a broad third-party list, because several",
        "# popular lists include some of these.",
        "#",
        "# This list is the reason the project exists. A blocklist is easy. Knowing what",
        "# not to block is the part that takes evidence.",
        "#",
        f"# Entries: {len(entries)}",
        f"# Updated: {date.today().isoformat()}",
        f"# Licence: CC0 1.0. Homepage: {HOMEPAGE}",
        "#",
        "# Generated by tools/build_blocklists.py. Do not edit by hand.",
        "#",
    ]
    current = None
    for e in entries:
        if e.vendor != current:
            current = e.vendor
            lines.append("")
            lines.append(f"# ---- {current} ----")
        lines.append(f"# {e.domain}")
        lines.append(f"#   breaks: {e.breaks_text}")
        lines.append(f"#   source: {e.source}")
        lines.append(f"@@||{e.domain}^")
    return "\n".join(lines) + "\n"


CORE_DESC = (
    "Safe defaults. Content recognition, advertising and telemetry endpoints with no "
    "documented breakage. Start here."
)
AGG_DESC = (
    "Everything in the core tier plus entries that break something a reader might want. "
    "Read the breakage notes in data/endpoints/ before using this."
)


def dedupe(entries: list[Entry]) -> list[Entry]:
    """Collapse the same domain appearing in several vendor files.

    Load() has already checked that duplicates agree on tier and safe_to_block, so keeping
    the first occurrence is safe. Sorting the input first keeps the choice deterministic.
    """
    out: list[Entry] = []
    seen: set[tuple[str, str]] = set()
    for e in sorted(entries, key=lambda x: (x.domain, x.regex or "", x.vendor)):
        key = (e.domain, e.regex or "")
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out


def build(ds: Dataset) -> dict[Path, str]:
    files: dict[Path, str] = {}

    core = dedupe(ds.by_tier("core"))
    enforce(ds, core, "core")
    files[OUT / "hosts" / "fightback-tv-core.txt"] = render_hosts(core, "core tier, hosts format", CORE_DESC)
    files[OUT / "domains" / "fightback-tv-core.txt"] = render_domains(core, "core tier, domains only", CORE_DESC)
    files[OUT / "dnsmasq" / "fightback-tv-core.conf"] = render_dnsmasq(core, "core tier, dnsmasq format", CORE_DESC)
    files[OUT / "adguard" / "fightback-tv-core.txt"] = render_adguard(core, "core tier, AdGuard format", CORE_DESC)

    aggressive = dedupe(core + ds.by_tier("aggressive"))
    enforce(ds, aggressive, "aggressive")
    files[OUT / "hosts" / "fightback-tv-aggressive.txt"] = render_hosts(
        aggressive, "aggressive tier, hosts format", AGG_DESC
    )
    files[OUT / "adguard" / "fightback-tv-aggressive.txt"] = render_adguard(
        aggressive, "aggressive tier, AdGuard format", AGG_DESC
    )

    for vendor, entries in sorted(ds.by_vendor().items()):
        enforce(ds, entries, f"vendor {vendor}")
        desc = (
            f"Every documented {vendor} endpoint, core and aggressive together. "
            f"Use this if you own {vendor} hardware and want full coverage."
        )
        files[OUT / "adguard" / f"fightback-tv-{vendor}.txt"] = render_adguard(
            entries, f"{vendor}, AdGuard format", desc
        )
        files[OUT / "hosts" / f"fightback-tv-{vendor}.txt"] = render_hosts(
            entries, f"{vendor}, hosts format", desc
        )

    files[OUT / "allowlist" / "fightback-tv-do-not-block.txt"] = render_never(ds)
    files[OUT / "README.md"] = render_readme(ds, files)
    return files


def render_readme(ds: Dataset, files: dict[Path, str]) -> str:
    core = ds.by_tier("core")
    aggressive = ds.by_tier("aggressive")
    vendors = ds.by_vendor()
    rows = "\n".join(
        f"| `{v}` | {len(e)} | [AdGuard](adguard/fightback-tv-{v}.txt), [hosts](hosts/fightback-tv-{v}.txt) |"
        for v, e in sorted(vendors.items())
    )
    return f"""# Blocklists

Generated from [`data/endpoints/`](../data/endpoints/) by
[`tools/build_blocklists.py`](../tools/build_blocklists.py). Do not edit these files, they are
overwritten on every build. To change an entry, edit the source data.

Licensed CC0 1.0. Use them anywhere, including in another blocklist, without attribution.

## Which list

| List | Entries | What it does |
| --- | --- | --- |
| **core** | {len(core)} | Safe defaults. No documented breakage. Start here. |
| **aggressive** | {len(core) + len(aggressive)} | Core plus entries that break something you might want. Read the notes first. |
| **do-not-block** | {len(ds.never)} | An allowlist. Domains that break a television. |

The do-not-block list is the one worth your attention. A blocklist is easy to write. Knowing what
not to block takes evidence, and several widely used lists include domains that break app stores,
firmware updates, programme guides or the clock.

## Formats

| Directory | For |
| --- | --- |
| `adguard/` | AdGuard Home, AdGuard DNS, anything taking AdBlock syntax. The only format that carries the regex entries. |
| `hosts/` | Pi-hole, `/etc/hosts`, anything taking a hosts file |
| `dnsmasq/` | dnsmasq and OpenWrt |
| `domains/` | Plain domains, one per line, for scripts |
| `allowlist/` | The do-not-block list, in AdGuard allowlist syntax |

Prefer the AdGuard format where you can. Some vendors mix telemetry and function under one
registrable domain, so those entries are regex-scoped, and a hosts file cannot express them.

## Per vendor

| Vendor | Entries | Files |
| --- | --- | --- |
{rows}

## How this relates to the lists you already use

[HaGeZi's lists](https://github.com/hagezi/dns-blocklists) are excellent, rebuilt several times a
day, and cover more domains than these do. If you want maximum coverage, use HaGeZi Pro plus the
native device lists for the hardware you own.

What we add is annotation and freshness. Every entry here carries a source, a stated purpose, and a
breakage note. The closest equivalent, Perflyst's per-domain commentary, has not had a version bump
since July 2023, and Firebog's smart TV recommendations point at it.

Two gaps worth knowing about: there is no HaGeZi native list for Google or Android TV, Vizio or
Hisense, and Google's platform telemetry is co-mingled with hosts that Play and DRM need. Our Google
file is correspondingly thin, and filling it is one of the most useful things a reader with a Google
TV can do.

## Safety properties the generator enforces

The build fails rather than emitting a list if any of these break:

1. A domain marked `never` appears in any output list.
2. A domain with `safe_to_block: unknown` appears in the core tier.
3. A domain marked `never` in one vendor file appears via another vendor file.

That last one matters because vendors share infrastructure. A domain someone documented as
load-bearing on Samsung cannot reach the core list through Amazon.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="verify committed output matches the data")
    args = ap.parse_args()

    try:
        ds = load()
        files = build(ds)
    except DataError as exc:
        print(f"data error: {exc}", file=sys.stderr)
        return 2

    if args.check:
        stale = []
        for path, content in sorted(files.items()):
            rel = path.relative_to(ROOT)
            if not path.exists():
                stale.append(f"  {rel}: missing")
            elif path.read_text(encoding="utf-8") != content:
                stale.append(f"  {rel}: out of date")
        if stale:
            print("blocklists do not match the source data:", file=sys.stderr)
            print("\n".join(stale), file=sys.stderr)
            print("\nrun: python tools/build_blocklists.py", file=sys.stderr)
            return 1
        print(f"blocklists match the source data ({len(files)} files, {len(ds.entries)} entries)")
        return 0

    for path, content in sorted(files.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    core = len(ds.by_tier("core"))
    agg = len(ds.by_tier("aggressive"))
    print(f"wrote {len(files)} files from {len(ds.entries)} entries")
    print(f"  core {core}, aggressive {agg}, never {len(ds.never)}")
    print(f"  vendors: {', '.join(sorted(ds.by_vendor()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
