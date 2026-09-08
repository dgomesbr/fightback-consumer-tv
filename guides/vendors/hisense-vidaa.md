---
title: Hisense (VIDAA)
platform: vidaa
brands: [Hisense, Toshiba (some regions)]
generations: "VIDAA 6 and VIDAA 7. Earlier VIDAA versions not separately documented."
dns_field: static-ip-required
dev_mode: no
adb: no
package_disable: no
root: none
max_tier: 2
updated: 2026-09-08
---

# Hisense (VIDAA)

VIDAA is Hisense's own operating system, and it also ships on Toshiba sets in some regions [8]. Do not
use the web browser on this television. The same privileged JavaScript bridge that lets researchers
sideload apps onto a VIDAA set also lets any web page the TV's browser visits install an application
with no notification and read files off the TV, including the Wi-Fi configuration [2]. That is a Tier 0
action, it needs no tools, and it is the most valuable thing on this page.

Check you are in the right guide first. Hisense also sells Google TV and Roku TV models under the same
brand [8]. Look under Settings > About. If it says Google TV or Android TV, read
[google-android-tv](google-android-tv.md). If the home screen is Roku's, read [roku](roku.md), and note
that Roku TVs have no DNS field at all.

**Covers:** Hisense televisions running VIDAA 6 and VIDAA 7
**Also sold as:** Toshiba in some regions [8]
**How far you can get:** Tier 2, and Tier 2 is fragile. The practical ceiling is Tier 1 at the router.

## What this device sends home

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
| Device and account telemetry | `api-gps-em.hismarttv.com` | Thousands of connections a day | [7][9] |
| Auth, messaging and launcher telemetry | `auth-em`, `msg-em`, `api-launcher-em`, `auth-launcher-em` under `.hismarttv.com`, plus the `-na` equivalents and `unified-ter-na` | Not yet documented. See Open questions. | [7][9] |
| Audio for content recognition | Not yet documented. Hisense's US privacy policy admits the collection without naming an endpoint | Not yet documented. See Open questions. | [7] |

The regional collectors are matched with
`^(api-gps|auth|msg|api-launcher|auth-launcher|unified-ter)-(em|na)\.hismarttv\.com$` [10]. That regex
enumerates the collector prefixes on purpose, because the `api.us`, `api.euro` and `api.eu` hosts under
the same domain may carry firmware updates and sit on the never-block list below. A lazier pattern such
as `^api\..*\.hismarttv\.com$`, which our earlier research notes suggested [7], catches all three of
them.

`api-gps-em` connecting thousands of times a day is the number to keep in mind when someone tells you
smart TV telemetry is occasional [9].

### The browser is the real vulnerability

Independent research documented two primitives exposed to pages loaded in the VIDAA browser [2]:

- `Hisense_installApp()` silently installs an HTML5 application with no user notification.
- A custom `File.read()` accepts `../` path traversal. The researcher used it to read Netflix
  preferences, the Wi-Fi configuration and `/etc/passwd`.

There is no setting that turns this off. A hostile or compromised page reaches both functions the moment
you load it. This is also the mechanism the sideloading project in Tier 2 depends on, which is why that
tier carries a warning instead of a recommendation.

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

**What this breaks:** nothing we have documented. Personalised Ads changes which ads you see, not
whether the TV works.

### Stop using the web browser

Do not open the browser app. If you have used it, assume any page you visited could have installed an
application and read your Wi-Fi configuration [2]. Check the installed app list for anything you did not
put there.

If you want a browser on the television, use a streaming stick with its own browser so the TV's
privileged bridge is never involved. At the router you can reduce the damage without touching the TV,
because a resolver that filters for the whole network filters the TV's browser too. That is the only
enforcement point available, since VIDAA gives you no way to remove or disable the browser [7].

### Turn off content recognition

Not yet documented. See Open questions.

Hisense's US privacy policy admits that it collects audio for content recognition, and gives no menu
path for switching that off [7]. One community guide lists "Settings > System > Privacy > Viewing
Information Services", but that wording is Samsung's, so we treat it as **UNVERIFIED** and will not
publish it as a path [7].

| Generation | Path | Status |
| --- | --- | --- |
| VIDAA 6, VIDAA 7 | Not yet documented | Open question |

### Turn off ad tracking and personalisation

| Generation | Path | Status |
| --- | --- | --- |
| VIDAA 6, VIDAA 7 | Settings > System > Advanced Settings > Personalised Ads | ⚠️ needs-confirmation |

### Other settings worth changing

