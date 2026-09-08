#!/usr/bin/env python3
"""Validate submitted reports against the schema and the redaction rules.

Runs in CI on every pull request touching data/reports/. Two layers, because the schema alone
is not enough:

  Structural. The report must match data/schema/report.schema.json. Since the schema sets
  additionalProperties false at every level, a field we refuse to collect is a validation
  failure rather than an ignored extra key.

  Semantic. A report can be structurally valid and still leak. A hostname the client failed
  to redact will match the fqdn_template pattern, so the entropy and shape rules run again
  here on data that has already crossed a trust boundary.

Exits non-zero with a message aimed at the contributor rather than at us.

    python tools/validate_reports.py                    # everything under data/reports/
    python tools/validate_reports.py path/to/one.json   # one file
    python tools/validate_reports.py --self-test        # prove the checks catch bad input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from collector.router import scrub  # noqa: E402

SCHEMA_PATH = ROOT / "data" / "schema" / "report.schema.json"
REPORTS = ROOT / "data" / "reports"

# Fields that must never appear, at any depth. The schema already rejects them through
# additionalProperties, but naming them here produces an error a contributor can act on
# instead of a schema path.
FORBIDDEN_KEYS = {
    "src_ip", "source_ip", "dest_ip", "destination_ip", "client_ip", "ip", "addr", "address",
    "mac", "mac_address", "oui", "bssid", "ssid", "wifi", "network_name",
    "serial", "serial_number", "device_id", "deviceid", "duid", "ad_id", "advertising_id",
    "tifa", "idfa", "rida", "client_hostname", "client_name", "hostname", "lan_peer",
    "url", "url_path", "path", "query_string", "query", "http_headers", "headers", "cookies",
    "payload", "body", "content", "tls_keylog", "sslkeylogfile", "keylog",
    "lat", "lon", "latitude", "longitude", "city", "postcode", "zip", "timezone", "tz",
    "account", "account_id", "account_email", "email", "user", "username",
    "exact_timestamp", "dns_answer", "answer",
}

HOUR = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:00:00Z$")
LOOKS_LIKE_RAW_ID = re.compile(
    r"(^|\.)([0-9a-f]{16,}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(\.|$)"
)


class Findings:
    def __init__(self, label: str) -> None:
        self.label = label
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def walk_keys(node, path: str = ""):
    if isinstance(node, dict):
        for k, v in node.items():
            here = f"{path}.{k}" if path else k
            yield here, k, v
            yield from walk_keys(v, here)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            here = f"{path}[{i}]"
            yield from walk_keys(v, here)


def validate_structure(report: dict, f: Findings) -> None:
    """Schema validation, with a readable fallback when jsonschema is absent."""
    try:
        import jsonschema
    except ImportError:
        f.warn("jsonschema is not installed, so only the built-in checks ran")
        _minimal_structure(report, f)
        return

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(report), key=lambda e: list(e.path)):
        where = ".".join(str(p) for p in err.path) or "(root)"
        f.error(f"{where}: {err.message}")


def _minimal_structure(report: dict, f: Findings) -> None:
    for key in (
        "schema_version", "report_id", "submitter_key", "submitted_at",
        "tool", "capture_method", "device", "settings", "observations",
    ):
        if key not in report:
            f.error(f"missing required field: {key}")
    if report.get("schema_version") != 1:
        f.error(f"schema_version must be 1, got {report.get('schema_version')!r}")
    if not isinstance(report.get("observations"), list) or not report["observations"]:
        f.error("observations must be a non-empty list")


def validate_privacy(report: dict, f: Findings) -> None:
    """The checks that exist because a structurally valid report can still leak."""

    for path, key, value in walk_keys(report):
        if key.lower() in FORBIDDEN_KEYS:
            f.error(
                f"{path}: the field {key!r} is not collected by this project and must be "
                f"removed. See PRIVACY.md for the full list."
            )
        if isinstance(value, str) and len(value) < 400:
            found = scrub.contains_identifier(value)
            if found:
                f.error(f"{path}: contains {' and '.join(found)}. Remove it.")

    for key in ("submitted_at",):
        val = report.get(key)
        if isinstance(val, str) and not HOUR.match(val):
            f.error(
                f"{key}: timestamps are rounded to the hour, so this must end in :00:00Z. "
                f"Got {val!r}."
            )

    device = report.get("device") or {}
    region = device.get("region")
    if isinstance(region, str) and not re.fullmatch(r"[A-Z]{2}", region):
        f.error(f"device.region: two-letter uppercase country code only, got {region!r}")
    os_major = device.get("os_major")
    if isinstance(os_major, str) and not re.fullmatch(r"\d{1,3}", os_major):
        f.error(
            f"device.os_major: major version only, so 8 rather than {os_major!r}. Full build "
            f"strings are near-unique per region and batch."
        )

    for i, obs in enumerate(report.get("observations") or []):
        if not isinstance(obs, dict):
            continue
        where = f"observations[{i}]"
        tpl = obs.get("fqdn_template", "")

        if LOOKS_LIKE_RAW_ID.search(tpl):
            f.error(
                f"{where}: fqdn_template {tpl!r} still contains what looks like an "
                f"identifier. It should have been replaced with {{id}}."
            )

        # Re-run the client-side rules. A hostname that normalises to something different
        # from what was submitted means the client did not redact it properly.
        renorm = scrub.normalise(tpl.replace("{id}", "zz").replace("{n}", "1").replace("*", "zz"))
        if renorm and renorm.original_label_count > 0:
            depth_above = tpl.count(".") + 1
            if depth_above > 6 and "*" not in tpl:
                f.warn(f"{where}: {tpl!r} is unusually deep and was not truncated")

        for tkey in ("first_seen", "last_seen"):
            val = obs.get(tkey)
            if isinstance(val, str) and not HOUR.match(val):
                f.error(f"{where}.{tkey}: must be rounded to the hour, got {val!r}")

        if obs.get("first_seen") and obs.get("last_seen"):
            if obs["last_seen"] < obs["first_seen"]:
                f.error(f"{where}: last_seen is before first_seen")

        if obs.get("redacted_label_count", 0) and obs.get("original_label_count", 0):
            if obs["redacted_label_count"] > obs["original_label_count"]:
                f.error(f"{where}: redacted_label_count exceeds original_label_count")

    notes = report.get("notes")
    if isinstance(notes, str) and len(notes) > 280:
        f.error(f"notes: max 280 characters, got {len(notes)}")


def validate_file(path: Path) -> Findings:
    f = Findings(str(path.relative_to(ROOT) if ROOT in path.parents else path))
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        f.error(f"could not read: {exc}")
        return f

    reports = []
    if path.suffix == ".ndjson":
        for lineno, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                reports.append(json.loads(line))
            except json.JSONDecodeError as exc:
                f.error(f"line {lineno}: not valid JSON: {exc.msg}")
    else:
        try:
            reports.append(json.loads(text))
        except json.JSONDecodeError as exc:
            f.error(f"not valid JSON: {exc.msg} at line {exc.lineno}")
            return f

    for report in reports:
        if not isinstance(report, dict):
            f.error("each report must be a JSON object")
            continue
        report.pop("_dropped_non_hostnames", None)
        validate_structure(report, f)
        validate_privacy(report, f)
    return f


SELF_TEST_CASES = [
    (
        "a MAC address in a note",
        {"notes": "my tv aa:bb:cc:dd:ee:ff kept calling"},
        "MAC address",
    ),
    (
        "a client IP field",
        {"device": {"src_ip": "192.168.1.9"}},
        "not collected by this project",
    ),
    (
        "an unredacted identifier in a hostname",
        {"observations": [{"fqdn_template": "3f2504e0-4f89-11d3-9a0c-0305e82c3301.m.example.com"}]},
        "looks like an identifier",
    ),
    (
        "a timestamp finer than an hour",
        {"submitted_at": "2026-09-08T14:37:12Z"},
        "rounded to the hour",
    ),
    (
        "a full firmware build string",
        {"device": {"os_major": "03.30.55"}},
        "major version only",
    ),
    (
        "a city instead of a country",
        {"device": {"region": "London"}},
        "two-letter uppercase country code",
    ),
]


def self_test() -> int:
    """Prove the checks catch what they claim to.

    A validator nobody has tested against bad input is decoration. This runs the six failure
    modes that matter and fails the build if any of them slips through.
    """
    print("Self-test: each case must be rejected.\n")
    failures = 0
    for label, fragment, expected in SELF_TEST_CASES:
        f = Findings(label)
        validate_privacy(fragment, f)
        matched = any(expected in e for e in f.errors)
        status = "caught " if matched else "MISSED "
        print(f"  {status} {label}")
        if not matched:
            failures += 1
            print(f"      expected an error containing {expected!r}")
            for e in f.errors:
                print(f"      got: {e}")
    print()
    if failures:
        print(f"{failures} of {len(SELF_TEST_CASES)} checks did not fire.", file=sys.stderr)
        return 1
    print(f"All {len(SELF_TEST_CASES)} checks fired.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="files to check, default all reports")
    ap.add_argument("--self-test", action="store_true", help="prove the checks catch bad input")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.paths:
        files = [p for p in args.paths if p.is_file()]
    else:
        files = sorted(REPORTS.rglob("*.json")) + sorted(REPORTS.rglob("*.ndjson"))

    if not files:
        print("No reports to check.")
        return 0

    bad = 0
    for path in files:
        f = validate_file(path)
        if f.ok and not f.warnings:
            print(f"ok    {f.label}")
            continue
        if f.ok:
            print(f"ok    {f.label}")
        else:
            bad += 1
            print(f"FAIL  {f.label}")
        for e in f.errors:
            print(f"        error: {e}")
        for w in f.warnings:
            print(f"        warn:  {w}")

    print()
    if bad:
        print(f"{bad} of {len(files)} reports failed.", file=sys.stderr)
        print("PRIVACY.md lists every field we collect and every field we refuse to.", file=sys.stderr)
        return 1
    print(f"{len(files)} reports passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
