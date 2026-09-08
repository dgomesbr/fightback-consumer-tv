---
title: AdGuard Home
updated: 2026-09-08
---

# AdGuard Home

**This is our general recommendation.** It does per-client policy with tags and per-client upstreams,
it has a REST API, and it ships its own DHCP server, which means you can own DHCP option 6 without
touching the router at all. That last point is why it is the right answer for the largest group of
readers, the ones stuck behind a carrier gateway.

One naming thing to clear up. AdGuard Home is software you run on your own machine. AdGuard DNS is a
hosted public resolver at `94.140.14.14` and `94.140.15.15`. This page is about the first one. The
second has no per-device policy and no query log you control, so it does not help you measure anything.

## Who it suits

You, if any of these are true:

- You have a spare machine, a Raspberry Pi, a NAS or a router with enough flash for the `adguardhome`
  package.
- Your router will not let you set DHCP option 6, and you want to run the DHCP server yourself.
- You want a different blocklist for the television than for the work laptop.
- You want to [contribute a device report](../../CONTRIBUTING.md), which needs per-client attribution
  in the log.

## What it costs

| Cost | Detail |
| --- | --- |
| A machine that stays up | Once devices point at it, it is the household's DNS. If it goes down, the internet looks broken to everyone |
| Your own maintenance | Updates, backups and blocklist tuning are yours. There is no support line |
| Disk for the query log | Retention runs from 1 hour to 1 year, file-based. A busy household on long retention is not small |
| A performance cost when logging | Logging is what makes this observable, and it is not free. Log for a measurement window rather than forever unless you have headroom |

**Undoing all of it:** point DHCP option 6 back at the router, or turn AdGuard Home's DHCP server off
and the router's back on, then stop the service. Devices recover on their next lease renewal. Nothing
on any television needs changing.

## How to point devices at it

Three routes, in order of how much they enforce:

1. **DHCP option 6 on your router**, advertising AdGuard Home's address. Advisory. Roughly two-thirds
   of televisions ignore it ([Mazhar and Shafiq, IoTDI 2020][iotdi] §IV-C). Start here anyway because
   it takes five minutes. See [OpenWrt](../routers/openwrt.md),
   [pfSense and OPNsense](../routers/pfsense-opnsense.md).
