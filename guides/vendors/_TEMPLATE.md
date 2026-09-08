---
title: <Brand> (<Platform>)
platform: <webos|tizen|roku|fire-os|google-tv|android-tv|vidaa|smartcast|tvos|other>
brands: [<Brand>, <other brands using this platform>]
generations: "<year range and OS versions covered>"
dns_field: <standalone|static-ip-required|none>
dev_mode: <yes|no>
adb: <yes|no>
package_disable: <yes|no>
root: <available|patched|none>
max_tier: <0|1|2|3|4>
updated: 2026-09-08
---

# <Brand> (<Platform>)

<!--
One paragraph. What this platform is, which brands ship it, and the single most important thing the
reader should know. If the honest answer is "you cannot fix this on the device, go to the router
guide", say that here in the first three lines rather than making them read to the bottom.
-->

**Covers:** <models and years>
**Also sold as:** <other brands>
**How far you can get:** Tier <N>. <One line on why.>

## What this device sends home

<!--
Facts with citations. Cadence if known. No adjectives. A table beats prose here.
Every row needs a source. Mark anything unsourced as UNVERIFIED.
-->

| What | Where it goes | How often | Source |
| --- | --- | --- | --- |
|  |  |  |  |

<!--
If there is peer-reviewed or press evidence specific to this platform, summarise it in two or three
sentences with the link. This is what makes the page credible to a sceptical reader.
-->

## Tier 0: settings only

**Time:** about 5 minutes. **Risk:** none. **Reversible:** yes.

<!--
The highest value section on the page. Most readers stop here, so it has to be complete.

Give the exact words on screen, in menu order, per generation. Mark every path:
  ✅ verified   confirmed on real hardware, name the model and firmware
  ⚠️ needs-confirmation   from vendor docs or a secondary source, nobody has checked it

The 2024 IMC study found opting out genuinely stops content recognition traffic, so lead with the
content recognition toggle rather than burying it among the ad settings.
-->

### Turn off content recognition

| Generation | Path | Status |
| --- | --- | --- |
|  |  |  |

### Turn off ad tracking and personalisation

| Generation | Path | Status |
| --- | --- | --- |
|  |  |  |

### Other settings worth changing

<!-- Microphone, voice, local network access, mobile device access, automatic updates. -->

**What this does not fix:** <Be specific. If the device hardcodes a resolver, say so with the
citation, and link to Tier 1.>

## Tier 1: DNS

**Time:** 30 minutes at the router. **Risk:** none to the TV. **Reversible:** yes.

<!--
Two questions, answered plainly:
  1. Does this device have a DNS field, and is it standalone or does it need a full static IP?
  2. Does it honour the DNS server the router hands it, or does it hardcode its own?

If it hardcodes, on-device DNS is theatre and the reader must go to the router. Say so.
-->

### On the device

<!-- Exact path, or "there is no DNS setting on this platform". -->

### At the router

Read [Why do it at the router](../why-dns.md) and
[Router enforcement](../router-enforcement.md). The short version for this platform:
<one or two sentences>

### What to block

<!-- Reference data/endpoints/<vendor>.yml rather than duplicating the list here. -->

Generated lists: [`blocklists/fightback-tv-<vendor>.txt`](../../blocklists/)

### What never to block

<!--
As important as the blocklist. Every entry needs a source and a consequence.
-->

| Domain | Blocking it breaks | Source |
| --- | --- | --- |
|  |  |  |

### Hardcoded addresses

<!--
Any IP:port the device dials without a DNS lookup. DNS filtering cannot touch these, only a firewall
rule can. See data/hardcoded/<vendor>.yml. Omit the section if none are known.
-->

## Tier 2: developer mode and sideloading

**Time:** 1 hour. **Risk:** low. **Reversible:** yes. **Warranty:** unaffected, this is an official
vendor feature.

<!--
Omit this whole section if the platform has no developer mode, and say so in one line instead.

Cover: how to enable it, what it lets you do, what it does NOT let you do, and the expiry traps.
Session and certificate expiry is the thing that surprises people, so put it in a callout, not a
footnote.
-->

## Tier 3: disable preinstalled advertising and metrics apps

**Time:** 1 hour. **Risk:** medium, a wrong package can stop the TV booting.
**Reversible:** yes, by re-enabling or factory reset.

<!--
Omit if the platform does not allow it.

Package safety is per model. Community lists contradict each other: the same package is a safe first
removal in one guide and a documented boot loop in another. So every package here is scoped to the
models it was tested on, and comes from data/packages/<platform>.yml.

Always include:
  - The do-not-disable table, with the documented consequence
  - The exact re-enable command
  - The factory reset recovery path
-->

### Safe to disable

### Do not disable

| Package | What breaks | Source |
| --- | --- | --- |
|  |  |  |

### Undoing it

## Tier 4: root and custom firmware

**Risk:** high. **Warranty:** void. **We do not publish the steps.**

<!--
Explain what root achieves on this platform, what it risks, and link to the upstream project. Do not
reproduce exploit steps, payloads, or firmware patching procedures. See LEGAL.md.

State plainly what root buys the reader in privacy terms, so they can judge whether it is worth it.
-->

**What root gets you:** <specific capabilities>
**What it costs you:** <specific risks, including firmware updates and bricking>
**Where to go:** <upstream project link>

## What breaks, by tier

| Tier | What stops working | How to undo it |
| --- | --- | --- |
| 0 |  |  |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

## Verify it worked

Do not assume a block is working because you configured it. Follow
[Verify it works](../verify-it-works.md). For this platform, the check that matters most is
<the one specific thing>.

## Open questions

<!--
Honesty section. What we do not know about this platform, so a reader with the hardware knows exactly
what would help. Link to the issue if one exists.
-->

## Sources

<!-- Numbered list of everything cited above. Prefer vendor docs, papers and upstream projects. -->
