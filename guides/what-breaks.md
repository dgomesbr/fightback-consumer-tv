# What breaks

**A blocklist that kills someone's Netflix does more harm than good.** This page is organised by what
you notice, because that is what you have when something goes wrong.

Find your symptom, check the table, unblock the host, then read [how to bisect](#how-to-bisect-a-break)
if the symptom is not listed.

| What you noticed | Section |
| --- | --- |
| App store empty, thumbnails missing | [1](#1-the-app-store-is-empty-or-thumbnails-are-missing) |
| Apps will not install or update | [2](#2-apps-will-not-install-or-update) |
| Firmware updates fail | [3](#3-firmware-updates-fail) |
| TV guide, TV Plus or a channel list gone | [4](#4-the-tv-guide-tv-plus-or-a-channel-list-disappeared) |
| Casting stopped working | [5](#5-casting-stopped-working) |
| Clock wrong, then apps stop playing | [6](#6-the-clock-is-wrong-and-then-apps-stop-playing) |
| An app refuses to sign in | [7](#7-an-app-refuses-to-sign-in) |
| TV claims it has no internet connection | [8](#8-the-tv-says-it-has-no-internet-connection) |
| Voice search or the assistant stopped answering | [9](#9-voice-search-or-the-assistant-stopped-answering) |
| Settings menu broken, or the TV will not boot | [10](#10-the-settings-menu-is-broken-or-the-tv-will-not-boot) |

Entries marked *notes* come from [our research notes](../RESEARCH-NOTES.md), where the original source
for each is recorded.

## 1. The app store is empty, or thumbnails are missing

| Host | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `ngfts.lge.com` | LG | Content Store thumbnails | notes |
| `lgtvsdp.com` | LG | Content Store | notes |
| `us.lgtvsdp.com` | LG | Content Store | [Perflyst issue 117](https://github.com/Perflyst/PiHoleBlocklist) |
| `lgappstv.com` | LG | Content Store | notes |
| `infolink.pavv.co.kr` | Samsung | App store and login | notes |
| `lcprd1.samsungcloudsolution.net` | Samsung | Smart Hub | notes |
| `osb-ussvc.samsungqbe.com` | Samsung | TV Plus | notes |
| `mas-ext.amazon.com` | Amazon | App installs | notes |
| `play.google.com` | Google | The Play Store | notes |
| `*.itunes.apple.com`, `*.apps.apple.com`, `*.mzstatic.com` | Apple | Store and artwork | notes |
| `api.vizio.com`, `images.vizio.com` | Vizio | SmartCast features | notes |

LG is the clearest example of why you cannot decide any of this from a second-level domain.
`smartshare.lgtvsdp.com` and `us.rdx2.lgtvsdp.com` are legitimate block targets. `lgtvsdp.com` and
`us.lgtvsdp.com` must stay. Same domain, opposite verdicts, one wildcard away from a broken TV.

## 2. Apps will not install or update

| Host | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `amazonadsi-a.akamaihd.net` | Amazon | Installs and updates | notes |
| `mas-ext.amazon.com` | Amazon | App installs | notes |
| `*.gvt1.com` | Google | App and system downloads | notes |
| `android.apis.google.com`, `*.googleapis.com` | Google | Broad platform functions | notes |
| `*.itunes.apple.com`, `*.apps.apple.com` | Apple | Installs | notes |

`amazonadsi-a.akamaihd.net` is the trap worth naming. The hostname contains "adsi", it appears on
"block Amazon ads" lists, and blocking it stops your apps updating.

## 3. Firmware updates fail

| Host | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `otnprd8` to `otnprd11.samsungcloudsolution.net`, `www.samsungotn.net`, `otn.samsungcloudcdn.com` | Samsung | Software updates | notes |
| `cdn.samsungcloudsolution.com` | Samsung | Update checks | notes |
| `softwareupdates.amazon.com` and its CloudFront hosts | Amazon | Updates | notes |
| `mesu`, `gdmf`, `gg`, `gs` `.apple.com` | Apple | Updates | notes |
| `ota.googlezip.net` | Google | Updates | notes |
| `update.biv.sony.tv` | Sony | Updates | notes |
| `api.us.hismarttv.com`, `api.euro.hismarttv.com`, `api.eu.hismarttv.com` | Hisense | May be needed for firmware updates | notes |
| `snu`, `su`, `su-ssl`, `nsu` `.lge.com` | LG | Updates | notes |

Some people block updates deliberately, and that is a defensible choice with an upstream precedent: the
webOS Homebrew Channel appends LG update servers to the hosts file when `webosbrew_block_updates` is
set. Two things to know before you copy it.

Blocking updates by DNS may not even work. LG has an over-the-air update fallback hardcoded at
`156.147.69.32:8080`, which never asks DNS, so a resolver cannot touch it. And update hosts carry
security fixes as well as features, so you are choosing to keep both out.

There is one case where blocking updates is mandatory rather than optional. If you are following the
Fire TV `kamakiri` root process, `amzdigitaldownloads.edgesuite.net`, `softwareupdates.amazon.com` and
`updates.amazon.com` have to be blocked during setup or the device force-updates past the vulnerable
build. That is the exception, not the pattern.

## 4. The TV guide, TV Plus or a channel list disappeared

| Host | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `osb-ussvc.samsungqbe.com` | Samsung | TV Plus | notes |
| `announcements.vizio.com` | Vizio | Perflyst explicitly declines to block it | [Perflyst](https://github.com/Perflyst/PiHoleBlocklist) |
| `api.vizio.com`, `images.vizio.com` | Vizio | SmartCast features | notes |

> **Unverified warning, and a loud one.** Gracenote supplies programme guide data to televisions, so a
> blocklist that includes Gracenote's hosts will kill the TV guide while looking like it only blocks
> content recognition. At least one circulating recognition blocklist is reported to include it.
>
> **This is not in our source material.** We cannot yet name the list, name the hosts, or point at a
> capture. It is here because losing your TV guide and not knowing why is a bad afternoon. If you can
> confirm it with a specific list and a specific hostname, that is a
> [bug report](../../../issues/new?template=bug_report.yml) we badly want.

Our notes carry no entry at all for **subtitles**. If subtitles stopped after you added a blocklist,
bisect it and tell us the hostname, because you would be the first.

## 5. Casting stopped working

If you added a blocklist and casting broke, check `multiscreen.samsung.com`, which is a never-block host
on Samsung sets.

If you moved the televisions onto their own VLAN and casting broke, that is not a blocklist problem and
unblocking things will not fix it.

**The mechanism.** Multicast DNS, which is how phones and laptops discover a TV to cast to, is
link-local. It does not cross a router boundary by design. Put the TV on a different VLAN from the phone
and the discovery packets never arrive. The TV is reachable, the app just cannot find it.

**The fix, and its cost.** An mDNS reflector forwards those announcements across the boundary, which
restores casting. It also partially undoes the isolation you built the VLAN for. That matters more here
than in most networks, because LG sets enumerate the devices on the local network, so a reflector hands
back the reconnaissance surface the VLAN removed.

There is no clean answer. Decide which you care about more, and know which one you chose.

## 6. The clock is wrong, and then apps stop playing

| Host | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `time.samsungcloudsolution.com` | Samsung | **Plex, YouTube and Prime Video** | notes |
| `ftv-smp.ntp-fireos.com`, `2.android.pool.ntp.org` | Amazon | Time sync | notes |
| `time.google.com` | Google | Time sync | notes |
| `vizio.pool.ntp.org` | Vizio | Time sync, and the set uses this host regardless of settings | notes |

The Samsung row is the one to remember. Blocking one time server breaks video playback in three
unrelated applications. Our notes record that consequence but not the mechanism, and the most likely
explanation is that a wrong clock invalidates TLS certificates, which is how every streaming app talks to
its servers.

Time hosts look harmless on a blocklist review. They are not.

## 7. An app refuses to sign in

| Host or package | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `auth.samsungosp.com` | Samsung | Account authentication | notes |
| `infolink.pavv.co.kr` | Samsung | App store and login | notes |
| `ns11.whois.co.kr` | Samsung | Series 7 sets cannot open YouTube | notes |
| `albert.apple.com` | Apple | Device activation | notes |
| `ocsp`, `certs`, `valid` `.apple.com` | Apple | Certificate validation | notes |
| `*.push.apple.com` | Apple | Push notifications | notes |
| `api.sr.roku.com` | Roku | One of only two destinations PETS 2021 classified as required | [PETS 2021](https://arxiv.org/abs/2105.05162) |
| `api.amazon.com`, `unagi-eu.amazon.com` | Amazon | Classified as required | [PETS 2021](https://arxiv.org/abs/2105.05162) |
| `applicast.ga.sony.net`, `portal.store.sonyentertainmentnetwork.com` | Sony | Platform services | notes |
| `com.amazon.identity.auth.device.authorization` | Amazon | Amazon logins **and Netflix** | [firestick-loader](https://github.com/esc0rtd3w/firestick-loader/blob/master/scripts/debloat/bloat-disable-noroot.sh) |
| `com.amazon.imp`, `com.amazon.tv.oobe` | Amazon | Applications and sign-in on Fire OS 5.2.6.3 | [Fire-Tools](https://github.com/mrhaydendp/Fire-Tools/blob/main/Fire-Tools/Debloat.txt) |

`api.amazon.com` appears on **both** the required and the non-required lists in PETS 2021, because it
multiplexes several services onto one hostname. You cannot decide that host from its name, and neither
could the researchers.

## 8. The TV says it has no internet connection

Usually this is how you answered, not what you blocked.

**Prefer NXDOMAIN over SERVFAIL, and REJECT over DROP.** Some firmware reads a SERVFAIL, or a connection
that is silently dropped, as "there is no internet" and then retries aggressively, which is worse for
your network than answering it. Configure your resolver to return NXDOMAIN for blocked names, and your
firewall to reject rather than drop.

Then check these are reachable:

| Host | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `connectivitycheck.android.com`, `connectivitycheck.gstatic.com` | Google | The connectivity check itself, so the TV concludes it is offline | notes |
| `cdn.samsungcloudsolution.com` | Samsung | Update checks | notes |

## 9. Voice search or the assistant stopped answering

| Host or package | Vendor | Blocking it breaks | Source |
| --- | --- | --- | --- |
| `lgsmartweb.com` | LG | Voice search | notes |
| `guzzoni.apple.com` | Apple | Siri | notes |
| Alexa endpoints | Amazon | Voice | notes |
| `com.google.android.katniss` | Google | Essential to the launcher, not only to voice | [sony-google-tv-debloat](https://github.com/ironshadow786786-boop/sony-google-tv-debloat) |
| `com.google.android.tts` | Google, Sony | Documented boot loops on Sony Google TV | [sony-google-tv-debloat](https://github.com/ironshadow786786-boop/sony-google-tv-debloat) |

The opposite case is `samples.voice.cti.roku.com`, which is where Roku sends voice samples. Blocking
that is the intended outcome, not a break.

## 10. The Settings menu is broken, or the TV will not boot

This only happens at Tier 3, where you disable preinstalled packages. DNS filtering cannot cause it.

**Fire OS. Use `pm disable-user`, never `uninstall`.** And version-gate everything, because the metrics
packages are simultaneously the most valuable ones to kill and the most likely to break Settings on some
builds.

| Package | Breaks | Build | Source |
| --- | --- | --- | --- |
| `com.amazon.client.metrics`, `com.amazon.client.metrics.api`, `com.amazon.metrics.api` | The Settings UI | 5.2.6.3 | firestick-loader |
| `com.amazon.device.settings.sdk.internal.library` | Device and Application settings | | firestick-loader |
| `amazon.jackson19` | Display and Applications settings | 5.2.7.2 | Fire-Tools |
| `com.amazon.application.compatibility.enforcer` | Must stay enabled | 5.2.7.2 | Fire-Tools |

**Sony Google TV, documented boot loops.**

| Package | Breaks | Source |
| --- | --- | --- |
| `com.google.android.webview` | The entire user interface | sony-google-tv-debloat |
| `com.google.android.katniss` | The launcher | sony-google-tv-debloat |
| `com.sony.dtv.tvx` | The boot process | sony-google-tv-debloat |
| `com.google.android.tts` | Boot | sony-google-tv-debloat |
| `com.android.location.fused` | Boot | sony-google-tv-debloat |

> **`com.android.vpndialogs` is the one that cannot be undone in practice.** A widely shared Sony
> debloat one-liner removes it. It is the system VPN consent dialog, so with it gone
> `VpnService.prepare()` can never be granted on that device again, and no network observer, logger or
> on-device blocker will ever work on that television. Do not run a debloat script you have not read
> line by line.

**And the contradiction that should stop you trusting any cross-brand package list.**
`com.google.android.tvrecommendations` is the primary safe first removal in the
[TCL debloat optimizer](https://github.com/livvaa/TCL-Google-TV-Debloat-Optimizer) and is listed under
"will cause a boot loop if removed" in the Sony guide. Both are probably correct for their own hardware.
That is why [our package data](../data/packages/) is scoped per model and why you should not paste a
list from a different brand.

One correction while you are here. `com.google.android.tungsten.setupwraith` is **not** a telemetry
package, despite appearing on debloat lists. It is the Android TV Setup Wizard and fallback launcher. It
only needs disabling if you have already disabled `com.google.android.apps.tv.launcherx` and want a
third-party launcher to stick, because otherwise it re-enables the default
([FLauncher](https://github.com/osrosal/flauncher)). Known side effect of disabling the default
launcher on Chromecast with Google TV: the YouTube button on the remote stops working.

## The general rules

**Never wildcard a vendor's whole domain.** Every vendor mixes telemetry and load-bearing services under
the same second-level name. `lgtvsdp.com` has hosts on both of our lists.
`samsungcloudsolution.com` and `.net` carry both a time server you must keep and a device log endpoint
you should block. `api.amazon.com` is required and non-required at once. Use targeted patterns:
`(^|\.)lgsmartad\.com` reaches roughly 159 LG ad hosts and their 163 mirrors without touching anything
else, and `(\.|^)tvinteractive\.tv$` covers Vizio's Inscape hosts.

**Even a targeted pattern needs checking against the never-block list.** Our own notes contain a live
example. The suggested Hisense pattern is `^api\..*\.hismarttv\.com$`, and the hosts that may be needed
for firmware updates are `api.us.hismarttv.com`, `api.euro.hismarttv.com` and `api.eu.hismarttv.com`,
which all match it. That pattern needs an exclusion, and if you copy it as-is you may stop getting
firmware updates.

**Time synchronisation breaks more than people expect.** See section 6. One Samsung time host takes out
three video apps.

**Update and authentication hosts are load-bearing. Content recognition hosts are usually not.** This is
the most useful asymmetry on the page, and it has measurements behind it. PETS 2021 classified only
`api.sr.roku.com` and `youtube.com` as required on a Roku, with `configsvc.cs.roku.com`,
`cooper.logs.roku.com`, `scribe.logs.roku.com` and `partnerad.l.doubleclick.net` all non-required. Fire
TV had 11 non-required destinations, the highest of any device tested. And IMC 2024 found that opting
out removed all traffic to every recognition domain, on sets that carried on working.

So the recognition and logging endpoints are the safe part. The risk is concentrated in updates, auth,
time and the app store.

**Gate by version and by model, always.** Fire OS package behaviour differs between 5.2.6.3 and 5.2.7.2.
Sony and TCL disagree about the same Android package. A guide that does not name the firmware it was
tested on is a guess.

## Vendors with no never-block data yet

We have no never-block entries at all for **Panasonic** or **Philips**, and this page does not pretend
otherwise.

Route by platform instead, because these brands ship other people's software. Several current Panasonic
flagships have Fire TV built in, so the Amazon rows above apply. Older EU Panasonic sets run My Home
Screen, for which we found no path of any kind. Philips ships Titan OS on many current EU sets, Android
TV on others, Saphi on older ones, and Roku TV on some, so the applicable rows depend entirely on which
one you have. Titan OS is business-gated and we found no consumer developer mode, which is recorded as
unverified rather than as a dead end.

If you own either brand and something broke, the hostname you found is genuinely new information. Send
it as a [bug report](../../../issues/new?template=bug_report.yml) or a
[guide request](../../../issues/new?template=guide_request.yml).

## How to bisect a break

Four steps. Do not skip the first one.

1. **Re-enable everything.** Turn the whole blocklist off and confirm the symptom goes away. If it does
   not, the filter was never the cause and you are about to waste an hour.
2. **Add back a quarter of the list.** Not one entry at a time. Quarters get you to the answer in about
   four rounds instead of four hundred.
3. **Test the specific broken feature, not "does the TV work".** Open the app store, cast something,
   check the clock, sign out and sign in. Power-cycle the TV between rounds, because most of its DNS
   requests fire in the first seconds after it comes up, so a TV that has been on for an hour will not
   re-ask for the host you just unblocked.
4. **Halve again until you have the entry.** Then check it against the tables on this page and against
   `data/endpoints/`.

When you find it, send it in. A [bug report](../../../issues/new?template=bug_report.yml) with the
hostname, the model, the firmware version and the feature that broke is the highest-value contribution
to this project, because the `breaks` field in our data matters more than the domain list itself.
