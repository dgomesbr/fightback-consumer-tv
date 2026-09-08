#!/usr/bin/env python3
"""Turn the DNS query log you already have into a scrubbed device report.

Local-only by default. The report is written to disk and nothing is transmitted. Submission
is a separate, explicit flag, and there is no code path that sends a report you have not been
shown first.

    # see what it would produce, send nothing
    python fightback.py --source adguard-file --log /opt/AdGuardHome/data/querylog.json \\
        --device 192.168.1.42 --vendor lg --model "LG OLED C3" --region GB --preview

    # write it to disk
    python fightback.py ... --out my-report.json

    # open a pull request with it
    python fightback.py ... --submit

Read PRIVACY.md for the field-by-field list of what this collects and what it refuses to.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from collector.router import scrub, sources  # noqa: E402

VERSION = "0.1.0"
SCHEMA_VERSION = 1

REPO = "dgomesbr/fightback-consumer-tv"
SALT_PATH = Path.home() / ".config" / "fightback" / "salt"

VENDORS = [
    "lg", "samsung", "roku", "amazon", "google", "sony", "tcl", "hisense", "vizio",
    "philips", "panasonic", "sharp", "toshiba", "xiaomi", "apple", "nvidia",
    "insignia", "onn", "other",
]
PLATFORMS = [
    "webos", "tizen", "roku", "fire-os", "google-tv", "android-tv", "vidaa",
    "smartcast", "tvos", "titan-os", "my-home-screen", "saphi", "other",
]
SCENARIOS = ["idle", "linear", "fast", "ott", "hdmi", "screencast", "standby", "mixed"]
ACR_STATES = ["optin", "optout", "unavailable", "unknown"]

# Powers of two, so a byte count cannot be used as a viewing-behaviour side channel.
def bucket_bytes(n: int | None) -> int | None:
    if not n or n <= 0:
        return 0 if n == 0 else None
    return 1 << (n.bit_length() - 1)


def floor_hour(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0).strftime(
        "%Y-%m-%dT%H:00:00Z"
    )


def submitter_key() -> str:
    """A salted hash that counts contributors without identifying one.

    The salt is generated here and never leaves this machine, so we can count distinct
    contributors and you can still prove which rows are yours if you want them deleted.
    Following the IoT Inspector design, which did the same thing under IRB approval.
    """
    import hashlib

    if SALT_PATH.exists():
        salt = SALT_PATH.read_text(encoding="utf-8").strip()
    else:
        salt = uuid.uuid4().hex
        SALT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SALT_PATH.write_text(salt, encoding="utf-8")
        try:
            os.chmod(SALT_PATH, 0o600)
        except OSError:
            pass
    return hashlib.sha256(salt.encode("utf-8")).hexdigest()


def normalise_model(vendor: str, raw: str) -> str:
    """Trim a regional SKU down to a family.

    A full model number plus a country plus a firmware version is a very small cohort, and
    sometimes a cohort of one. OLED55C34LA and OLED65C36LB are the same television for our
    purposes, so both become LG OLED C3.
    """
    text = re.sub(r"\s+", " ", raw.strip())
    lg = re.match(r"^(?:LG\s+)?(OLED|QNED|NANO|UP|UQ|UR)\s*(\d{2})?([A-Z]\d)", text, re.I)
    if lg and vendor == "lg":
        return f"LG {lg.group(1).upper()} {lg.group(3).upper()}"
    samsung = re.match(r"^(?:Samsung\s+)?([A-Z]{2})(\d{2})([A-Z]{1,2}\d{3,4})", text, re.I)
    if samsung and vendor == "samsung":
        return f"Samsung {samsung.group(3).upper()}"
    return text[:60]


def build_report(args, result: sources.SourceResult) -> dict:
    now = datetime.now(timezone.utc)
    observations = []
    dropped = 0

    for obs in result.observations:
        norm = scrub.normalise(obs.hostname)
        if norm is None:
            dropped += 1
            continue
        first = obs.first_seen or now
        last = obs.last_seen or now
        if last < first:
            first, last = last, first
        observations.append(
            {
                "fqdn_template": norm.fqdn_template,
                "registrable_domain": norm.registrable_domain,
                "original_label_count": norm.original_label_count,
                "redacted_label_count": norm.redacted_label_count,
                "dest_port": obs.dest_port,
                "l4proto": obs.l4proto,
                "l7proto": obs.l7proto,
                "first_seen": floor_hour(first),
                "last_seen": floor_hour(last),
                "count": max(1, obs.count),
                "blocked": obs.blocked,
                "scenario": args.scenario,
            }
        )

    # Collapse rows that normalised to the same template, which happens when a vendor uses
    # per-request identifier subdomains: a hundred distinct names become one row.
    collapsed: dict[str, dict] = {}
    for row in observations:
        key = row["fqdn_template"]
        if key in collapsed:
            prior = collapsed[key]
            prior["count"] += row["count"]
            prior["first_seen"] = min(prior["first_seen"], row["first_seen"])
            prior["last_seen"] = max(prior["last_seen"], row["last_seen"])
            prior["redacted_label_count"] = max(
                prior["redacted_label_count"], row["redacted_label_count"]
            )
            if row["blocked"]:
                prior["blocked"] = True
        else:
            collapsed[key] = row
    observations = sorted(collapsed.values(), key=lambda r: (-r["count"], r["fqdn_template"]))

    report = {
        "schema_version": SCHEMA_VERSION,
        "report_id": str(uuid.uuid4()),
        "submitter_key": submitter_key(),
        "submitted_at": floor_hour(now),
        "tool": {"name": "fightback-collector", "version": VERSION},
        "capture_method": args.capture_method,
        "resolver_kind": args.resolver_kind,
        "device": {
            "vendor": args.vendor,
            "model_family": normalise_model(args.vendor, args.model),
            "platform": args.platform,
            "os_major": args.os_major,
            "year_class": args.year,
            "region": args.region.upper(),
            "locale": args.locale,
            "app_inventory": None,
        },
        "settings": {
            "acr_state": args.acr,
            "ad_personalization": args.ads,
            "account_signed_in": args.signed_in,
            "ota_updates": None,
            "microphone": None,
        },
        "observations": observations,
    }
    if args.notes:
        report["notes"] = scrub.scrub_text(args.notes)

    report["_dropped_non_hostnames"] = dropped
    return report


def print_preview(report: dict, result: sources.SourceResult) -> None:
    dropped = report.pop("_dropped_non_hostnames", 0)
    obs = report["observations"]
    redacted = [o for o in obs if "{id}" in o["fqdn_template"]]
    sharded = [o for o in obs if "{n}" in o["fqdn_template"]]
    truncated = [o for o in obs if o["fqdn_template"].startswith("*.")]

    print()
    print("=" * 78)
    print("  This is exactly what would be uploaded. Nothing has been sent.")
    print("=" * 78)
    print()
    print(f"  Device      {report['device']['vendor']} {report['device']['model_family']}"
          f"  ({report['device']['platform']} {report['device']['os_major']}, "
          f"{report['device']['region']})")
    print(f"  Recognition {report['settings']['acr_state']}")
    print(f"  Method      {report['capture_method']}"
          + (f" via {report['resolver_kind']}" if report["resolver_kind"] else ""))
    print(f"  Endpoints   {len(obs)} unique, {sum(o['count'] for o in obs)} lookups")
    if result.window_hours:
        print(f"  Window      {result.window_hours:.0f} hours, timestamps rounded to the hour")
    print()

    def plural(n: int, one: str, many: str) -> str:
        return one if n == 1 else many

    if redacted:
        n = len(redacted)
        print(f"  {n} {plural(n, 'hostname', 'hostnames')} had an identifier removed:")
        for o in redacted[:8]:
            print(f"    {o['fqdn_template']}   ({o['count']} lookups)")
        if n > 8:
            print(f"    ... and {n - 8} more")
        print()
    if truncated:
        n = len(truncated)
        print(f"  {n} {plural(n, 'hostname was', 'hostnames were')} truncated to two labels "
              f"above the domain.")
    if sharded:
        n = len(sharded)
        print(f"  {n} had a numeric server suffix normalised, which is server structure "
              f"rather than an identifier.")
    if dropped:
        print(f"  {dropped} {plural(dropped, 'entry was', 'entries were')} dropped as addresses "
              f"or local names, which we do not collect.")
    print()

    print("  Top endpoints by lookups:")
    for o in obs[:15]:
        flag = " [blocked]" if o.get("blocked") else ""
        print(f"    {o['count']:>7}  {o['fqdn_template']}{flag}")
    if len(obs) > 15:
        print(f"    {'':>7}  ... and {len(obs) - 15} more")
    print()

    print("  Not present in this file, because the schema has no field for them:")
    print("    your IP address, the TV's IP address, MAC addresses, serial numbers,")
    print("    your Wi-Fi network name, other devices on your network, URL paths,")
    print("    payload contents, timestamps finer than one hour.")
    print()
    print("=" * 78)


def submit(report: dict, path: Path) -> int:
    """Open a pull request with the report. Requires the gh CLI, authenticated."""
    if not _have("gh"):
        print(
            "\nThe GitHub CLI is not installed, so this cannot open a pull request.\n"
            f"Your report is saved at {path}\n"
            f"Attach it to a new issue instead:\n"
            f"  https://github.com/{REPO}/issues/new?template=device_report.yml\n",
            file=sys.stderr,
        )
        return 1

    vendor = report["device"]["vendor"]
    model = report["device"]["model_family"].lower().replace(" ", "-")
    branch = f"report/{vendor}-{model}-{report['report_id'][:8]}"
    target = Path("data/reports") / vendor / f"{report['report_id']}.json"

    print(f"\nOpening a pull request on {branch}")
    print(f"  {target}")
    print("\nThis publishes the file you just reviewed. Press Enter to continue, or Ctrl-C to stop.")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing was sent.")
        return 1

    body = (
        f"Device report for {report['device']['vendor']} "
        f"{report['device']['model_family']}, "
        f"{report['device']['platform']} {report['device']['os_major']}, "
        f"{report['device']['region']}.\n\n"
        f"- Content recognition: {report['settings']['acr_state']}\n"
        f"- Capture method: {report['capture_method']}\n"
        f"- Unique endpoints: {len(report['observations'])}\n\n"
        f"Generated by the collector, schema version {SCHEMA_VERSION}. "
        f"Scrubbed locally and reviewed before submission.\n"
    )
    cmd = [
        "gh", "pr", "create", "--repo", REPO, "--title",
        f"Report: {report['device']['vendor']} {report['device']['model_family']}",
        "--body", body,
    ]
    print("\nRun these to finish, from a clone of the repository:\n")
    print(f"  git checkout -b {branch}")
    print(f"  mkdir -p {target.parent}")
    print(f"  cp {path} {target}")
    print(f"  git add {target} && git commit -m 'Report: {report['device']['model_family']}'")
    print(f"  git push -u origin {branch}")
    print("  " + " ".join(_quote(c) for c in cmd))
    print()
    return 0


def _quote(s: str) -> str:
    return f'"{s}"' if " " in s or "\n" in s else s


def _have(exe: str) -> bool:
    from shutil import which

    return which(exe) is not None


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    src = ap.add_argument_group("where to read from")
    src.add_argument(
        "--source",
        required=True,
        choices=["adguard-file", "adguard-api", "pihole", "nextdns", "domains-file"],
    )
    src.add_argument("--log", type=Path, help="path to querylog.json or a plain domains file")
    src.add_argument("--url", help="base URL, for adguard-api and pihole")
    src.add_argument("--token", help="API token or session id. Prefer the environment variable.")
    src.add_argument("--profile", help="NextDNS profile id")
    src.add_argument("--device", default="", help="the TV's address, or its NextDNS device name")
    src.add_argument("--hours", type=int, default=24, help="how far back to read (default 24)")

    dev = ap.add_argument_group("about the device")
    dev.add_argument("--vendor", required=True, choices=VENDORS)
    dev.add_argument("--model", required=True, help='for example "LG OLED C3"')
    dev.add_argument("--platform", required=True, choices=PLATFORMS)
    dev.add_argument("--os-major", required=True, help="major version only, for example 8")
    dev.add_argument("--region", required=True, help="ISO country code, for example GB")
    dev.add_argument("--locale", default=None, help="menu language, for example en")
    dev.add_argument("--year", type=int, default=None, help="model year")

    st = ap.add_argument_group("settings state")
    st.add_argument("--acr", required=True, choices=ACR_STATES,
                    help="was content recognition opted out when you captured this")
    st.add_argument("--ads", default=None, choices=["on", "off", "unavailable", "unknown"])
    st.add_argument("--signed-in", default=None, type=lambda v: v.lower() == "true",
                    help="true or false")
    st.add_argument("--scenario", default=None, choices=SCENARIOS,
                    help="what the TV was doing")

    meta = ap.add_argument_group("provenance")
    meta.add_argument("--capture-method", default="resolver_log",
                      choices=["resolver_log", "router_dnsmasq", "router_unbound", "pcap_ap",
                               "pcap_span", "zeek_span", "on_device_vpnservice", "manual"])
    meta.add_argument("--resolver-kind", default=None,
                      choices=["pihole", "adguardhome", "nextdns", "controld", "blocky",
                               "technitium", "unbound", "dnsmasq", "isp", "unknown"])
    meta.add_argument("--notes", default="", help="max 280 chars, scrubbed for addresses")

    out = ap.add_argument_group("what to do with it")
    out.add_argument("--preview", action="store_true", help="print it and send nothing (default)")
    out.add_argument("--out", type=Path, help="write it to this path")
    out.add_argument("--submit", action="store_true", help="open a pull request with it")

    args = ap.parse_args()

    if not re.fullmatch(r"[A-Za-z]{2}", args.region):
        print("--region takes a two-letter country code, for example GB or US.", file=sys.stderr)
        print("We do not collect city, postcode or coordinates.", file=sys.stderr)
        return 2
    if not re.fullmatch(r"\d{1,3}", args.os_major):
        print(f"--os-major takes the major version only, so 8 rather than {args.os_major!r}.",
              file=sys.stderr)
        print("Full build strings are near-unique per region and batch.", file=sys.stderr)
        return 2

    token = args.token or os.environ.get("FIGHTBACK_TOKEN") or ""

    try:
        if args.source == "adguard-file":
            if not args.log:
                raise sources.SourceError("--log is required for adguard-file")
            result = sources.read_adguard_file(args.log, args.device, args.hours)
            args.resolver_kind = args.resolver_kind or "adguardhome"
        elif args.source == "adguard-api":
            if not args.url:
                raise sources.SourceError("--url is required for adguard-api")
            result = sources.read_adguard_api(args.url, args.device, args.hours, token)
            args.resolver_kind = args.resolver_kind or "adguardhome"
        elif args.source == "pihole":
            if not args.url:
                raise sources.SourceError("--url is required for pihole, for example http://pi.hole")
            result = sources.read_pihole_api(args.url, args.device, args.hours, token)
            args.resolver_kind = args.resolver_kind or "pihole"
        elif args.source == "nextdns":
            if not args.profile:
                raise sources.SourceError("--profile is required for nextdns")
            result = sources.read_nextdns(args.profile, args.device, args.hours, token)
            args.resolver_kind = args.resolver_kind or "nextdns"
        else:
            if not args.log:
                raise sources.SourceError("--log is required for domains-file")
            result = sources.read_domains_file(args.log, args.hours)
            args.capture_method = "manual"
    except sources.SourceError as exc:
        print(f"could not read the log: {exc}", file=sys.stderr)
        return 2

    for note in result.notes:
        print(f"note: {note}", file=sys.stderr)

    if not result.observations:
        print("\nNo observations found, so there is nothing to report.", file=sys.stderr)
        if result.clients_seen:
            print("Clients this resolver has seen:", file=sys.stderr)
            for c in result.clients_seen[:20]:
                print(f"  {c}", file=sys.stderr)
            print("\nPass one of those to --device.", file=sys.stderr)
        return 1

    report = build_report(args, result)
    print_preview(report, result)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Written to {args.out}")

    if args.submit:
        path = args.out or Path("fightback-report.json")
        if not args.out:
            path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return submit(report, path)

    if not args.out:
        print("Nothing was written or sent. Add --out to save it, or --submit to contribute it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
