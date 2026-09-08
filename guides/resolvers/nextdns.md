---
title: NextDNS
updated: 2026-09-08
---

# NextDNS

NextDNS is a hosted filtering resolver. There is no machine to run, nothing to keep patched, and
nothing that takes the household's internet down when a Raspberry Pi's SD card wears out. For readers
behind a carrier gateway whose only usable control is the upstream DNS field, it is often the single
thing they can do.

## Read this before you rely on it

**The free tier stops filtering after 300,000 queries a month. It does not stop answering.**

Past the cap, NextDNS keeps resolving names and returns them normally, including the ones on your
blocklists. Nothing on the television changes. Nothing in your house looks different. Your dashboard
stops recording blocks, and if you are not looking at your dashboard, you will believe you are
protected for the rest of the month while your set reports home exactly as it did before you started.

That failure mode is worse than no filtering, because no filtering does not lie to you.

How much is 300,000 queries? A single Hisense hostname, `api-gps-em`, has been observed connecting
thousands of times a day. Multiply that by the devices in a household and the cap is not generous. Two
televisions, a handful of phones and a laptop can reach it inside a month.

**So check your usage before you trust the setup**, and check it again a week in. The NextDNS dashboard
shows a query count for the current period. Our notes do not record the exact label or menu path, so
treat the location as **needs-confirmation** and look for the analytics or usage figure rather than
following a path from this page. If your count is anywhere near 300,000, either pay for the plan or move
to a self-hosted resolver.

If you want a resolver that fails closed, [AdGuard Home](adguard-home.md) and [Pi-hole](pi-hole.md) run
on your own hardware and either work or visibly stop working.

## Who it suits