Not yet documented. See Open questions. We have no sourced path for the microphone, voice services or
automatic updates on VIDAA.

**What this does not fix:** the browser primitives, which have no toggle [2], the content recognition
audio collection, which has no documented toggle either [7], and the telemetry to `.hismarttv.com`, which
is Tier 1 work. Opting out has been measured as effective on Samsung and LG sets [3], never on a Hisense.

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

### On the device

VIDAA has DNS fields, bundled with a full static IP. Once you turn DHCP off you own the address for that
TV, and an address collision months later presents as "the TV stopped working" [7].

| Path | Status |
| --- | --- |
| Settings > Network > Network Configuration > Advanced Settings > IP Settings, set IP Setting Mode to Manual, then DNS Server 1 and DNS Server 2 | ⚠️ needs-confirmation |

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform: hand the resolver
out with DHCP option 6, redirect outbound TCP and UDP port 53 to it, and reject port 853. Mirror every
rule on IPv6, because a Router Advertisement can hand the TV a resolver through RFC 8106 with no DHCP
involved [7]. 68% of the smart TVs in a 200-plus-home study reached Google Public DNS directly instead of
the resolver they were handed [6], and nobody has published a per-brand breakdown, so assume a Hisense is
in that 68% and enforce it.

### What to block

The endpoint set lives in [`data/endpoints/hisense.yml`](../../data/endpoints/hisense.yml) with a
breakage flag per entry, rather than being duplicated here. It is the collector regex above plus four
never-block entries.

HaGeZi publishes no Hisense list [4], so this vendor is another genuine gap and the list in this repo is
built from Perflyst [9] and FTPrivacy [10].

Generated lists: [`blocklists/fightback-tv-hisense.txt`](../../blocklists/)

### What never to block

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
| `api.us.hismarttv.com` | May be required for software and firmware updates | [9][10] |
| `api.euro.hismarttv.com` | May be required for software and firmware updates | [9][10] |
| `api.eu.hismarttv.com` | May be required for software and firmware updates | [9][10] |
| `*.vidaahub.com` | The app store stops working | [1][10] |

"May be required" is doing real work in that table, because nobody has tested a firmware update with
those hosts blocked, and that is an Open question. Allowlist all four explicitly rather than relying on
regex ordering, or your TV stops getting security updates and you will not notice for a year.

`vidaahub.com` is the domain the Tier 2 sideloading method redirects [1]. Blocking it and redirecting it
are different operations, and doing both at once gets you neither an app store nor a sideload.

### Hardcoded addresses

None documented for VIDAA. If you capture a Hisense dialling a bare IP address, that belongs in
`data/hardcoded/hisense.yml`.

## Tier 2: developer mode and sideloading

**Time:** several hours, most of it setting up infrastructure. **Risk:** low to the TV, moderate to
your patience. **Reversible:** yes. **Warranty:** unclear. This is not an official vendor feature.

