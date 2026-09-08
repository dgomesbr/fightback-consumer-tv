# Endpoint data format

One file per vendor. These files are the input to the blocklist generator. Do not edit anything
under `blocklists/`, it is overwritten on every build.

```yaml
vendor: lg              # matches the vendor enum in ../schema/report.schema.json
platform: webos
updated: 2026-09-08

entries:
  - domain: acr-eu-prd.samsungcloud.tv   # required, lowercase, no trailing dot
    wildcard: false                      # optional, default false. true also blocks subdomains
    regex: '^acr-[a-z]{2}-prd\...'       # optional. Use when a wildcard would be too broad
    purpose: acr                         # required
    tier: core                           # required
    safe_to_block: true                  # required
    breaks: null                         # required. null, a sentence, or the word unknown
    source: https://...                  # required
    verified: 2026-09-08                 # optional, when someone confirmed it on hardware
    notes: >-                            # optional
      Anything a future maintainer would otherwise have to rediscover.
    vendor: philips                      # optional, only in other.yml where one file holds several
```

## `purpose`

| Value | Meaning |
| --- | --- |
| `acr` | Automatic content recognition, the fingerprinting of what is on screen |
| `ads` | Ad serving, ad measurement, ad identifiers |
| `telemetry` | Usage, diagnostics, crash reporting, home-screen personalisation |
| `ota` | Firmware and software updates |
| `functional` | Something the device needs to work: login, licensing, app store, connectivity checks |
| `cdn` | Content delivery for images and assets |
| `ntp` | Time synchronisation |

## `tier`

| Value | Meaning |
| --- | --- |
| `core` | Safe to block. No documented breakage. Goes in the default list we recommend. |
| `aggressive` | Blocks something a reader might want. Always paired with a real `breaks` value. |
| `never` | Breaks core function. CI asserts these never appear in any generated list. |

Entries with `safe_to_block: unknown` belong in `aggressive`, never in `core`. When in doubt,
`aggressive` is the right answer, because a list that breaks a television does more harm than the
tracking it prevents.

## `breaks`

The field this project exists to get right. Three valid shapes:

- `null` means no documented breakage. Only use this when a source says so or you tested it.
- A sentence describing what stops working, in the reader's terms. "Thumbnails stop loading in the
  LG Content Store" rather than "affects CDN functionality".
- `unknown` means nobody has checked. Honest, and it keeps the entry out of the core tier.

## Guard entries

Some `never` entries exist purely to stop a mistake, not because anyone was going to block them by
accident. `roku.com`, `googleapis.com`, `amazonaws.com`, `gracenote.com` and `nielsen.com` are in
that category. Each has shipped in a real community blocklist and broken something. The generator
asserts they are absent from output, so the guard is enforced rather than advisory.

## Why regex instead of wildcard

A wildcard on a registrable domain is usually wrong when the vendor mixes telemetry and function
under one name. Samsung puts content recognition at `acr-eu-prd.samsungcloud.tv` and other services
elsewhere under `samsungcloud.tv`. Amazon puts clickstream collection at `fls-na.amazon.com`. In both
cases a regex scoped to the pattern blocks the telemetry and leaves the rest alone.

## Adding an entry

1. Find a source. A vendor document, a paper, an upstream blocklist, or your own capture. Your own
   capture is fine if you name the model and firmware.
2. Work out what it breaks. If you cannot, write `unknown` and put it in `aggressive`.
3. Run `python tools/build_blocklists.py` and check the diff is what you expected.
4. Open a pull request with the source in the evidence table.
