---
title: Pi-hole v6
updated: 2026-09-08
---

# Pi-hole v6

Pi-hole has the largest community and the most tutorials of any resolver in this space, which is the
main reason to choose it. When you get stuck at 11pm, somebody has already written up your exact
problem. Version 6 added a documented API, so it can now do the same export job as
[AdGuard Home](adguard-home.md).

If you are choosing between the two and have no preference, we suggest AdGuard Home, because its
built-in DHCP server helps readers whose router will not expose DHCP option 6. If you already run
Pi-hole, there is no reason to migrate.

## Who it suits

- You want the most-documented option, because you would rather search than debug.
- You want per-client policy and are happy to organise it with groups.
- You want to [contribute a device report](../../CONTRIBUTING.md). The collector reads Pi-hole logs and
  the documented example in CONTRIBUTING uses this resolver.

If you need the resolver to hand out DHCP leases as well, our research notes record that capability for
AdGuard Home and do not record it either way for Pi-hole. Check Pi-hole's own documentation rather than
taking this page's word for it.

## What it costs

| Cost | Detail |
| --- | --- |
| A machine that stays up | Once devices point at it, it is the household's DNS. If it dies, the internet looks broken to everyone in the house |
| Your own maintenance | Updates, backups, list tuning. No support line |
| Disk and a performance hit for logging | Query logging is what makes any of this observable, and it is not free |

**Undoing all of it:** point DHCP option 6 back at the router and stop the service. Devices recover on
the next lease renewal. Nothing on any television changes.

## How to point devices at it

Three routes, weakest first:

1. **DHCP option 6 on your router**, advertising Pi-hole's address. Advisory, and roughly two-thirds of
   televisions ignore it ([Mazhar and Shafiq, IoTDI 2020][iotdi] §IV-C). Do it because it is five
   minutes. See [OpenWrt](../routers/openwrt.md),
   [pfSense and OPNsense](../routers/pfsense-opnsense.md).