Hisense ships no developer mode. What exists instead is [`weinzii/vidaa-edge`](https://github.com/weinzii/vidaa-edge),
which points the hostname `vidaahub.com` at a host you control, has you open that address in the TV's
browser, and uses the privileged JavaScript bridge to install a progressive web app [1]. The underlying
research is documented at [bananamafia.dev](https://bananamafia.dev/post/hisensehax/) [2].

There is no vendor-sanctioned door here. The technique impersonates a Hisense domain and then calls
`Hisense_installApp()`, the same function a hostile web page calls. The hole is already open and you are
walking through it deliberately.

**Before you spend an evening on this, four warnings.**

1. It is firmware-dependent. The bridge function names and the behaviour of the browser change between
   VIDAA builds, and nothing guarantees your set matches the one the project was built against [1].
2. It requires running your own DNS server so you can answer for `vidaahub.com` [1]. If you are willing
   to do that, you have already built the machine that Tier 1 asks for, and Tier 1 gives you filtering
   for every device in the house. Do Tier 1 first and treat this as a bonus.
3. It gets you a sandboxed web application. It does not get you a shell, a package manager or the
   ability to disable the ad service, so it does not unlock Tier 3.
4. A firmware update can close it at any time, and no upgrade path is promised.

We link this project because it exists, it is honest about what it does, and readers deserve to know the
option is there. We do not recommend it as a privacy measure. Tier 1 achieves more with less.

## Tier 3: disable preinstalled advertising and metrics apps

Not possible. VIDAA exposes no ADB, no shell and no package manager, and the Tier 2 sideload runs in the
browser sandbox rather than giving you system access [1][7].

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

No public root or custom firmware project exists for VIDAA [7]. The `../` traversal in the browser
bridge reads files, and reading `/etc/passwd` is not root [2]. Nobody has published a privilege
escalation from that primitive to a persistent shell.

What does exist is [epk2extract](https://github.com/throwaway96/epk2extract), which extracts firmware
images for LG, Hisense, Sharp, Philips and Thompson [5]. That is analysis, not modification. It is how
you prove a set ships a named content recognition binary instead of asserting it, and it runs on your
computer rather than on the television, so it carries none of the risk in this tier.

**What root gets you:** unknown, because nobody has it.
**What it costs you:** unknown for the same reason.
**Where to go:** nowhere yet. See [LEGAL.md](../../LEGAL.md) for why we would link rather than
reproduce, if a project appeared.

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 | The web browser, because you have decided to stop using it | Nothing to undo |
| 1 | Firmware updates, if you block `api.us`, `api.euro` or `api.eu` `.hismarttv.com`. The app store, if you block `vidaahub.com` | Allowlist those four hosts and reboot the TV |
| 2 | The app store, because `vidaahub.com` now answers with your host instead of Hisense's | Remove the DNS override |
| 3 | Not applicable | |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is counting
`api-gps-em.hismarttv.com` in your resolver's query log over 24 hours. It should be in the thousands
before you filter and zero afterwards [7].

Start the capture before the TV boots. Most DNS requests fire in the first seconds after activation, and
a late start loses the hostname-to-address mapping for the session [7].

## Open questions

Answer any of these with a Hisense in front of you and it is a direct contribution. Use the
[device report form](https://github.com/dgomesbr/fightback-consumer-tv/issues/new?template=device_report.yml).

- Where is the content recognition toggle on VIDAA 6 and VIDAA 7, if it exists at all? Hisense's own
  privacy policy admits the audio collection without giving a path [7].
- Is "Settings > System > Privacy > Viewing Information Services" real on VIDAA, or is that guide
  copying Samsung's wording? [7]
- Does the Personalised Ads toggle stop any traffic, or only change ad selection? The equivalent has
  been measured on Samsung and LG [3] and never here.
- Which endpoint carries the content recognition audio? None of the known `.hismarttv.com` hosts has
  been attributed to it [7].
- Do firmware updates actually fail with `api.us.hismarttv.com` blocked? The never-block entry says
  "may be required" and nobody has tested it [9].
- Does a VIDAA set honour DHCP option 6, or does it reach a resolver of its own?
- Is `Hisense_installApp()` still reachable on current VIDAA 7 firmware, or has Hisense fixed it since
  the bananamafia write-up? [2]
- Does a VIDAA set keep sending telemetry when used as a plain HDMI display with no apps opened?

## Sources

1. [weinzii/vidaa-edge](https://github.com/weinzii/vidaa-edge). Sideloading by pointing `vidaahub.com`
   at your own host.
2. [bananamafia.dev, Hisense hax](https://bananamafia.dev/post/hisensehax/). `Hisense_installApp()`
   silent install, and `File.read()` with `../` traversal reaching Netflix preferences, Wi-Fi
   configuration and `/etc/passwd`.
3. Anselmi et al., IMC 2024, [Watching TV with the Second-Party: A First Look at Automatic Content
   Recognition Tracking in Smart TVs](https://arxiv.org/html/2409.06203v1). Opt-out verified effective
   on Samsung and LG.
4. HaGeZi, [dns-blocklists](https://github.com/hagezi/dns-blocklists). GPL-3.0. No Hisense list exists.
5. [epk2extract](https://github.com/throwaway96/epk2extract). Firmware extraction for LG, Hisense,
   Sharp, Philips and Thompson.
6. Mazhar and Shafiq, IoTDI 2020, [Characterizing Smart Home IoT Traffic in the
   Wild](https://arxiv.org/abs/2001.08288) §IV-C.
7. [Project research notes](../../RESEARCH-NOTES.md), Hisense VIDAA section and cross-cutting facts,
   gathered 8 September 2026.
8. [Project research notes](../../RESEARCH-NOTES.md), "Which OS is it" table.
9. Perflyst, [PiHoleBlocklist SmartTV.txt](https://github.com/Perflyst/PiHoleBlocklist/blob/master/SmartTV.txt).
   MIT, stale since 13 July 2023. Source of the collector hostnames, the `api-gps-em` connection count and
   the never-block entries.
10. Project endpoint data, [`data/endpoints/hisense.yml`](../../data/endpoints/hisense.yml), where each
    entry carries its own upstream source.
