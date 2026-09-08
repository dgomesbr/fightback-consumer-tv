---
title: Roku (Roku OS)
platform: roku
brands: [Roku, TCL, Hisense, Philips, Sharp]
generations: "All Roku OS versions, streaming players and Roku TVs. Roku OS 14.1 noted where it changes behaviour."
dns_field: none
dev_mode: yes
adb: no
package_disable: no
root: none
max_tier: 2
updated: 2026-09-08
---

# Roku (Roku OS)

You cannot fix this on the device. Roku OS has no DNS field and no static IP form in any version,
including Roku TVs, so there is nothing on the box to point at a filtering resolver. There is no ADB,
no package manager access, and no public root. Turn off the four privacy settings in Tier 0, then do
the rest of the work at your router. If you are not willing to change something at the router, Tier 0
is your ceiling on this hardware.

**Covers:** Roku streaming players, sticks and Roku TVs, all Roku OS versions
**Also sold as:** TCL, Hisense, Philips and Sharp all ship Roku TV models. If the home screen is a
grid of channel tiles with a purple remote, you are in the right guide regardless of the badge on the
bezel.
**How far you can get:** Tier 1. Developer mode exists and is documented below as Tier 2, but it buys
you nothing for privacy: one sideloaded app at a time, in a sandbox with no view of the network or of
other apps.

## What this device sends home

Cadence is missing from most rows because nobody has published per-second measurements for Roku. The
IMC 2024 content recognition study covered Samsung and LG only. Treat every hostname below as
"appears in curated blocklists and, where marked, in a peer-reviewed capture", not as proof of what
left your house.

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Content recognition | `acr.roku.com` | Not documented | HaGeZi `native.roku` [5]. No published capture. **UNVERIFIED for cadence and for which inputs trigger it.** |
| Device logs and traces | `logs.roku.com` plus its `scribe`, `midland`, `austin`, `cooper`, `liberty` and `mobile` subdomains; `logs.sr.roku.com`, `traces.sr.roku.com`, `userdata.sr.roku.com` | Not documented | HaGeZi `native.roku` [5]. PETS 2021 observed `cooper.logs.roku.com` and `scribe.logs.roku.com` and classified both as non-required [1] |
| Configuration and device check-in | `configsvc.cs.roku.com` | Not documented | PETS 2021, classified non-required [1] |
| First-party advertising | `ads.roku.com`, `adservices.roku.com`, `advertising.roku.com`, `ads-us-east-1.delivery.roku.com` and regional siblings, `pixel.web.roku.com`, `roku.adsmeasurement.com`, `ravm.tv`, `display.ravm.tv` | Not documented | HaGeZi `native.roku` [5] |
| Voice samples | `samples.voice.cti.roku.com` | Not documented | HaGeZi `native.roku` [5] |
| Third-party tracking inside channels | `doubleclick.net` reached by 975 of the top 1,000 Roku channels. `partnerad.l.doubleclick.net` seen in the Roku capture and classified non-required | Per channel session | CCS 2019 [2], PETS 2021 [1] |
| Wi-Fi network name | SSIDs observed leaving toward trackers | Not documented | CCS 2019 [2] |

`acr.roku.com` is the single most on-target hostname on this platform. If you block one thing, block
that.

The strongest published result for Roku owners comes from PETS 2021 [1]. The researchers classified
every destination a Roku contacted as required or non-required for the device to function, and the
required set came out at two entries: `api.sr.roku.com` and `youtube.com`. Everything else they saw
was optional. That is an unusually firm basis for aggressive blocking, because it means the failure
mode of over-blocking Roku is narrow and known rather than a guess.

Two other papers matter here. CCS 2019 [2] counted `doubleclick.net` on 975 of the top 1,000 Roku
channels, so channel-level tracking is close to universal and is separate from anything Roku itself
sends. PETS 2020 [3] found that existing blocklists defend better against third-party trackers than
against a platform's own first-party telemetry, which is why the vendor-specific list in Tier 1 is
worth adding on top of a general list.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

Nothing here breaks playback. Turning off channel microphone access stops voice features inside
channels that use them. Resetting the advertising identifier makes ads less relevant to you, which is
the point.