2. **A port 53 redirect**, which is what makes option 6 binding and what catches a Chromecast hardcoded
   to `8.8.8.8`. See [Router enforcement §2](../router-enforcement.md#2-redirect-outbound-port-53-to-your-resolver).
3. **The device's own DNS field**, if it has one. Nothing to point at on a Roku.

Behind a carrier gateway that offers none of the above, read
[ISP and carrier gateways](../routers/isp-gateway.md) before buying hardware.

## Per-client policy with groups

Pi-hole does per-client policy through groups: assign a client to a group, assign lists to the group.
So the television gets the aggressive per-vendor lists and the work laptop does not.

**One warning about the topology.** If your router uses outbound NAT to reach Pi-hole, every query
arrives from the router's address and per-client grouping stops working, because there is only one
client. That is [rule 3 on the pfSense
page](../routers/pfsense-opnsense.md#rule-3-outbound-nat-and-the-reason-to-avoid-needing-it), and it is
the reason to prefer a topology that does not need it.

### Which lists to load

Follow HaGeZi's own tiering. Light and Normal carry only native trackers that do not break things,
Ultimate blocks all of them and does break things, and the recommendation is Pro plus the device lists
for hardware you actually own:

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.{lgwebos|samsung|roku|amazon|apple|xiaomi|huawei|oppo-realme|vivo|tiktok|winoffice}-onlydomains.txt
```

`native.lgwebos` is 341 entries, `native.amazon` 369, `native.samsung` 199, `native.apple` 108,
`native.roku` 72. HaGeZi publishes no native list for Google or Android TV, Vizio or Hisense.

The Pi-hole ecosystem has three other lists worth naming, and the differences between them matter:

| List | Licence | State | Use it? |
| --- | --- | --- | --- |
| [Perflyst PiHoleBlocklist][perflyst] | MIT | **Stale since 13 July 2023** | Read it, do not rely on it. It is the only list carrying per-domain breakage annotations, and that commentary is the most useful artifact in this space. Firebog's smart TV recommendations are this list, so a lot of advice you will find elsewhere is three years old |
| [oisd][oisd] | Not stated | Updated about hourly | Yes, as a safe baseline. It explicitly prioritises functionality over blocking, so it is weaker exactly where device-native telemetry lives |
| [blocklistproject smart-tv][blp] | MIT | Updated 2026-07-06 | Carefully. 77 entries, unannotated, and it blocks `cloudservices.roku.com` with no note about what that breaks |
| [StevenBlack hosts][sb] | MIT | Active | It has no smart TV coverage. It is a fine general list and not a substitute for one |

For the vendors HaGeZi does not cover, use this project's generated lists in
[`blocklists/`](../../blocklists/). Every entry carries a flag for what it breaks, which is the field
that stops a blocklist from doing more harm than good.

**Return NXDOMAIN, not SERVFAIL, for blocked names.** Some television firmware reads SERVFAIL as no
internet and retries aggressively.

**Read the do-not-block tables on the vendor pages.** Blocking `ngfts.lge.com` breaks LG Content Store
thumbnails. Blocking `time.samsungcloudsolution.com` breaks Plex, YouTube and Prime Video on a Samsung.
Blocking `mas-ext.amazon.com` breaks Fire TV app installs. These are the entries that make people give
up on filtering entirely.

## What the query log contains

`GET /api/queries` on the v6 API returns, per query:

| Field | What it is |
| --- | --- |
| `id` | Record identifier |
| `time` | Timestamp |
| `type` | Query type |
| `domain` | Queried name |
| `cname` | CNAME target, where relevant |
| `status` | Allowed, blocked, cached, forwarded |
| `client` | **An object with `ip` and `name`** |
| `dnssec` | Validation state |
| `reply` | An object with `type` and `time_ms` |
| `list_id` | Which list matched |
| `upstream` | Which upstream answered |
| `ede` | Extended DNS error |

### Never upload this

`client` is an object containing `ip` and `name`, and `name` is **the hostname you chose for your own
device**. People name their machines after themselves, their children, their employer and their
bedroom. A raw Pi-hole log is therefore a labelled inventory of your household plus a second-resolution
record of what each labelled device looked up.

Our schema refuses it. `src_ip`, `client_hostname`, `client_name` and `dns_answer` do not exist as
fields in [`data/schema/report.schema.json`](../../data/schema/report.schema.json), and
`additionalProperties` is false at every object level, so a report carrying one fails validation rather
than slipping through. See [PRIVACY.md](../../PRIVACY.md).

**So the collector reads the log locally.** It parses it on your machine, keeps the hostnames the
television looked up, discards everything about your own devices, and writes a report to your disk.
Nothing leaves until you run a second command.

## Exporting for a report

This reads your Pi-hole query log, builds a report for one device, and prints the exact file it would
upload without uploading it. It writes only to your own disk, so there is nothing to undo.

```bash
python collector/router/fightback.py --source pihole --device "LG OLED C3" --preview
```

Read the output. Add `--submit` when you are happy with it, and the tool opens a pull request.

**Start logging before the television boots.** The IMC 2024 team found most DNS requests fire in the
first seconds after activation, so a late start loses the hostname-to-address mapping for the session
and your report understates what the set does.

Record `settings.acr_state` accurately. Reports from sets with content recognition still switched on are
as valuable as reports from sets that opted out, because the open question is whether opting out
survives firmware updates. A report with that field wrong is worse than no report at all.

If you would rather not use a terminal, the device report form takes the same information by hand.
[CONTRIBUTING.md](../../CONTRIBUTING.md) links it.

## Alternatives worth knowing about

| Tool | Why you might pick it instead |
| --- | --- |
| [AdGuard Home](adguard-home.md) | Per-client upstreams and a built-in DHCP server, so you can own option 6 without the router |
| [NextDNS](nextdns.md) | No hardware, at the cost of a free tier that stops filtering past its cap |
| Blocky | Exports to CSV, Postgres, MariaDB or Timescale, with Prometheus and Grafana. Shortest path if you want to datamine your own logs |
| Technitium | Also a DoH, DoT and DoQ **server**, so you can hand a television a private encrypted endpoint rather than blocking encrypted DNS |

[iotdi]: https://arxiv.org/abs/2001.08288
[perflyst]: https://github.com/Perflyst/PiHoleBlocklist
[oisd]: https://oisd.nl/
[blp]: https://github.com/blocklistproject/Lists/blob/master/smart-tv.txt
[sb]: https://github.com/StevenBlack/hosts
