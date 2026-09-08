---
title: Vizio (SmartCast)
platform: smartcast
brands: [Vizio]
generations: "SmartCast, current and older firmware. Menu wording differs between them."
dns_field: static-ip-required
dev_mode: no
adb: no
package_disable: no
root: none
max_tier: 1
updated: 2026-09-08
---

# Vizio (SmartCast)

Vizio SmartCast is closed. No developer mode, no sideloading, no ADB, no root, no third-party SDK, and
no homebrew project exists for it [6]. Two things are available to you, the TV's own settings menu and
your router, and this page covers both.

Start with the Viewing Data toggle, because it is the one setting on any television in this project
that a regulator forced into existence. In February 2017 the FTC and the New Jersey Attorney General
fined Vizio $2.2 million over second-by-second viewing data collected from 11 million televisions, with
age, income, marital status and home value appended to it and the result sold on [1]. The order that
settled the case requires Vizio to obtain affirmative express consent before doing that again [1][6].
So the toggle is in the menu because a regulator put it there, and switching it off is a right rather
than a favour.

**Covers:** Vizio SmartCast televisions and Vizio streaming hardware running SmartCast
**Also sold as:** nothing. Vizio does not license SmartCast to other brands in our notes.
**How far you can get:** Tier 1. There is no device-side access above the settings menu, so DNS at the
router is the ceiling.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Viewing data, the feed the FTC case was about. This is Inscape | `control`, `control2`, `control-zoo-dai-default`, `control-zoo-dtsstage`, `mcp` and `tvmeta-dynamic` under `.tvinteractive.tv` | Not yet documented. See Open questions. | [2][7] |
| Legacy smart-platform telemetry | `digitalhomeservices.yahoo.com`, `widgets.yahoo.com` | Not yet documented | [2][7] |
| Possibly corporate rather than device traffic | `inscape.tv`, `tvmetrix.com` | Not yet documented. See Open questions. | [7], low confidence |
| Time sync | `vizio.pool.ntp.org`, hardcoded in firmware | Not yet documented | [7][8] |

The whole `tvinteractive.tv` zone is the target. Match it with the regex `(\.|^)tvinteractive\.tv$`
rather than listing hosts, because the subdomain set is not stable [2][7]. The `inscape.tv` and
`tvmetrix.com` entries are held out of the core tier because the source is low confidence and they may be
corporate websites rather than data endpoints [7].

Nobody has published a packet capture of a current SmartCast set, so the strongest evidence here is
legal. The FTC's 2017 complaint describes the capture, the demographic append and the onward sale, and
the consent order names the remedy [1]. Vizio's recognition business is a named subsidiary with its own
corporate domains, which plainly explains why the device has no developer surface at all. Whether that
business is a material revenue line for Vizio is **UNVERIFIED** in our notes and sits under Open
questions.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

**What this breaks:** nothing we have documented. Viewing Data governs the recognition feed, not
playback, apps or casting. If your set behaves differently after the toggle, that is a
[bug report](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=bug_report.yml) and
we want it.

Every Vizio privacy and support URL probed during research returned HTTP 404 or 401 [6]. The paths
below come from community write-ups and older Vizio documentation, so all three are marked
needs-confirmation and none has been checked against a set with a known model and firmware. If you own
one, confirming a path is a five-minute contribution.

### Turn off content recognition

| Generation | Path | Status |
| --- | --- | --- |
| Current firmware | All Settings > Privacy & Legal > Viewing Data | ⚠️ needs-confirmation |
| Older firmware | All Settings > Admin & Privacy > Viewing Data | ⚠️ needs-confirmation |
| Older still | Menu > System > Reset & Admin > Viewing Data | ⚠️ needs-confirmation |

### Turn off ad tracking and personalisation

Not yet documented. See Open questions. Our notes record no separate Vizio advertising or
interest-based-ads toggle, and we will not guess at one. On Samsung and LG sets those switches sit next
to the viewing-data switch, so check the same screen and tell us what is on it.

### Other settings worth changing

Not yet documented. See Open questions. We have no sourced path for the microphone, voice services,
mobile device access or automatic updates on SmartCast.

**What this does not fix:** the toggle has been measured on Samsung and LG, where opting out produced a
complete absence of traffic to every content recognition domain the researchers had identified [4]. No
equivalent measurement exists for Vizio. Treat Tier 0 as necessary and unproven here, and do Tier 1 as
well. Separately, 68% of the smart TVs in a 200-plus-home study reached Google Public DNS directly
instead of using the resolver their router handed them [3]. That study did not break results out by
brand, so we cannot tell you whether a Vizio is in that 68%, which is the argument for enforcing DNS at
the router rather than trusting the field on the TV.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

### On the device

SmartCast has a DNS field, but it is bundled with a full static IP. Turning DHCP off means you also
own the address, gateway and netmask for that TV forever, and an address collision later shows up as
"the TV stopped working" [6].

| Path | Status |
| --- | --- |
| Menu > Network > Manual Setup, set DHCP off, then Pref DNS Server and Alt DNS Server | ⚠️ needs-confirmation |

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: set the resolver
in DHCP option 6 for the whole network, then redirect outbound port 53 to your resolver and reject port
853 so a TLS resolver cannot be used as an escape hatch. Do the IPv6 twin of every rule, because a
Router Advertisement can hand the TV a resolver through RFC 8106 with no DHCP involved at all [6].