Every path below is marked ⚠️ **needs-confirmation** for one reason: nobody has been able to check
them against a vendor document. Roku's privacy policy page renders client-side, so a fetch returns an
empty shell rather than text, and Roku's support sitemap contains no privacy article at all. The paths
come from secondary sources. If you own a Roku, correcting one of these rows is the single most useful
thing you can send this project.

### Turn off content recognition

| Generation | Path | Status |
| --- | --- | --- |
| Roku TVs only | Settings > Privacy > Smart TV Experience, then uncheck **Use info from TV inputs** | ⚠️ needs-confirmation |
| Streaming players and sticks | This setting does not appear. Content recognition on Roku OS is tied to TV inputs, so a player plugged into someone else's TV has no equivalent toggle. | ⚠️ needs-confirmation |

Unchecking that box is the one Tier 0 action with a measured analogue elsewhere. IMC 2024 found that
on Samsung and LG sets, opting out produced a complete absence of traffic to every content
recognition domain the researchers had identified. Nobody has repeated that test on Roku. Assume the
toggle helps and verify with Tier 1 anyway.

### Turn off ad tracking and personalisation

| Generation | Path | Status |
| --- | --- | --- |
| Older builds | Settings > Privacy > Advertising, then **Limit ad tracking** | ⚠️ needs-confirmation |
| Newer builds | Settings > Privacy > Advertising, then **Personalize ads** (same screen, renamed control) | ⚠️ needs-confirmation |
| All builds | Settings > Privacy > Advertising, then **Reset advertising identifier** | ⚠️ needs-confirmation |

Reset the identifier after you change the toggle, not before. The toggle stops new linkage; the reset
breaks the existing profile's key.

### Other settings worth changing

**Microphone.** Settings > Privacy > Microphone > **Channel microphone access**. ⚠️
needs-confirmation. This governs whether channels can request the mic, not whether the remote's voice
button works.