2. **A port 53 redirect on your router**, which makes option 6 binding. This is the step that catches a
   Chromecast hardcoded to `8.8.8.8`. See [Router enforcement §2](../router-enforcement.md#2-redirect-outbound-port-53-to-your-resolver).
3. **The device's own DNS field**, where it has one. Fine for a single set, useless for a Roku.

### Own DHCP option 6 without touching the router

AdGuard Home includes a DHCP server. Turn it on, turn the router's off, and AdGuard Home hands out
leases that advertise itself. No router configuration, no vendor admin page, no fighting a carrier
gateway's firmware.

**What breaks:** everything, briefly, if you get the handover wrong. Two DHCP servers answering on one
network segment race each other, and the symptoms are intermittent and depend on which replies first.
Turn the router's server off before or in the same minute as turning AdGuard Home's on, and reboot one
device to confirm it gets a lease from the right place before you walk away.

**What it does not fix:** option 6 is still advisory. A television that ignores the lease ignores
yours exactly as it ignored the router's. Without a port 53 redirect you have moved the DHCP server,
not enforced anything. Some carrier gateways also refuse to disable their DHCP server at all, in which
case put AdGuard Home on your own network segment behind your own router
([Branch C](../routers/isp-gateway.md#branch-c-double-nat)).

**To undo:** turn AdGuard Home's DHCP server off, turn the router's back on.

## Per-client policy

AdGuard Home supports per-client configuration with tags, and per-client upstreams. Two things follow
that matter here.

**A harsher list for the television.** Follow HaGeZi's own tiering guidance rather than turning
everything on. The Light and Normal tiers deliberately carry only native trackers that do not break
things. Ultimate blocks all of them and does break things. Pro plus the specific device lists for
hardware your household owns is the recommendation:

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.{lgwebos|samsung|roku|amazon|apple|xiaomi|huawei|oppo-realme|vivo|tiktok|winoffice}-onlydomains.txt
```

Sizes, so you know what you are adding: `native.lgwebos` 341 entries, `native.amazon` 369,
`native.samsung` 199, `native.apple` 108, `native.roku` 72. There is no HaGeZi native list for Google
or Android TV, Vizio or Hisense, so use this project's lists in [`blocklists/`](../../blocklists/) for
those. Every entry there carries a flag for what it breaks.

**A per-client blocklist is also a per-client breakage.** Blocking `ngfts.lge.com` breaks Content Store
thumbnails. Blocking `time.samsungcloudsolution.com` breaks Plex, YouTube and Prime Video. Blocking
`mas-ext.amazon.com` breaks app installs. The do-not-block tables are on the vendor pages and they are
not optional reading.

**Return NXDOMAIN, not SERVFAIL, for blocked names.** Some television firmware treats SERVFAIL as no
internet and retries aggressively, which turns a working block into a support call from your household.

## What the query log contains

The query log is JSONL, one object per query. The fields:

| Field | What it is |
| --- | --- |
| `T` | Timestamp |
| `QH` | Query hostname |
| `QT` | Query type |
| `QC` | Query class |
| `ECS` | EDNS client subnet |
| `CID` | Client identifier |
| `CP` | Client protocol |
| `Upstream` | Which upstream answered |
| `Answer` | **The full DNS answer, packed** |
| `IP` | **The client's address, on every single record** |
| `Result` | Filtering result |
| `Elapsed` | Response time |
| `Cached` | Whether it came from cache |

### Never upload this file

Two fields make the raw query log a description of your home network.

`IP` carries the client address on every record, so the file is an inventory of which device on your
LAN asked for what, at what time. `Answer` is a fully packed DNS message, so it also carries the
resolved addresses.

Uploading it anywhere, to us or to a forum thread or into a chat window while asking for help, leaks
your LAN topology and your viewing behaviour at second resolution. That is the same category of data
the FTC fined Vizio $2.2M for collecting.

Our schema cannot accept it. `src_ip`, `dest_ip`, `client_hostname` and `dns_answer` do not exist as
fields in [`data/schema/report.schema.json`](../../data/schema/report.schema.json), and
`additionalProperties` is false at every level, so a report carrying any of them fails validation
rather than being quietly accepted. See [PRIVACY.md](../../PRIVACY.md).

**So the collector reads the log locally.** It parses the file on your machine, builds a report from
what is publishable, and writes it to your disk. Nothing is transmitted until you run a separate
command, and `--preview` prints the exact bytes first.

## Exporting for a report

The log lives as a JSONL file in AdGuard Home's working directory, and there is a REST API for reading
it. Our notes do not record the exact filename or the endpoint path, so do not guess at either. Point
the collector at your installation instead:

This reads your AdGuard Home query log, builds a report for one device, and prints the file it would
send without sending it. It writes nothing outside your machine, so there is nothing to undo.

```bash
python collector/router/fightback.py --source adguardhome --device "LG OLED C3" --preview
```

Add `--submit` when you are happy with what you read, and it opens a pull request. The `--source`
values match the schema's `resolver_kind` enum, so this one is `adguardhome`.

**Start the capture before the television boots.** The IMC 2024 team found most DNS requests fire in the
first seconds after activation, so a late start loses the hostname-to-address mapping for that session
and your report will understate what the set does.

Set `settings.acr_state` honestly. A report from a set with content recognition still switched on is as
useful as one from a set that has opted out, because the open question is whether opting out keeps
working across firmware updates. Reports with the setting recorded wrongly are worse than no report.

If you would rather not use a terminal, the device report form takes the same information by hand.
[CONTRIBUTING.md](../../CONTRIBUTING.md) links it.

## Alternatives worth knowing about

| Tool | Why you might pick it instead |
| --- | --- |
| [Pi-hole v6](pi-hole.md) | Largest community, most tutorials, so more help available when you are stuck |
| [NextDNS](nextdns.md) | No hardware at all, at the cost of a free tier that fails open |
| Blocky | Writes to CSV, Postgres, MariaDB or Timescale, with Prometheus and Grafana. The shortest path if you want to datamine your own logs. Collects no telemetry itself |
| Technitium | Also a DoH, DoT and DoQ **server**, so you can hand a television a private encrypted endpoint instead of blocking encrypted DNS |

[iotdi]: https://arxiv.org/abs/2001.08288
