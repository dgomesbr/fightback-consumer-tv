"""Readers for the query logs you already have.

Each reader returns a list of Observation objects. None of them keep the client address
past the point of matching the device you asked about, and none of them return anything the
schema does not accept.

Two things every reader has to handle carefully:

  AdGuard Home's on-disk query log carries the client address on every record and a fully
  packed DNS answer in the `Answer` field, so the raw file is more sensitive than the web
  interface suggests.

  Pi-hole's records carry a `client` object with the hostname you chose for your own devices,
  which is household topology.

Both are read here and neither leaves this process.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class Observation:
    """One hostname seen, aggregated over the capture window."""

    hostname: str
    count: int = 1
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    blocked: bool | None = None
    l4proto: str = "udp"
    l7proto: str | None = "dns"
    dest_port: int | None = 53

    def merge(self, other: "Observation") -> None:
        self.count += other.count
        if other.first_seen and (not self.first_seen or other.first_seen < self.first_seen):
            self.first_seen = other.first_seen
        if other.last_seen and (not self.last_seen or other.last_seen > self.last_seen):
            self.last_seen = other.last_seen
        if other.blocked:
            self.blocked = True


@dataclass
class SourceResult:
    observations: list[Observation] = field(default_factory=list)
    clients_seen: list[str] = field(default_factory=list)
    window_hours: float | None = None
    notes: list[str] = field(default_factory=list)


class SourceError(Exception):
    """Something the contributor has to fix, phrased for a contributor."""


def _aggregate(rows: list[Observation]) -> list[Observation]:
    merged: dict[str, Observation] = {}
    for row in rows:
        existing = merged.get(row.hostname)
        if existing:
            existing.merge(row)
        else:
            merged[row.hostname] = row
    return sorted(merged.values(), key=lambda o: (-o.count, o.hostname))


def _http_json(url: str, headers: dict[str, str] | None = None, timeout: int = 20):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SourceError(f"{url} returned HTTP {exc.code}. Check the address and your token.") from exc
    except urllib.error.URLError as exc:
        raise SourceError(f"could not reach {url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise SourceError(f"{url} did not return JSON. Is that the right address?") from exc


# --------------------------------------------------------------------------- AdGuard Home


def read_adguard_file(path: Path, device: str, hours: int) -> SourceResult:
    """Read AdGuard Home's querylog.json, which is newline-delimited JSON.

    Field names come from internal/querylog/entry.go: T timestamp, QH query host, QT type,
    IP client address, Result the filtering outcome.
    """
    if not path.exists():
        raise SourceError(
            f"{path} does not exist. AdGuard Home usually writes it to "
            f"/opt/AdGuardHome/data/querylog.json, and the directory is set by "
            f"querylog.dir_path in AdGuardHome.yaml."
        )

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows: list[Observation] = []
    clients: set[str] = set()
    matched = 0
    skipped = 0

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                skipped += 1
                continue

            client = str(rec.get("IP") or "")
            if client:
                clients.add(client)
            if device and client != device:
                continue

            host = rec.get("QH")
            if not host:
                continue

            ts = _parse_ts(rec.get("T"))
            if ts and ts < cutoff:
                continue

            result = rec.get("Result") or {}
            reason = result.get("Reason")
            # Reason values 3 and above are the filtering outcomes in AdGuard Home.
            blocked = bool(reason) and int(reason) >= 3

            matched += 1
            rows.append(
                Observation(
                    hostname=host,
                    first_seen=ts,
                    last_seen=ts,
                    blocked=blocked,
                    l7proto="dns",
                )
            )

    notes = []
    if skipped:
        notes.append(f"skipped {skipped} unparseable lines")
    if not matched and device:
        notes.append(
            f"no queries from {device}. Clients in this log: "
            + (", ".join(sorted(clients)[:12]) or "none")
        )
    return SourceResult(
        observations=_aggregate(rows),
        clients_seen=sorted(clients),
        window_hours=float(hours),
        notes=notes,
    )


def read_adguard_api(base_url: str, device: str, hours: int, token: str | None) -> SourceResult:
    """Read AdGuard Home over its REST API, GET /control/querylog."""
    headers = {}
    if token:
        headers["Authorization"] = f"Basic {token}"

    url = base_url.rstrip("/") + "/control/querylog?limit=5000"
    if device:
        url += "&search=" + urllib.parse.quote(device)
    payload = _http_json(url, headers)

    rows: list[Observation] = []
    clients: set[str] = set()
    for rec in payload.get("data") or []:
        client = str(rec.get("client") or "")
        if client:
            clients.add(client)
        if device and client != device:
            continue
        host = rec.get("question", {}).get("name")
        if not host:
            continue
        ts = _parse_ts(rec.get("time"))
        blocked = str(rec.get("reason", "")).startswith("Filtered")
        rows.append(Observation(hostname=host, first_seen=ts, last_seen=ts, blocked=blocked))

    return SourceResult(
        observations=_aggregate(rows),
        clients_seen=sorted(clients),
        window_hours=float(hours),
    )


# --------------------------------------------------------------------------- Pi-hole


def read_pihole_api(base_url: str, device: str, hours: int, token: str | None) -> SourceResult:
    """Read Pi-hole v6 over GET /api/queries.

    Record fields per the OpenAPI spec: time as a float unix timestamp, domain, status,
    client as an object with ip and name. The client object is dropped here.
    """
    now = datetime.now(timezone.utc)
    params = {
        "from": str(int((now - timedelta(hours=hours)).timestamp())),
        "until": str(int(now.timestamp())),
        "length": "5000",
    }
    if device:
        params["client_ip"] = device
    url = base_url.rstrip("/") + "/api/queries?" + urllib.parse.urlencode(params)
    headers = {"accept": "application/json"}
    if token:
        headers["X-FTL-SID"] = token

    payload = _http_json(url, headers)
    rows: list[Observation] = []
    clients: set[str] = set()

    for rec in payload.get("queries") or []:
        client = (rec.get("client") or {}).get("ip") or ""
        if client:
            clients.add(str(client))
        if device and str(client) != device:
            continue
        host = rec.get("domain")
        if not host:
            continue
        ts = _parse_ts(rec.get("time"))
        status = str(rec.get("status") or "")
        blocked = status.startswith(("GRAVITY", "DENYLIST", "REGEX", "BLACKLIST", "SPECIAL"))
        rows.append(Observation(hostname=host, first_seen=ts, last_seen=ts, blocked=blocked))

    notes = []
    if not rows and device:
        notes.append(
            f"no queries from {device}. Clients Pi-hole has seen: "
            + (", ".join(sorted(clients)[:12]) or "none")
        )
    return SourceResult(
        observations=_aggregate(rows),
        clients_seen=sorted(clients),
        window_hours=float(hours),
        notes=notes,
    )


# --------------------------------------------------------------------------- NextDNS


def read_nextdns(profile: str, device: str, hours: int, api_key: str) -> SourceResult:
    """Read NextDNS logs.

    The API is community-documented rather than official, so treat endpoint stability as
    unconfirmed. If this stops working, that is why.
    """
    if not api_key:
        raise SourceError("NextDNS needs an API key. Find it under Account in the dashboard.")

    since = f"-{hours}h"
    url = f"https://api.nextdns.io/profiles/{urllib.parse.quote(profile)}/logs?from={since}&limit=1000"
    payload = _http_json(url, {"X-Api-Key": api_key})

    rows: list[Observation] = []
    devices: set[str] = set()
    for rec in payload.get("data") or []:
        dev = (rec.get("device") or {}).get("name") or ""
        if dev:
            devices.add(dev)
        if device and dev.lower() != device.lower():
            continue
        host = rec.get("domain")
        if not host:
            continue
        ts = _parse_ts(rec.get("timestamp"))
        rows.append(
            Observation(
                hostname=host,
                first_seen=ts,
                last_seen=ts,
                blocked=str(rec.get("status") or "") == "blocked",
                l7proto="doh" if rec.get("encrypted") else "dns",
            )
        )

    notes = []
    if not rows and device:
        notes.append(
            f"no queries from a device named {device}. Devices NextDNS knows: "
            + (", ".join(sorted(devices)[:12]) or "none")
        )
    return SourceResult(
        observations=_aggregate(rows),
        clients_seen=sorted(devices),
        window_hours=float(hours),
        notes=notes,
    )


# --------------------------------------------------------------------------- plain text


def read_domains_file(path: Path, hours: int) -> SourceResult:
    """Read a plain list of hostnames, optionally with a count after each.

    For anyone whose setup is not covered above, and for the test fixtures. One hostname per
    line, comments with #, an optional whitespace-separated count.
    """
    if not path.exists():
        raise SourceError(f"{path} does not exist")

    rows: list[Observation] = []
    now = datetime.now(timezone.utc)
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        host = parts[0]
        count = 1
        if len(parts) > 1 and parts[1].isdigit():
            count = int(parts[1])
        rows.append(
            Observation(
                hostname=host,
                count=count,
                first_seen=now - timedelta(hours=hours),
                last_seen=now,
            )
        )
    return SourceResult(observations=_aggregate(rows), window_hours=float(hours))


# --------------------------------------------------------------------------- helpers


def _parse_ts(value) -> datetime | None:
    """Parse the several timestamp shapes these tools use."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        # Milliseconds if it is implausibly large as seconds.
        seconds = value / 1000 if value > 1e11 else value
        try:
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str):
        text = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def summarise_by_registrable(observations: list[Observation]) -> dict[str, int]:
    """Group counts by registrable domain, for the preview summary."""
    from . import scrub

    out: dict[str, int] = defaultdict(int)
    for obs in observations:
        norm = scrub.normalise(obs.hostname)
        if norm:
            out[norm.registrable_domain] += obs.count
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))
