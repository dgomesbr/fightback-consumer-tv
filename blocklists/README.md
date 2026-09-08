# Blocklists

Generated from [`data/endpoints/`](../data/endpoints/) by
[`tools/build_blocklists.py`](../tools/build_blocklists.py). Do not edit these files, they are
overwritten on every build. To change an entry, edit the source data.

Licensed CC0 1.0. Use them anywhere, including in another blocklist, without attribution.

## Which list

| List | Entries | What it does |
| --- | --- | --- |
| **core** | 119 | Safe defaults. No documented breakage. Start here. |
| **aggressive** | 136 | Core plus entries that break something you might want. Read the notes first. |
| **do-not-block** | 73 | An allowlist. Domains that break a television. |

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
| `amazon` | 21 | [AdGuard](adguard/fightback-tv-amazon.txt), [hosts](hosts/fightback-tv-amazon.txt) |
| `apple` | 11 | [AdGuard](adguard/fightback-tv-apple.txt), [hosts](hosts/fightback-tv-apple.txt) |
| `google` | 7 | [AdGuard](adguard/fightback-tv-google.txt), [hosts](hosts/fightback-tv-google.txt) |
| `hisense` | 1 | [AdGuard](adguard/fightback-tv-hisense.txt), [hosts](hosts/fightback-tv-hisense.txt) |
| `lg` | 25 | [AdGuard](adguard/fightback-tv-lg.txt), [hosts](hosts/fightback-tv-lg.txt) |
| `multiple` | 1 | [AdGuard](adguard/fightback-tv-multiple.txt), [hosts](hosts/fightback-tv-multiple.txt) |
| `panasonic` | 3 | [AdGuard](adguard/fightback-tv-panasonic.txt), [hosts](hosts/fightback-tv-panasonic.txt) |
| `philips` | 3 | [AdGuard](adguard/fightback-tv-philips.txt), [hosts](hosts/fightback-tv-philips.txt) |
| `roku` | 17 | [AdGuard](adguard/fightback-tv-roku.txt), [hosts](hosts/fightback-tv-roku.txt) |
| `samsung` | 28 | [AdGuard](adguard/fightback-tv-samsung.txt), [hosts](hosts/fightback-tv-samsung.txt) |
| `sony` | 9 | [AdGuard](adguard/fightback-tv-sony.txt), [hosts](hosts/fightback-tv-sony.txt) |
| `toshiba` | 1 | [AdGuard](adguard/fightback-tv-toshiba.txt), [hosts](hosts/fightback-tv-toshiba.txt) |
| `vizio` | 5 | [AdGuard](adguard/fightback-tv-vizio.txt), [hosts](hosts/fightback-tv-vizio.txt) |
| `xiaomi` | 4 | [AdGuard](adguard/fightback-tv-xiaomi.txt), [hosts](hosts/fightback-tv-xiaomi.txt) |

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
