"""Hostname normalisation and redaction.

This is the privacy-critical module. Everything here runs before a report is shown to the
contributor, and the same rules run again server-side in CI. Keep it small and readable so
it can be reviewed independently.

The problem it solves: vendors put identifiers inside hostnames. A television that looks up
`3f2504e0-4f89-11d3-9a0c-0305e82c3301.metrics.example.com` has published a unique identifier
for its household in a DNS query. Stored verbatim, every row of a crowdsourced dataset
becomes a household identifier.

RFC 9076 is the normative reference for why this matters: query names disclose software and
identity, DNS query patterns alone re-identified users with 73.1% accuracy in the study it
cites, and a long query name is itself a covert channel.

The distinction that took some thought: a numeric suffix like `acr-eu-3` is server-shard
structure, not identity. The IMC 2024 authors inferred a vendor's regional server layout
from exactly that pattern. So digits at the end of an otherwise meaningful label become
`{n}`, while a high-entropy blob becomes `{id}`, and only the second is treated as a leak.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

# Multi-label public suffixes that appear in television telemetry, plus the common
# country-code second levels. This is a curated subset of the Public Suffix List rather than
# the whole thing, because vendoring 15,000 lines to resolve maybe 40 domains is not a good
# trade. Anything not listed falls back to the last label, which over-truncates rather than
# under-truncates, so the failure mode is losing a little detail rather than leaking.
#
# If you hit a domain this gets wrong, add it here and add a test.
MULTI_LABEL_SUFFIXES = frozenset(
    {
        "co.uk", "org.uk", "me.uk", "ac.uk", "gov.uk",
        "co.kr", "or.kr", "ne.kr", "go.kr", "re.kr", "pe.kr",
        "co.jp", "or.jp", "ne.jp", "ac.jp", "go.jp",
        "com.cn", "net.cn", "org.cn", "gov.cn", "edu.cn",
        "com.au", "net.au", "org.au", "edu.au", "gov.au",
        "com.br", "net.br", "org.br", "gov.br",
        "co.in", "net.in", "org.in", "gov.in",
        "com.mx", "com.ar", "com.tr", "com.tw", "com.hk", "com.sg", "com.my",
        "co.nz", "co.za", "co.il", "co.id", "co.th",
        "com.pl", "com.ua", "com.ru", "com.sa", "com.eg",
        "github.io", "cloudfront.net", "azureedge.net", "akamaihd.net",
        "akamaized.net", "edgesuite.net", "edgekey.net", "fastly.net",
        "amazonaws.com", "azurewebsites.net", "herokuapp.com",
    }
)

# A label that matches any of these is an identifier, not a name.
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
_HEX_BLOB = re.compile(r"^[0-9a-f]{16,}$")
_BASE32ish = re.compile(r"^[a-z2-7]{20,}$")
_BASE64URLish = re.compile(r"^[a-z0-9_-]{22,}$")

# A meaningful name with digits on the end is a shard, not an identifier.
# acr0, eu-acr3, ssm2, otnprd11, log-1 all match. The separator is captured so
# eu-acr3 becomes eu-acr{n} and log-1 becomes log-{n}.
_NUMERIC_SHARD = re.compile(r"^([a-z][a-z-]*[a-z])(-?)(\d{1,4})$")

MAX_LABEL_LEN = 20
MAX_DIGITS = 8

# Entropy is a backstop, not the primary rule: hex, base32 and base64 shapes are matched
# explicitly above. The threshold sits at 3.5 rather than 3.0 because real vendor hostnames
# are long and varied enough to clear 3.0. `device-metrics-us` and `tv-analytics-events` both
# do, and redacting those would throw away the data the project exists to collect.
#
# Labels containing a hyphen skip the check entirely. Vendors hyphenate meaningful names;
# generated identifiers almost never do, and the ones that do (UUIDs) are matched by shape.
MAX_ENTROPY_BITS_PER_CHAR = 3.5
MIN_LEN_FOR_ENTROPY = 8
SUBDOMAIN_DEPTH = 2

ID = "{id}"
SHARD = "{n}"


@dataclass(frozen=True)
class Normalised:
    """The result of normalising one hostname."""

    fqdn_template: str
    registrable_domain: str
    original_label_count: int
    redacted_label_count: int

    @property
    def leaked_identifier(self) -> bool:
        """True when a label looked like an identifier, so the row needs review."""
        return ID in self.fqdn_template


def shannon_entropy(s: str) -> float:
    """Bits per character. A random hex blob scores near 4, an English word near 3."""
    if not s:
        return 0.0
    counts: dict[str, int] = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def registrable_domain(labels: list[str]) -> tuple[str, int]:
    """Return the effective top-level domain plus one, and how many labels it spans."""
    if len(labels) < 2:
        return ".".join(labels), len(labels)
    for span in (3, 2):
        if len(labels) >= span:
            candidate = ".".join(labels[-span:])
            suffix = ".".join(labels[-(span - 1):])
            if suffix in MULTI_LABEL_SUFFIXES:
                return candidate, span
    return ".".join(labels[-2:]), 2


def classify_label(label: str) -> str:
    """Return the label, or a placeholder if it carries identity or shard structure."""
    if not label or label == "*":
        return label

    # Shard first: a numeric suffix on a meaningful stem is structure, not identity, and
    # checking it before the digit-count rule stops otnprd11 becoming {id}.
    shard = _NUMERIC_SHARD.match(label)
    if shard:
        stem, sep, digits = shard.groups()
        if len(stem) >= 2 and len(digits) <= 4:
            return f"{stem}{sep}{SHARD}"

    if _UUID.match(label):
        return ID
    if _HEX_BLOB.match(label):
        return ID
    if len(label) >= 20 and _BASE32ish.match(label):
        return ID
    if len(label) >= 22 and _BASE64URLish.match(label) and sum(c.isdigit() for c in label) >= 4:
        return ID
    if len(label) > MAX_LABEL_LEN:
        return ID
    if sum(c.isdigit() for c in label) >= MAX_DIGITS:
        return ID
    if (
        "-" not in label
        and len(label) >= MIN_LEN_FOR_ENTROPY
        and shannon_entropy(label) > MAX_ENTROPY_BITS_PER_CHAR
    ):
        return ID
    return label


def normalise(hostname: str) -> Normalised | None:
    """Normalise and redact one hostname. Returns None if it is not a usable name.

    Steps, in order:
      1. lowercase, strip the trailing dot and any port
      2. resolve the registrable domain
      3. keep at most two labels above it, collapse the rest to a single `*`
      4. replace identifier-shaped labels with {id} and shard suffixes with {n}
    """
    host = (hostname or "").strip().lower().rstrip(".")
    if not host:
        return None
    host = host.split(":", 1)[0]
    if "/" in host or " " in host:
        return None

    # An address is not a hostname, and we do not collect addresses.
    if re.fullmatch(r"[0-9.]+", host) or ":" in host:
        return None
    # Local and reverse-lookup names are household topology, not vendor endpoints.
    if host.endswith((".local", ".arpa", ".lan", ".home", ".internal", ".localdomain")):
        return None

    labels = [lab for lab in host.split(".") if lab]
    if len(labels) < 2:
        return None

    original_label_count = len(labels)
    reg, reg_span = registrable_domain(labels)
    prefix = labels[: len(labels) - reg_span]

    truncated = False
    if len(prefix) > SUBDOMAIN_DEPTH:
        prefix = prefix[-SUBDOMAIN_DEPTH:]
        truncated = True

    cleaned = [classify_label(lab) for lab in prefix]
    redacted = sum(1 for a, b in zip(prefix, cleaned) if a != b and b == ID)
    if truncated:
        redacted += original_label_count - reg_span - SUBDOMAIN_DEPTH
        cleaned = ["*"] + cleaned

    template = ".".join(cleaned + [reg]) if cleaned else reg
    return Normalised(
        fqdn_template=template,
        registrable_domain=reg,
        original_label_count=original_label_count,
        redacted_label_count=redacted,
    )


# --------------------------------------------------------------------------- text scrubbing

_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_IPV6 = re.compile(r"\b(?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{0,4}\b", re.I)
_MAC = re.compile(r"\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b", re.I)
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_URL = re.compile(r"\bhttps?://\S+", re.I)


def scrub_text(text: str, limit: int = 280) -> str:
    """Remove addresses and identifiers from free text.

    Free text is a leak vector. A contributor writing a helpful note is exactly the person
    likely to paste an address into it without thinking.
    """
    if not text:
        return ""
    out = _URL.sub("[url removed]", text)
    out = _EMAIL.sub("[email removed]", out)
    out = _MAC.sub("[mac removed]", out)
    out = _IPV4.sub("[ip removed]", out)
    out = _IPV6.sub("[ip removed]", out)
    return out.strip()[:limit]


def contains_identifier(text: str) -> list[str]:
    """Return the kinds of identifier found in a string. Used by CI to reject a report."""
    found = []
    if _IPV4.search(text):
        found.append("IPv4 address")
    if _MAC.search(text):
        found.append("MAC address")
    if _EMAIL.search(text):
        found.append("email address")
    return found
