# Privacy

This project asks people to send us data about their televisions. That obliges us to be precise about
what we take, what we refuse to take, and what we publish.

The technical annex to this document is [`data/schema/report.schema.json`](data/schema/report.schema.json),
versioned in git. If this page and the schema ever disagree, the schema is what the software enforces
and this page is the bug.

## Defaults

**Local-only is the default.** The collector reads your query log, builds a report, and writes it to
your disk. Nothing is transmitted. Submission is a separate, explicit command.

**You see the file first.** Running with `--preview` prints the exact bytes that would be uploaded,
with redactions highlighted. There is no code path that sends a report you have not been shown.

**Application inventory is off, permanently.** The list of apps installed on a device is a strong
behavioural fingerprint. It defaults to null and requires a second, separate opt-in.

## What a report contains

| Field | Example | Why we need it |
| --- | --- | --- |
| `schema_version` | `1` | So old reports stay readable |
| `submitter_key` | salted hash | To count distinct contributors. The salt never leaves your device |
| `submitted_at` | `2026-09-08T14:00:00Z` | Rounded to the hour |
| `device.vendor` | `lg` | The unit of analysis |
| `device.model_family` | `LG OLED C3` | Normalised. Not your full regional SKU |
| `device.platform` | `webos` | |
| `device.os_major` | `8` | Major version only. Behaviour changes across firmware |
| `device.region` | `GB` | Country only. Content recognition differs by jurisdiction |
| `device.locale` | `en` | Language affects which endpoints are contacted |
| `settings.acr_state` | `optout` | The central question: does opting out work? |
| `observations[].fqdn_template` | `*.acr-{n}.example.tv` | The evidence, with identifiers removed |
| `observations[].registrable_domain` | `example.tv` | |
| `observations[].dest_port` | `443` | |
| `observations[].first_seen` / `last_seen` | hour precision | |
| `observations[].count` | `1420` | |
| `observations[].blocked` | `true` | |
| `observations[].scenario` | `idle` | Idle, linear, FAST, streaming, HDMI or screencast |

## What we never collect

These fields **do not exist in the schema**, so a report cannot carry them even by accident:

Your IP address. The TV's IP address. The endpoint's IP address. MAC addresses. Hardware serial
numbers. Device identifiers. Advertising identifiers. Wi-Fi network names. The hostnames of other
devices on your network. URL paths. Query strings. HTTP headers. Any payload content. TLS key logs.
Coordinates, city, postcode or timezone. Account names, emails or hashes of them. Timestamps finer
than one hour.

Two consequences worth spelling out:

**We do not accept raw log files.** AdGuard Home's query log carries a client IP address on every
record and a fully packed DNS answer. Pi-hole's carries a client object with the hostname you chose
for your own devices. Uploading either would leak your network layout. The collector reads them
locally and emits a report; the log itself stays on your machine.

**We do not accept packet captures.** Same reason, more so.

## Hostnames get rewritten before they leave your machine

Vendors put identifiers inside hostnames. A device that looks up
`3f2504e0-4f89-11d3-9a0c-0305e82c3301.metrics.example.com` has just published a unique identifier for
your household in a DNS query. If we stored that verbatim, every row in our dataset would be a
household identifier.

So every hostname is rewritten:

1. Lowercased, trailing dot stripped, internationalised names normalised.
2. The registrable domain is resolved through the [Public Suffix List](https://publicsuffix.org/).
3. Anything more than two labels above it is collapsed to `*`.
4. Any remaining label is replaced with `{id}` if it looks like a UUID, is a long hex or base32 run,
   runs past 20 characters, carries eight or more digits, or exceeds 3.0 bits of entropy per character.
5. Numeric shard suffixes become `{n}` instead of `{id}`, because `acr-eu-3` tells us about a vendor's
   regional server layout and nothing about you.

The example above becomes `{id}.metrics.example.com`. We keep a count of how many labels were
redacted, so an analyst knows depth was lost.

This runs on your machine before the preview, and again on ours. If a report arrives with a raw
high-entropy label, CI rejects it.

## What we publish, and when

A row becomes public only when all of these hold:

- At least **5 distinct contributors** reported it.
- **And** either at least 2 countries or at least 2 firmware major versions are represented. This
  stops one enthusiast with five televisions from publishing on their own.
- **And** either nothing was redacted from the hostname, or a human reviewed it.

Below that threshold a row stays quarantined and we expose only the number of quarantined rows. This
is a stricter bar than the closest precedent: [IoT Inspector](https://arxiv.org/abs/1909.09848)
published a crowdsourced dataset of 44,956 devices with no stated k-anonymity threshold at all.

Published artifacts:

| What | Licence |
| --- | --- |
| Derived blocklists | CC0 1.0 |
| Per-model reports | CC BY 4.0 |
| Scrubbed corpus, as NDJSON and Parquet | ODbL 1.0 plus DBCL 1.0 |

## Legal basis and the word "anonymous"

We do not claim reports are anonymous. GDPR Recital 26 is explicit that pseudonymised data which
could be attributed to a person using additional information is still personal data. What we claim:

- **The submission pipeline is pseudonymised with aggressive minimisation.** Consent is the legal
  basis. It is freely given, it is withdrawable, and local-only mode is a genuine alternative rather
  than a token one.
- **The published aggregate is anonymous** because of the redaction rules and the five-contributor
  threshold, and the reasoning for that is on this page rather than asserted.

Deletion works without us holding an identifier. Your submitter key is derived from a salt that only
you have, so you can prove which rows are yours; we cannot. Open an issue with the key and we remove
them.

## Residual risk, stated plainly

A vendor may embed an identifier in a hostname in a shape our redaction does not yet recognise. If
you spot one in the published dataset, [open an
issue](../../issues/new?template=bug_report.yml) and we will remove the rows and fix the rule.

[OONI](https://ooni.org/about/data-policy/) makes a similar admission about unintentional capture and
is the model for this section. Unlike OONI, we commit to a removal procedure, which is the paragraph
above.

## The household problem

This tooling watches network traffic. On a shared network, that can mean watching people.

We have narrowed the blast radius as far as the design allows: one device at a time, metadata only,
no payloads, hour-resolution timestamps, and no capture of other devices' hostnames. That reduces the
risk, it does not remove it. The authors of IoT Inspector were candid that their equivalent
protections only "increase the barrier".

So: run this on equipment you are responsible for, on a network you are responsible for, and tell the
people who share the household.

## Anti-abuse, without collecting identity

A motivated party could try to poison the dataset. Our defences do not require knowing who anyone is:

1. **Schema validation.** An attacker trying to inject an identifier hits the same redaction filter
   that protects honest contributors.
2. **The five-contributor threshold.** This is the main defence and it costs nothing. Promoting a
   fabricated row needs a real sybil effort across multiple countries or firmware versions.
3. **Outlier detection.** Reports whose hostname set barely overlaps its cohort get quarantined, not
   dropped.
4. **Review queue** for anything new: new vendor, new model, new registrable domain, heavy redaction.
5. **Provenance labelling.** Reports signed by a key from a reproducible release build are marked
   `verified`. This is not a security boundary, since the key is extractable from any build. It is a
   cost boundary and a label, and we would rather say that than overstate it.

## Questions

Open an issue. If it concerns your own data, say so and we will treat it as such.