- Your carrier gateway exposes an upstream DNS field and nothing else. See
  [ISP and carrier gateways, Branch A](../routers/isp-gateway.md#branch-a-set-the-gateways-upstream-dns).
- You do not want to run or maintain a server.
- You want per-device policy and log export without building anything.
- You are prepared to either pay for it or watch the counter.

## What it costs

| Cost | Detail |
| --- | --- |
| The cap, on the free tier | 300,000 queries a month, then it fails open and keeps answering |
| A third party holds your query history | Retention runs from 1 hour to 2 years. Every query your household makes sits on someone else's disk for as long as you choose |
| No enforcement of its own | It filters queries that reach it. A television that dials `8.8.8.8` never sends it one |

**Set retention to the shortest window that does the job.** If you are running a measurement week to
build a device report, you need days, not two years. Longer retention buys you nothing here and it
increases what a breach or a subpoena would expose. NextDNS also lets you choose the storage region,
which is worth setting deliberately rather than accepting the default.

**Undoing all of it:** point your gateway's or device's DNS back at automatic. Delete the logs and the
configuration in your NextDNS account. Nothing on any television changes.

## How to point devices at it

| Route | Enforces? | Notes |
| --- | --- | --- |
| The gateway's upstream DNS field | No | The cheapest whole-house win. Filters every device that asks the gateway |
| DHCP option 6 on a router you control | No | Advisory. Roughly two-thirds of televisions ignore it ([Mazhar and Shafiq, IoTDI 2020][iotdi] §IV-C) |
| A port 53 redirect on a router you control | **Yes** | Catches a Chromecast hardcoded to `8.8.8.8`. See [Router enforcement §2](../router-enforcement.md#2-redirect-outbound-port-53-to-your-resolver) |
| The device's own DNS field | For that device | Nothing to set on a Roku or a pre-Google-TV Chromecast |

NextDNS generates the exact resolver addresses and encrypted endpoints for your configuration in its own
dashboard, and they are specific to your account. **Our notes do not record the endpoint formats**, so
copy them from the dashboard rather than from any guide, including this one.

Being hosted has one consequence worth planning for. If you point your router's upstream at NextDNS but
do not redirect port 53, the two-thirds of televisions that resolve around you are not covered, and your
NextDNS log does not show their queries either. So the log looks clean while the set talks to Google.
That is the same trap as the fail-open cap, arriving from a different direction.

## Per-device configurations

NextDNS supports per-device configurations, which is how you get separate policy and separate log lines
for the television rather than one merged view of the whole house. The mechanism for identifying a
device is in NextDNS's own documentation and we are not going to paraphrase it here, because the setup
differs by how you connected.

What per-device buys you for this project is attribution. A merged log tells you that something in your
house looked up `acr.roku.com`. A per-device log tells you which set did, which is the difference
between a hunch and a report.

### Which lists to enable

Follow HaGeZi's own tiering rather than turning everything on. Light and Normal carry only native
trackers that do not break things. Ultimate blocks all of them and does break things. Pro plus the
device lists for hardware your household owns is the recommendation. Sizes: `native.lgwebos` 341
entries, `native.amazon` 369, `native.samsung` 199, `native.apple` 108, `native.roku` 72. There is no
HaGeZi native list for Google or Android TV, Vizio or Hisense.

[oisd][oisd] is a good safe baseline, updated about hourly, and it explicitly prioritises functionality
over blocking, which makes it weaker exactly where device-native telemetry lives. Pair it with the
per-vendor lists rather than treating it as sufficient.

Read the do-not-block tables on the vendor pages before you get enthusiastic. Blocking `ngfts.lge.com`
breaks LG Content Store thumbnails. Blocking `time.samsungcloudsolution.com` breaks Plex, YouTube and
Prime Video. Blocking `mas-ext.amazon.com` breaks Fire TV app installs.

## The log, and how to get it out

NextDNS exposes a **resumable server-sent events log stream**, which is the documented export path.
Because it resumes, a collector can reconnect after a network drop and pick up where it stopped instead
of losing the window or double-counting it.

Retention is configurable from 1 hour to 2 years, and you choose the storage region.

### Exporting for a report

This reads your NextDNS log, builds a report for one device, and prints the exact file it would upload
without uploading it. It writes only to your own disk, so there is nothing to undo.

```bash
python collector/router/fightback.py --source nextdns --device "LG OLED C3" --preview
```

Read the output, then add `--submit` to open a pull request. The `--source` values match the schema's
`resolver_kind` enum, so this one is `nextdns`.

Three things to get right, all of which are specific to a hosted resolver:

**Do not build a report from a period after you exceeded the cap.** Past 300,000 queries the log records
nothing as blocked, so `observations[].blocked` comes out false across the board and the report claims
your filtering does not work when in fact your filtering was switched off. Check the counter for the
window you are exporting.

**Start the capture before the television boots.** The IMC 2024 team found most DNS requests fire in the
first seconds after activation, so a late start loses the hostname-to-address mapping for the session.

**Record `settings.acr_state` accurately.** A report from a set with content recognition still on is as
useful as one from a set that opted out, because the open question is whether opting out survives
firmware updates. A report with that field wrong is worse than no report.

If you would rather not use a terminal, the device report form takes the same information by hand.
[CONTRIBUTING.md](../../CONTRIBUTING.md) links it.

## Other hosted resolvers, and two that do not help

| Resolver | What it does here |
| --- | --- |
| AdGuard DNS, `94.140.14.14` and `94.140.15.15` | Filters, with no per-device policy and no log you control. Fine as a five-minute improvement, no use for measurement |
| ControlD | The free resolvers keep no individual logs, which is good for privacy and means no report data. The paid tier adds an API and log streaming |
| Quad9 | Blocks malware. **Not advertising and not telemetry.** Pointing your gateway at it changes nothing about what your television reports |
| Cloudflare for Families | Same. Malware and adult content, not telemetry |
| Mullvad DNS | **Scheduled for discontinuation on 2 November 2026.** Do not build on it |

If none of those fit, the self-hosted options are [AdGuard Home](adguard-home.md), our general
recommendation, and [Pi-hole](pi-hole.md), which has the largest community and the most tutorials.

[iotdi]: https://arxiv.org/abs/2001.08288
[oisd]: https://oisd.nl/
