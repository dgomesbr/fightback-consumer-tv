---
title: Apple TV (tvOS)
platform: tvos
brands: [Apple]
generations: "tvOS. Only the tvOS 17.0 network capability is separately documented in our notes."
dns_field: standalone
dev_mode: yes # Apple developer account and TestFlight, not an on-device toggle
adb: no
package_disable: no
root: none # no tvOS root path is documented in our notes
max_tier: 2
updated: 2026-09-08
---

# Apple TV (tvOS)

There is less to do here than on any other platform in this project, and that is a finding rather than
brand loyalty. tvOS has no content recognition. It does not sample the frames on your screen, it does not
run a recogniser over your HDMI input, and there is no viewing-history pipeline to switch off. What you
are dealing with is analytics plus Apple's own ad network, which is five hostnames and a HaGeZi list of
108 entries. LG webOS has 341 entries and a recogniser that samples a frame every 10 milliseconds. DNS
is also decoupled from IP here, so Tier 1 on the device takes about a minute.

**Covers:** Apple TV hardware running tvOS.
**Also sold as:** nothing. No other brand in our platform table routes to this guide.
**How far you can get:** Tier 1 covers everything a normal reader can do, and it is close to
sufficient. Tier 2 exists as of tvOS 17 but needs a developer account, so it is a research build rather
than something you install.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Analytics | `metrics.apple.com`, `securemetrics.apple.com`, `xp.apple.com` | Not yet documented | Project endpoint set |
| Apple TV app analytics | `tv-analytics-events.apple.com` | Not yet documented | Project endpoint set |
| Apple's ad network | `iadsdk.apple.com` | Not yet documented | Project endpoint set |
| Everything else community lists have found | 108 entries in HaGeZi's `native.apple` | n/a | [HaGeZi](https://github.com/hagezi/dns-blocklists) [1] |
| Content recognition | Nothing. No recogniser, no endpoints. | n/a | Project research notes |

That last row is the whole story of this page. The comparison that makes it concrete:

| Platform | Content recognition | Sampling and cadence | Source |
| --- | --- | --- | --- |
| LG webOS | Alphonso, LG-owned since 2021, at `eu-acrX.alphonso.tv` and `tkacrX.alphonso.tv` | Frame every 10 ms, batched and sent every 15 s | [Anselmi et al., IMC 2024](https://arxiv.org/html/2409.06203v1) [2] |
| Samsung Tizen | In-house, `acr-<region>-prd.samsungcloud.tv` | Frame every 500 ms, sent about every minute | IMC 2024 [2] |
| Roku | `acr.roku.com` | Not documented | Project endpoint set |
| Sony Google TV | Samba TV, shipped as `tv.samba.ssm` | Not documented | Sony debloat guide |
| **Apple tvOS** | **None** | **n/a** | Project research notes |

Nobody has published a packet capture of a tvOS device in the literature we cite, so the analytics
cadence is unknown. No content recognition domain for tvOS turned up in any list or paper we reviewed.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

**What breaks:** ads get less relevant. Nothing stops working.

### Turn off content recognition

There is nothing to turn off. See the table above.

### Turn off ad tracking and personalisation

| Generation | Path | Status |
| --- | --- | --- |
| tvOS | Settings > General > Privacy > Apple Advertising > Personalized Ads | ⚠️ needs-confirmation |

### Other settings worth changing

| Generation | Path | Status |
| --- | --- | --- |
| tvOS | Settings > General > Privacy > Analytics & Improvements > Share Apple TV Analytics | ⚠️ needs-confirmation |

Both paths are marked needs-confirmation. If you have the hardware and can confirm the exact wording on
your tvOS version, that correction is worth more to this page than any new research.

Microphone, Siri and local network settings paths are not yet documented for this platform. See
[Open questions](#open-questions).

**What this does not fix:** the toggles cover Apple's advertising identifier and analytics sharing. They
do not stop the endpoints in the table above being contacted, and they do nothing about tracking inside
individual streaming apps. A 2019 Princeton study of streaming devices found `doubleclick.net` on 975 of
1,000 Roku channels and `amazon-adsystem.com` on 687 of 1,000 Fire TV channels [4]. Nobody has run that
count on tvOS apps. Tier 1 is what reaches app-level trackers on any platform.

## Tier 1: DNS

**Time:** 5 minutes on the device, 30 minutes at the router. **Risk:** none to the TV.
**Reversible:** yes.

**What breaks:** nothing, if you keep [the never-block set](#what-never-to-block) intact. Apple's
update, activation and App Store hosts are easy to catch with a careless wildcard, and the symptoms
(an Apple TV that will not activate, or an App Store that hangs) do not look like a DNS problem when
you hit them.

### On the device

| Generation | Path | Status |
| --- | --- | --- |
| tvOS | Settings > General > Network > *your network* > Configure DNS > Manual | ⚠️ needs-confirmation |

**DNS is decoupled from IP here.** tvOS and Samsung Tizen are the only two platforms in this project
where that is true. You set a resolver and nothing else changes, with no static address to pin, no
gateway to type and no subnet to get wrong. Everything Android-derived, plus webOS, Vizio, VIDAA,
Panasonic, Philips, Sharp and Toshiba, makes you replace the entire DHCP lease to change one field. The
path is marked needs-confirmation because Apple's own guide page does not document it.

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: a 200-home
measurement found 68% of smart TVs ignored the resolver their router handed them and queried Google
Public DNS directly ([Mazhar and Shafiq, IoTDI 2020](https://arxiv.org/abs/2001.08288) [3]). No tvOS
hardcoded resolver is documented in our notes, but the device-side setting is not something to trust on
its own. Hand out your resolver with DHCP option 6, redirect TCP and UDP port 53 to it, and build the
IPv6 twin at the same time. Router Advertisements can hand a device a resolver through the RFC 8106
RDNSS option with no DHCPv6 involved, so see [IPv6 leaks](../ipv6-leaks.md).

### What to block

HaGeZi's `native.apple` list, 108 entries, GPL-3.0, updated several times daily [1]. We build on it
rather than duplicating it. Follow HaGeZi's own guidance on tiers: Light and Normal include only native
trackers that do not break things, Ultimate blocks everything and does break things, and Pro plus the
device-specific native lists is the posture to run.

Generated lists: [`blocklists/fightback-tv-apple.txt`](../../blocklists/)

### What never to block

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `mesu.apple.com`, `gdmf.apple.com`, `gg.apple.com`, `gs.apple.com` | Software updates | Project never-block set |
| `albert.apple.com` | Device activation. A blocked activation looks like broken hardware | Project never-block set |
| `*.itunes.apple.com`, `*.apps.apple.com`, `*.mzstatic.com` | App Store, iTunes services and media artwork | Project never-block set |
| `ocsp.apple.com`, `certs.apple.com`, `valid.apple.com` | Certificate validation | Project never-block set |
| `guzzoni.apple.com` | Siri | Project never-block set |
| `*.push.apple.com` | Push notifications | Project never-block set |

*The breakage column names the service each host serves. Our notes carry this set without per-domain
test notes, so treat the specific symptom as unconfirmed.*

When you do block something, answer with NXDOMAIN rather than SERVFAIL, and REJECT rather than DROP.
Some firmware reads a silent drop as no internet and retries aggressively.

### Hardcoded addresses

None documented for tvOS. That is an absence of evidence rather than evidence of absence. For LG we
know about an OTA fallback at `156.147.69.32:8080` and a telemetry dial to `54.186.247.229:443` only
because somebody ran a WAN-side capture on a rooted set, and nobody has done the equivalent here. See
[Open questions](#open-questions).

## Tier 2: developer mode and sideloading

**Time:** not applicable to a normal reader. **Risk:** none to the device. **Warranty:** unaffected.

**tvOS 17 gained third-party packet tunnel support**, contrary to a belief that has outlived its
accuracy. We checked Apple's documentation API rather than the forums: `NEPacketTunnelProvider`,
`NEVPNManager`, `NETunnelProviderManager` and the
`com.apple.developer.networking.networkextension` entitlement all show tvOS 17.0 availability.
Whole-device DNS and SNI visibility is now possible on an Apple TV, which was not true before. The
ceiling is specific.

| Capability | API | tvOS status |
| --- | --- | --- |
| Whole-device packet tunnel, so DNS and SNI visibility | `NEPacketTunnelProvider` | Available from tvOS 17.0 |
| VPN configuration management | `NEVPNManager`, `NETunnelProviderManager` | Available from tvOS 17.0 |
| Per-app attribution, so knowing which app made a connection | `NEAppProxyProvider` | Unavailable |
| Content filtering | `NEFilterDataProvider` | Unavailable |
| System-wide DNS settings | `NEDNSSettingsManager` | Unavailable |
| DNS proxying | `NEDNSProxyProvider` | Unavailable |

The entitlement is managed, so Apple has to grant it before anything builds.

**Getting it onto the App Store is implausible, and that is the honest limit.** Guideline 5.4(a)
requires a VPN app to be "offered by a VPN provider, not by a third party", with disclosures about
"which servers and countries" the app uses. A tunnel that terminates on the device itself has no
servers and no countries, so it structurally cannot make the disclosure the guideline demands.
Guideline 2.5.1 adds an intended-purpose clause on top of that.

TestFlight is the realistic path: 100 internal testers, 10,000 external testers, and Beta App Review in
between. That makes a tvOS observer a research build for people who can run Xcode, not something a reader
can install this evening. Design around that constraint rather than discovering it at submission.

## Tier 3: disable preinstalled advertising and metrics apps

Does not exist on tvOS. There is no package manager, no ADB equivalent and no way to disable a system
component.

## Tier 4: root and custom firmware

No tvOS root or custom firmware path is documented in our research, so there is nothing for us to link
or warn about. See [Open questions](#open-questions).

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Personalised ads. Nothing else documented. | Turn the toggle back on |
| 1 | Nothing, if you keep the never-block set. A careless wildcard on `apple.com` breaks activation, updates and the App Store together | Remove the entry, restart the resolver |
| 2 | Not applicable, a developer build affects only the device you install it on | Delete the TestFlight build |
| 3 | Does not exist | n/a |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is confirming
that `iadsdk.apple.com` and `metrics.apple.com` show up in your resolver's query log attributed to the
Apple TV's own address, and are answered with NXDOMAIN. If the Apple TV appears in the log at all, your
interception is working; if it never appears, it is talking to something else and you have not tested
what you think you tested.

Two specifics:

1. Repeat every check over IPv6. See [IPv6 leaks](../ipv6-leaks.md).
2. Start the capture before you power on the device. The 2024 IMC team found most DNS requests fire in
   the first seconds after activation [2], so a late start loses the mapping for the session.

## Open questions

1. **Both Tier 0 paths and the Configure DNS path.** Apple's own guide pages document none of them.
   Confirmation from real hardware, with the tvOS version, clears three markers off this page.
2. **Analytics cadence.** How often `metrics.apple.com`, `xp.apple.com` and
   `tv-analytics-events.apple.com` are contacted, and whether the Tier 0 toggles change it. A
   resolver-log contribution settles this.
3. **Whether the Tier 0 toggles stop the traffic.** The 2024 IMC study proved opt-out works on Samsung
   and LG [2]. Nobody has run that experiment on tvOS.
4. **Microphone, Siri and local network settings paths.**
5. **Hardcoded IP dials.** No WAN-side capture of a tvOS device exists in our notes, so we cannot say
   whether DNS filtering is sufficient here.
6. **Whether a tvOS root or jailbreak path exists.** Our notes are silent, which is not a negative
   result.
7. **Whether Apple grants the managed NetworkExtension entitlement for a local-only tunnel.** The tvOS
   17 capability is confirmed from the API. Whether anyone has shipped one is untested.
8. **Whether a firmware update re-enables the Tier 0 toggles.** Undocumented everywhere, and measurable.

## Sources

1. [HaGeZi DNS blocklists](https://github.com/hagezi/dns-blocklists). GPL-3.0, updated several times
   daily, `native.apple` at 108 entries. List URL pattern:
   `https://cdn.jsdelivr.net/gh/hagezi/dns-blocklists@latest/wildcard/native.apple-onlydomains.txt`
2. [Anselmi et al., IMC 2024](https://arxiv.org/html/2409.06203v1). Samsung and LG content recognition
   domains and cadence, that opting out works, and that most DNS requests fire seconds after activation.
   Code and data at [SafeNetIoT/ACR](https://github.com/SafeNetIoT/ACR), AGPL-3.0.
3. [Mazhar and Shafiq, IoTDI 2020](https://arxiv.org/abs/2001.08288) §IV-C, for the 68% figure. The
   repeated 72% figure mis-cites this paper.
4. [Moghaddam et al., CCS 2019](https://blog.citp.princeton.edu/2019/09/18/watching-you-watch-the-tracking-ecosystem-of-over-the-top-tv-streaming-devices/),
   for the Roku and Fire TV channel counts.
5. Apple documentation API, queried 8 September 2026, for tvOS 17.0 availability of
   `NEPacketTunnelProvider`, `NEVPNManager`, `NETunnelProviderManager` and the
   `com.apple.developer.networking.networkextension` entitlement, and for the unavailability of
   `NEDNSSettingsManager`, `NEDNSProxyProvider`, `NEFilterDataProvider` and `NEAppProxyProvider`.
6. App Store Review Guidelines 5.4(a) and 2.5.1, and the TestFlight limits of 100 internal and 10,000
   external testers with Beta App Review.