**Control by mobile apps.** Turn this off if you do not use a phone as a remote. It is in the same
settings area and is ⚠️ needs-confirmation. From Roku OS 14.1 this gates most commands sent over the
External Control Protocol on port 8060, which is the LAN service that hands out your model, serial
number, device ID, software version and MAC addresses to anything on the network that asks. See
[External Control Protocol](#external-control-protocol-port-8060) below for what that service exposes
and why closing it is worth doing.

**What this does not fix:** everything in the table above still resolves and still connects. Tier 0
changes what Roku says it does with the data, not whether the device talks to those hosts. Worse,
there is a report that Roku falls back to Google's public resolvers, 8.8.8.8 and 8.8.4.4, from Roku OS
5.4 onward if the DHCP-supplied resolver does not answer the way it expects. That report is Reddit
sourced, could not be fetched directly and is **UNVERIFIED**, but it is consistent with the 68% of
smart TVs that IoTDI 2020 measured reaching Google Public DNS directly across 200-plus homes [4]. If
it holds for your unit, handing Roku a resolver address is theatre and only a router rule works. Go
to Tier 1.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

If you get the blocklist wrong, channels fail to load or the device claims it has no internet. The
fix is removing the entry you added, so nothing here is permanent. Two habits keep the damage small:
answer blocked names with NXDOMAIN rather than SERVFAIL, and REJECT rather than DROP on the firewall.
Some firmware reads a SERVFAIL or a silently dropped connection as "no internet" and retries hard,
which turns a quiet block into a traffic storm.

### On the device

There is no DNS setting on this platform. There is no static IP form either, in any Roku OS version,
on players and on Roku TVs alike. Roku is the only platform in this project with nothing at all on
this axis, which is why every other section points at your router.

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: handing out your
resolver with DHCP option 6 is necessary but not sufficient, because a Roku that ignores option 6 has
no on-device field you can correct, so you need a port 53 redirect that forces every LAN client to
your resolver whether it asked to use it or not. Add the IPv6 twin of that rule and reject port 853,
or you have built half a fence.

Three specifics that decide whether this works:

- **DHCP option 6** is defined in [RFC 2132](https://www.rfc-editor.org/rfc/rfc2132.html) §3.8. Set
  it first, because it is the path that produces clean per-client attribution in your query log.
- **Redirect TCP and UDP port 53** to your resolver, and exclude the resolver itself from the rule.
  On OpenWrt that is the `src_ip="!192.168.2.2"` line in the documented `intercept_dns` recipe [8].
  Omitting the exclusion causes a redirect loop, and it is the step people forget.
- **Do the IPv6 version.** RFC 8106 lets a Router Advertisement hand a device a resolver through the
  RDNSS option, type 25, with no DHCPv6 involved at all. An IPv4-only rule leaks. See
  [IPv6 leaks](../ipv6-leaks.md).

Carrier-grade NAT does not affect any of this. It comes up in every thread on the subject and it is
irrelevant to outbound interception.

### What to block

The endpoint list lives in [`data/endpoints/roku.yml`](../../data/endpoints/roku.yml), with a flag on
each entry for what it breaks. Do not copy hostnames out of this page into your resolver; the YAML is
the version that gets corrected.

Generated lists: [`blocklists/fightback-tv-roku.txt`](../../blocklists/)

For a curated upstream list, HaGeZi's `native.roku` carries 72 entries, is GPL-3.0 and updates
several times daily [5]:

```
https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.roku-onlydomains.txt
```

HaGeZi's own guidance is that the Light and Normal tiers deliberately include only native trackers
that do not break things, while Ultimate blocks everything and does break things. Pro plus
`native.roku` is the posture to recommend for a household with a Roku in it.

**Do not wildcard `roku.com`.** A wildcard takes `api.sr.roku.com` with it, and PETS 2021 classified
that hostname as required for the device to work [1]. This is the most common way people brick their
own Roku with a blocklist.

**Watch `cloudservices.roku.com`.** The blocklistproject `smart-tv` list, 77 entries as of 2026-07-06,
blocks it with no breakage annotation [7]. Nobody has documented what it does or what stops working
without it. Perflyst's list is the only one in this space that annotates per-domain breakage, and it
has been stale since 13 July 2023 [6], so there is no maintained commentary to fall back on. Leave
`cloudservices.roku.com` alone until someone tests it, and if you do test it, report the result.

### What never to block

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `api.sr.roku.com` | The device. PETS 2021 classified it as one of only two required destinations. | [1] |
| `youtube.com` | YouTube. Also one of the two required destinations. | [1] |
| `roku.com` as a wildcard | Takes `api.sr.roku.com` with it. Match specific hostnames. | [1] |
| `cloudservices.roku.com` | Unknown. Blocked by blocklistproject with no breakage note, and no maintained list annotates it. Treat as unknown risk, not as safe. | [7] |

### Hardcoded addresses

No IP:port pair that Roku dials without a DNS lookup has been documented. That is a gap in the
research, not a clean bill of health; the only platform where such addresses have been captured is LG,
and that took a rooted set.

The nearest thing on Roku is the reported resolver fallback to 8.8.8.8 and 8.8.4.4 from Roku OS 5.4
[**UNVERIFIED**, Reddit, could not be fetched directly]. That is a hardcoded *resolver*, not a
hardcoded destination, and the port 53 redirect above catches it. Catching a hardcoded destination
would need a WAN-side packet capture, which is on the open questions list.

## External Control Protocol, port 8060

Roku ships a plain HTTP control service on port 8060 that any device on your LAN can read without
authentication. It is the one genuinely useful power-user feature on this platform, and it cuts both
ways.

**As an audit tool.** Two requests tell you what the device is and what is installed on it, with no
developer mode and no account:

```
curl http://<roku-ip>:8060/query/device-info
curl http://<roku-ip>:8060/query/apps
```

`/query/device-info` returns the model, serial number, device ID, software version, MAC addresses,
timezone and locale. `/query/apps` lists the installed channels. That is enough to record exactly
which model and firmware a measurement came from, which is what makes a device report useful to this
project rather than anecdotal.

**As a fingerprinting surface.** The same request works for anything else on the network, including a
compromised laptop, an IoT gadget or a guest's phone. Serial number, device ID and MAC addresses are
stable identifiers, and they are readable over unauthenticated HTTP.

If you do not use a phone or tablet as a remote, turn off **Control by mobile apps** in settings. From
Roku OS 14.1 that gates most control commands over ECP. Whether it closes the informational queries
above or only the command verbs is not documented, and is in the open questions.

## Tier 2: developer mode and sideloading

**Time:** 1 hour. **Risk:** low. **Reversible:** yes. **Warranty:** unaffected, this is an official
vendor feature.

Developer mode on Roku is real, official and useless for privacy. It is documented here so nobody
spends an evening discovering that for themselves.

Enable it from the remote: **Home three times, Up twice, then Right, Left, Right, Left, Right.** You
get a web installer served at the device's IP, logging in as user `rokudev`, plus telnet debug
consoles on port 8085 for BrightScript and 8080 for SceneGraph.

**What it does not let you do, which is the important part.** Roku's developer documentation states
that "scripts only have access to platform resources that are exposed to the scripting layer as
BrightScript components" [12]. No packet capture. No DNS visibility. No view of any other app's
traffic. Roku's certification requirements separately forbid cross-app functionality, so even a
sanctioned app could not do it. Compare Fire OS and Android TV, where a third-party app can observe
the whole device's traffic through `VpnService`. On Roku that class of tool cannot be built.

**Only one app can be sideloaded at a time**, and installing a second replaces the first. So there is
no "install a monitor and leave it running while you use the TV normally" workflow either.

> **Expiry and distribution traps.** The private and non-certified channel programme is not offered
> today. Roku's current developer documentation lists two options: public, which requires
> certification, and beta, which "cannot be published to the public Streaming Store" [12]. A beta
> channel lasts **120 days**, an account is capped at **10 beta apps**, and each takes **20 testers**.
> After 120 days it is gone. The exact date private channels were retired is **UNVERIFIED**: the
> developer forum archive is offline and the Wayback Machine holds no snapshot of a non-certified
> channels document.

## Tier 3: disable preinstalled advertising and metrics apps

This tier does not exist on Roku. There is no ADB, no package manager access and no shell. The
BrightScript sandbox described in Tier 2 is the only code execution a Roku owner gets, and it cannot
see or touch other channels. Nothing to disable, no way to disable it.

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

There are no steps to publish. No public root exists for Roku OS, and no community rooting attempt for
the platform could be found during research. Contrast webOS, which has a compatibility oracle and five
named autoroot tools, and Fire OS, which has a MediaTek bootrom exploit for two SKUs. Roku has
nothing.

**What root gets you:** unknown, because nobody has demonstrated it. On webOS, root buys a writable
hosts file and the ability to neuter crash-upload spools, so the equivalent capability on Roku would
be on-device blocking that survives leaving the house. That is speculation, not a claim.

**What it costs you:** not applicable, since there is no project to attempt.

**Where to go:** nowhere. If you find a credible Roku rooting project, open an issue rather than
following it blind. US readers should note that
[37 CFR 201.40(b)(10)](https://www.ecfr.gov/current/title-37/section-201.40) exempts circumvention for
the sole purpose of running lawfully obtained applications on a smart TV or streaming device, and that
the exemption does not displace a licence agreement. See [LEGAL.md](../../LEGAL.md).

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Voice features inside channels that use the mic, if you turn off channel microphone access. Phone remote apps, if you turn off Control by mobile apps. Ads become less relevant. Playback is unaffected. | Turn the setting back on in Settings > Privacy |
| 1 | Over-blocking makes channels fail to load or the device report no internet. Wildcarding `roku.com` takes `api.sr.roku.com` down and breaks the device. | Remove the entry from your resolver, then reboot the Roku so it re-resolves |
| 2 | The sideloaded app replaces any previous sideloaded app. Beta channels vanish after 120 days. | Disable developer mode and factory reset if the device is left in a bad state |
| 3 | Not applicable, no such tier on this platform | |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is
**confirming the Roku's own queries appear in your resolver log under the Roku's client IP**, because
there is no on-device DNS field you can inspect to prove where it is asking. Filter your query log to
the Roku's address and watch for a few minutes with the device idle on the home screen. An empty
result means the device is resolving somewhere you cannot see, not that it is quiet.

Then capture the LAN side for port 53, port 853 and UDP 443, and repeat the whole check over IPv6.
Start the capture before the Roku boots. The IMC 2024 team noted that most DNS requests fire in the
first seconds after activation, so a late start loses the hostname-to-address mapping for the session
and everything after that looks like traffic to bare IPs.

Use `/query/device-info` on port 8060 to record the exact model and software version you tested, so
the result is attributable.

## Open questions

Roku is the least-measured platform in this project, and the hardware is cheap and widespread, so
these are all answerable by a reader with a device and a query log.

- **No menu path in Tier 0 has been confirmed against a vendor document or on hardware.** Roku's
  privacy policy page renders client-side and the support sitemap has no privacy article. Every path
  on this page is a secondary source. Confirming or correcting one, with the model and Roku OS version,
  is the highest-value contribution here.
- **Is `acr.roku.com` actually contacted, on which models, and how often?** It appears in blocklists.
  No published capture confirms it. The IMC 2024 study measured Samsung and LG cadence and left Roku
  out.
- **Does unchecking "Use info from TV inputs" stop that traffic?** IMC 2024 proved opt-out works on
  Samsung and LG. Nobody has repeated the test on a Roku TV.
- **Does Roku fall back to 8.8.8.8 and 8.8.4.4 from Roku OS 5.4?** Reddit-sourced, unfetchable,
  UNVERIFIED. A LAN capture on port 53 answers it in ten minutes.
- **Does turning off "Control by mobile apps" close `/query/device-info` on port 8060, or only the
  command verbs?** Roku OS 14.1 changed the gating. The scope is not documented.
- **What does `cloudservices.roku.com` do, and what breaks without it?** blocklistproject blocks it
  unannotated.
- **Does Roku dial any hardcoded IP:port?** Needs a WAN-side capture. None documented either way.
- **When was the private and non-certified channel programme retired?** The forum archive is gone and
  Wayback has no snapshot.
- **Does the developer-mode remote sequence differ by Roku OS version?** Only one sequence is
  documented.

## Sources

1. Mandalari et al., *Blocking Without Breaking*, PETS 2021.
   https://arxiv.org/abs/2105.05162
   Per-device required and non-required destinations. Roku required: `api.sr.roku.com`,
   `youtube.com`. Non-required: `configsvc.cs.roku.com`, `cooper.logs.roku.com`,
   `scribe.logs.roku.com`, `partnerad.l.doubleclick.net`, plus four Netflix analytics endpoints.
2. Moghaddam et al., *Watching You Watch*, CCS 2019.
   https://blog.citp.princeton.edu/2019/09/18/watching-you-watch-the-tracking-ecosystem-of-over-the-top-tv-streaming-devices/
   `doubleclick.net` on 975 of the top 1,000 Roku channels, SSIDs leaking to trackers.
3. Varmarken et al., *The TV is Smart and Full of Trackers*, PETS 2020.
   https://arxiv.org/abs/1911.03447
   Blocklists defend third-party tracking better than first-party platform telemetry.
4. Mazhar and Shafiq, IoTDI 2020. https://arxiv.org/abs/2001.08288
   68% of smart TVs in 200-plus homes reached Google Public DNS directly. The commonly quoted 72% is
   a mis-citation of this paper.
5. HaGeZi DNS blocklists. https://github.com/hagezi/dns-blocklists
   GPL-3.0, updated several times daily. `native.roku` has 72 entries.
6. Perflyst PiHoleBlocklist. https://github.com/Perflyst/PiHoleBlocklist
   The only list with per-domain breakage annotations, stale since 13 July 2023.
7. blocklistproject `smart-tv`.
   https://github.com/blocklistproject/Lists/blob/master/smart-tv.txt
   MIT, 77 entries as of 2026-07-06, unannotated, blocks `cloudservices.roku.com`.
8. OpenWrt, intercept DNS.
   https://openwrt.org/docs/guide-user/firewall/fw3_configurations/intercept_dns
   The port 53 redirect recipe, identical for fw3 and fw4.
9. RFC 2132 §3.8, DHCP option 6. https://www.rfc-editor.org/rfc/rfc2132.html
10. RFC 8106, RDNSS option type 25 and DNSSL type 31 in IPv6 Router Advertisements.
11. 37 CFR 201.40(b)(10). https://www.ecfr.gov/current/title-37/section-201.40
    DMCA exemption covering smart TVs and streaming devices.
12. Roku developer documentation, fetched 8 September 2026. Establishes the BrightScript sandbox
    restriction, the certification ban on cross-app functionality, one-sideloaded-app-at-a-time, the
    ECP endpoints on port 8060, and the beta channel limits of 120 days, 10 apps and 20 testers. No
    stable URL was recorded in `RESEARCH-NOTES.md`, so this citation needs a permalink added.
