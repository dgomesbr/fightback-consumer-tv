# Choose a resolver

**Four questions decide this: do you want to run hardware, do you mind making an account, do you want
per-device rules, and do you want the query data afterwards.**

Work out which of the four profiles below is you, take the recommendation, and skip the rest of the
page. The comparison tables are there for when you want to check the reasoning.

| Profile | Recommendation | Jump |
| --- | --- | --- |
| No new hardware, no account | AdGuard public DNS in your router's DHCP | [below](#no-new-hardware-and-no-account) |
| No new hardware, an account is fine | NextDNS, with the free-cap warning read | [below](#no-new-hardware-but-an-account-is-fine) |
| Willing to run one small box | AdGuard Home | [below](#willing-to-run-one-small-box) |
| You want the data, not just the block | Blocky into Postgres or Timescale | [below](#you-want-the-data) |

## No new hardware and no account

Set your router's DHCP to advertise `94.140.14.14` and `94.140.15.15`, AdGuard's public filtered
resolvers. Nothing to install, nothing to keep running, no login.

What you give up: no per-device policy, no query log, and no way to tell whether the television is
using it. Every device that ignores the DNS server your router hands out ignores this too, which by
measurement is most televisions. Read [why-dns](why-dns.md) for what that means.

This is still the right first move for most households, because it costs nothing and it covers the
phones and laptops, which honour DHCP.

## No new hardware but an account is fine

**NextDNS.** Per-device configurations, so the television can have a stricter policy than the work
laptop. Log retention is selectable from 1 hour to 2 years, you choose the storage region, and there is
a resumable server-sent-events log stream if you want to pull the data out programmatically. The free
tier is 300,000 queries a month.

> **Read this before you rely on it.** NextDNS **fails open past the free cap**. Once you pass 300,000
> queries in a month it keeps answering, normally, without blocking. Nothing on your television tells
> you. Nothing in your house looks different. You will believe you are filtered and you will not be.
>
> A household with a few televisions, a handful of phones and a doorbell can pass 300,000 queries a
> month without trying. If you use NextDNS, watch the query counter, or pay, or run something local
> instead.

**ControlD.** The free resolvers keep no individual logs, which is a genuine privacy property and also
means you cannot audit anything. The paid tiers add an API and log streaming.

**AdGuard public DNS** is the same option as the profile above, with no account and no per-device
policy.

## Willing to run one small box

Run **AdGuard Home**. It is the general recommendation for three reasons.

Per-client policy with tags and per-client upstreams, so the TVs get one blocklist set and everything
else gets another. A REST API, so the query log is a scriptable data source rather than a web page. And
built-in DHCP, which matters more than it sounds: it means you can hand out DHCP option 6 yourself,
without needing your router to let you change it. If you are stuck behind an ISP gateway that will not
let you set a DNS server, that one feature is the whole solution. See
[the ISP gateway guide](routers/isp-gateway.md).

Log retention is file-based, from 1 hour to 1 year.

Pick **Pi-hole v6** instead if you would rather have the largest community and the most tutorials
behind you. Every problem you hit has already been answered somewhere. v6 added an API, which earlier
versions lacked.

Either one needs a machine that is always on. A small single-board computer, a container on a NAS, or
the router itself if it runs OpenWrt or OPNsense.

## You want the data

**Blocky** is the shortest path from "I have a resolver" to "I have a queryable dataset". It writes
query logs to Postgres, MariaDB or Timescale, or to CSV, and it ships Prometheus metrics with Grafana
dashboards. Per-client group policy. It also collects no telemetry about you itself, which is worth
saying out loud about a privacy tool.

If you want to be the encrypted resolver rather than block the ones your TV picks, use **Technitium**.
It serves DoH, DoT and DoQ, so you can hand a device a private encrypted endpoint that is yours. It
also does per-client blocklists.

If you already run OPNsense, **Unbound** is there with multiple policies, Log Queries and Log Replies,
and built-in blocklist feeds that include oisd and HaGeZi. The OPNsense documentation warns that query
logging makes the server significantly slower, so size it before you turn it on.

**dnscrypt-proxy** is a good upstream and a poor policy engine. Use it in front of one of the above,
not instead of one. Per-client policy is limited, it logs suspicious queries separately rather than
giving you a general query log, and it has no API.

### Self-hosted, side by side

| Tool | Per-client policy | Log export | API | Notes |
| --- | --- | --- | --- | --- |
| AdGuard Home | Yes, with tags and per-client upstreams | Yes, file-based, 1 hour to 1 year | REST | Built-in DHCP so you can own option 6 without the router. Best general recommendation |
| Pi-hole v6 | Yes, groups | Yes | Yes, new in v6 | Largest community and most tutorials |
| Blocky | Yes, per client group | CSV, or Postgres, MariaDB, Timescale | REST plus Prometheus and Grafana dashboards | Shortest path for data analysis. Collects no telemetry itself |
| Technitium | Yes, per-client blocklists | Yes | Yes | Also a DoH, DoT and DoQ **server**, so you can hand a TV a private encrypted endpoint |
| Unbound on OPNsense | Yes, multiple policies | Log Queries and Log Replies | Via OPNsense | Built-in feeds include oisd and HaGeZi. Docs warn query logging makes the server significantly slower |
| dnscrypt-proxy | Limited | Separate logs for suspicious queries | No | Best as an upstream, not the policy engine |

### If you plan to send us a report, check the log format first

AdGuard Home's query log is JSONL with the fields `T`, `QH`, `QT`, `QC`, `ECS`, `CID`, `CP`,
`Upstream`, `Answer`, `IP`, `Result`, `Elapsed`, `Cached`. Two of those matter for privacy: `Answer` is
a fully packed DNS message, and `IP` is the client address on **every** record. So a raw AdGuard Home
query log upload leaks your LAN topology.

Never paste a raw query log into an issue. The [collector](../collector/router/) strips those fields and
shows you the exact file before anything leaves your machine. Pi-hole v6's `GET /api/queries` returns
`id`, `time`, `type`, `domain`, `cname`, `status`, `client{ip,name}`, `dnssec`, `reply{type,time_ms}`,
`list_id`, `upstream` and `ede`, and the `client` object has the same problem.

## Two resolvers that do not solve this problem

**Quad9 and Cloudflare for Families block malware, not advertising or telemetry.** They are good at
what they do. What they do is not this. If you point your TV at either one expecting content
recognition traffic to stop, nothing will happen and you will conclude that filtering does not work.

**Mullvad DNS is scheduled for discontinuation on 2 November 2026.** Do not build anything on it, and
if you already have, move now rather than in October.

## Blocklists

The resolver decides how policy is applied. The blocklist decides what policy is. They are separate
choices and people conflate them.

### HaGeZi, and why we build on it

[HaGeZi's lists](https://github.com/hagezi/dns-blocklists) are the best per-vendor work in this space.
GPL-3.0, rebuilt several times daily, and maintained by someone who actually annotates what the entries
are for. This project builds on them rather than duplicating them.

Per-device native telemetry lists, with current entry counts:

| List | Entries |
| --- | --- |
| `native.lgwebos` | 341 |
| `native.amazon` | 369 |
| `native.samsung` | 199 |
| `native.apple` | 108 |
| `native.roku` | 72 |

The URL pattern:

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.{lgwebos|samsung|roku|amazon|apple|xiaomi|huawei|oppo-realme|vivo|tiktok|winoffice}-onlydomains.txt
```

### Which HaGeZi tier

This comes from HaGeZi's own guidance rather than our opinion. The **Light** and **Normal** tiers
deliberately include only native trackers that do not break things. **Ultimate** blocks every native
tracker, and it does break things, on purpose, with that stated up front.

**Use Pro, plus the specific device lists for the hardware your household actually owns.** Pro gives
you a working default that does not generate support calls from housemates. The device lists are where
the television-specific value is, and adding only the ones you need keeps the breakage surface small
and the diagnosis easy. If something stops working, you know which four lists to bisect.

### The gaps HaGeZi does not cover

**There is no HaGeZi native list for Google or Android TV, for Vizio, or for Hisense.** That is not an
oversight on their part, it is a genuinely hard problem. Google's platform telemetry is co-mingled with
load-bearing `*.googleapis.com` hosts, and the community has isolated only three specific hostnames so
far: `androidtvchannels-pa.googleapis.com`, `androidtvlauncherxfe-pa.googleapis.com` and
`androidtvwatsonfe-pa.googleapis.com`.

Those three platforms are a large fraction of the televisions sold, and filling that gap is part of what
our [dataset](../data/endpoints/) is for. If you own a Sony, a TCL, a Vizio or a Hisense, a
[device report](../../../issues/new?template=device_report.yml) from you is directly useful.

### The other lists, and what each is for

| List | Licence | Cadence | Use it for |
| --- | --- | --- | --- |
| [HaGeZi](https://github.com/hagezi/dns-blocklists) | GPL-3.0 | Several times daily | Everything. Start here |
| [Perflyst](https://github.com/Perflyst/PiHoleBlocklist) | MIT | **Stale since 13 July 2023** | Reading the breakage annotations. See below |
| [oisd](https://oisd.nl/) | Not stated | Roughly hourly | A safe default that explicitly prioritises functionality over blocking. Weaker on device-native telemetry |
| [blocklistproject smart-tv](https://github.com/blocklistproject/Lists/blob/master/smart-tv.txt) | MIT | Updated 6 July 2026 | 77 entries, unannotated. Blocks `cloudservices.roku.com` with no breakage note, so read it before you load it |
| [StevenBlack](https://github.com/StevenBlack/hosts) | MIT | Active | General purpose. No smart TV coverage. Not a substitute for any of the above |
| [DandelionSprout GameConsoleAdblockList](https://github.com/DandelionSprout/adfilt/blob/master/GameConsoleAdblockList.txt) | | 2024 | Roughly 11 relevant console entries. That repo has no smart TV list |

### Perflyst deserves a paragraph of its own

Perflyst's lists carry **per-domain breakage annotations**, which no other list in this space does.
Comments saying what a specific domain is for and what stops working if you block it. That commentary
is the most valuable artifact anybody has produced here, and it is why Firebog's smart TV
recommendations are simply this list.

It has been stale since **13 July 2023**. Three years of vendor domain churn have happened since. So
read it for the reasoning, not as a current list, and expect entries that no longer resolve and vendor
hosts that did not exist when it was last touched.

Reproducing that annotation quality, kept current, is one of this project's reasons to exist. See
[what breaks](what-breaks.md) for our version.

## What to do next

- Install the resolver you picked, then hand it out with DHCP option 6:
  [AdGuard Home](resolvers/adguard-home.md), [Pi-hole](resolvers/pi-hole.md),
  [Blocky](resolvers/blocky.md), [NextDNS](resolvers/nextdns.md)
- Then make it stick: [OpenWrt](routers/openwrt.md),
  [pfSense and OPNsense](routers/pfsense-opnsense.md), [ISP gateway](routers/isp-gateway.md)
- Then prove it: [Verify it works](verify-it-works.md)
- If nothing is being blocked and everything looks configured: [IPv6 leaks](ipv6-leaks.md)