### What to block

The endpoint set lives in [`data/endpoints/vizio.yml`](../../data/endpoints/vizio.yml) with a breakage
flag per entry, rather than being duplicated here. The one line that matters is the regex
`(\.|^)tvinteractive\.tv$` [2][7].

HaGeZi publishes no Vizio list [5], and neither does anyone else we found. This vendor is one of the
real gaps in the blocklist landscape, so the Vizio list in this repo is ours to get right.

Generated lists: [`blocklists/fightback-tv-vizio.txt`](../../blocklists/)

### What never to block

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `api.vizio.com` | SmartCast features stop working | [2][7] |
| `images.vizio.com` | SmartCast artwork stops loading | [2][7] |
| `vizio.pool.ntp.org` | The clock drifts and certificate validation starts failing | [7][8] |
| `announcements.vizio.com` | Perflyst explicitly declines to block this one | [6] |

### Hardcoded addresses

No hardcoded IP and port pair is documented for SmartCast. `vizio.pool.ntp.org` is hardcoded as a
hostname, so DNS filtering can see it, which is why it is on the never-block list rather than needing a
firewall rule [7][8]. If you capture a SmartCast set dialling a bare IP address, that belongs in
`data/hardcoded/vizio.yml` and we want the report.

## Tier 2: developer mode and sideloading

Does not exist. SmartCast has no developer mode, no sideloading path and no third-party SDK [6].

## Tier 3: disable preinstalled advertising and metrics apps

Not possible. There is no ADB, no shell and no package manager you can reach [6].

## Tier 4: root and custom firmware

Not possible today. No public root, jailbreak or custom firmware project exists for SmartCast, so
there is no upstream to link and nothing for us to warn you away from [6]. If one appears, it belongs
here as a link and an honest risk statement, not as steps. See [LEGAL.md](../../LEGAL.md).

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | Nothing documented | Turn the toggle back on |
| 1 | SmartCast apps and casting if you block `api.vizio.com` or `images.vizio.com`. Clock and TLS failures if you block `vizio.pool.ntp.org` | Remove the entry from your resolver and reboot the TV |
| 2 | Not applicable | |
| 3 | Not applicable | |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is watching
your resolver's query log for `tvinteractive.tv` in the hour after you switch Viewing Data off. Nobody
has measured whether Vizio's toggle actually stops the traffic, so you are the measurement. Start the
capture before the TV boots, because most DNS requests fire in the first seconds after activation and a
late start loses the mapping for that session [6].

## Open questions

Anything here that you can answer with a Vizio in front of you is a direct contribution. Use the
[device report form](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=device_report.yml).

- Does turning Viewing Data off actually stop traffic to `tvinteractive.tv`? Measured on Samsung and LG
  [4], never on Vizio.
- Which of the three Viewing Data menu paths is correct for which firmware? All three are unconfirmed,
  and every Vizio privacy URL we probed returned 404 or 401 [6].
- Is there a separate advertising toggle on SmartCast, and a microphone or voice-services toggle?
- How often does a SmartCast set contact `tvinteractive.tv`, and does it keep doing so when the TV is
  used as a plain HDMI display?
- Are the Inscape corporate domains ever contacted by a television, or are they corporate-only? Our
  source for them is low confidence [6].
- Is Vizio's recognition business a material revenue line? **UNVERIFIED** in our notes. A figure from a
  Vizio annual report or SEC filing would settle it.
- Does a SmartCast set honour DHCP option 6, or does it reach a resolver of its own? No brand-level
  breakdown exists behind the 68% figure [3].

## Sources

1. FTC and New Jersey Attorney General, February 2017.
   [Vizio to pay $2.2 million to FTC, State of New Jersey to settle charges it collected viewing
   histories on 11 million smart televisions without users' consent](https://www.ftc.gov/news-events/news/press-releases/2017/02/vizio-pay-22-million-ftc-state-new-jersey-settle-charges-it-collected-viewing-histories-11-million)
2. Perflyst, [PiHoleBlocklist](https://github.com/Perflyst/PiHoleBlocklist), specifically `SmartTV.txt`
   and `regex.list`. MIT, stale since 13 July 2023, still the only list that annotates what each domain
   breaks.
3. Mazhar and Shafiq, IoTDI 2020, [Characterizing Smart Home IoT Traffic in the
   Wild](https://arxiv.org/abs/2001.08288) §IV-C. 68% of smart TVs reached Google Public DNS directly.
   The "72%" figure circulating online is a mis-citation of this paper.
4. Anselmi et al., IMC 2024, [Watching TV with the Second-Party](https://arxiv.org/html/2409.06203v1).
   Opt-out verified effective on Samsung and LG.
5. HaGeZi, [dns-blocklists](https://github.com/hagezi/dns-blocklists). GPL-3.0. No Vizio list exists.
6. [Project research notes](../../RESEARCH-NOTES.md), Vizio section and cross-cutting facts, gathered 8
   September 2026.
7. Project endpoint data, [`data/endpoints/vizio.yml`](../../data/endpoints/vizio.yml), where each entry
   carries its own upstream source, tier and breakage flag.
8. [jrwren/hosts, vizio](https://github.com/jrwren/hosts/blob/master/vizio). Source for
   `vizio.pool.ntp.org`.
