---
title: ISP and carrier gateways
updated: 2026-09-08
---

# ISP and carrier gateways

Most guides on this subject assume you own a router you can configure. Most people do not. They have
the box the internet company shipped, and that box frequently:

- does not expose DHCP option 6, so you cannot advertise your own resolver;
- does not allow LAN-side port forwarding, so you cannot redirect port 53;
- does not let you disable its DHCP server, so you cannot replace it in place;
- hides the DNS fields behind a firmware build the support line will not discuss.

That combination removes techniques 1, 2 and 3 from the [Router enforcement](../router-enforcement.md)
page in one go. This page is the decision tree for what is left, worked in order of cost. Answer each
question, and stop at the first yes.

One thing to clear away first. **Carrier-grade NAT is irrelevant here.** It dominates forum threads
about carrier gateways and it has nothing to do with outbound DNS interception. If someone tells you
CGNAT is why you cannot filter your television, they are wrong.

| Question | If yes | Cost | What you get |
| --- | --- | --- | --- |
| Can you set the gateway's upstream DNS? | [Branch A](#branch-a-set-the-gateways-upstream-dns) | 5 min, no hardware | Whole-house filtering for every device that honours the lease |
| Can you put the gateway in bridge mode? | [Branch B](#branch-b-bridge-mode) | One router, an afternoon | Everything on the enforcement page |
| Can you put your own router behind it? | [Branch C](#branch-c-double-nat) | One router, an hour | Everything, for the devices you move across |
| Does the device have its own DNS field? | [Branch D](#branch-d-per-device-dns) | 5 min per device | One device, if it honours the setting |
| None of the above | [Branch E](#branch-e-when-the-answer-is-no) | | Tier 0 in the TV's own menus, and that is it |

## Branch A: set the gateway's upstream DNS

This is the cheapest whole-house win available and it needs no hardware. If the gateway's admin page
has a WAN DNS or upstream DNS field, point it at a filtered hosted resolver. Every device that takes
its resolver from the gateway then gets filtered answers.

**What breaks:** nothing structural. If the hosted resolver goes down or you exceed a quota, you get
the failure mode of that provider, which is the next paragraph.

**To undo:** set the field back to automatic, or to your ISP's own resolvers, and reboot the gateway.

### Which hosted resolver

| Resolver | Free tier | Watch out for |
| --- | --- | --- |
| [NextDNS](../resolvers/nextdns.md) | 300,000 queries a month | **It fails open past the cap.** Queries are answered normally instead of filtered, so you look protected and are not. Check your usage counter before you trust it |
| AdGuard public DNS | `94.140.14.14` and `94.140.15.15` | No per-device policy and no query log you control |
| ControlD | Free resolvers keep no individual logs | No API or log streaming without a paid plan, so no report data |

**Two resolvers that do not solve this problem.** Quad9 and Cloudflare for Families block malware. They
do not block advertising or telemetry, so pointing your gateway at either changes nothing about what
your television reports. **Mullvad DNS is scheduled for discontinuation on 2 November 2026**, so do not
build on it.

If you want to contribute a device report later, NextDNS is the only entry in that table with a log you
can export, and its free tier is the one with the fail-open trap. Read
[the NextDNS page](../resolvers/nextdns.md) before you commit.

### The limit you must understand before relying on Branch A

Setting the gateway's upstream DNS only filters devices that ask the gateway. A television that dials
`8.8.8.8` directly walks straight past it, and **68% of smart TVs measured in 200-plus homes did
exactly that** ([Mazhar and Shafiq, IoTDI 2020][iotdi] §IV-C). Chromecast before Google TV hardcodes
`8.8.8.8` and `8.8.4.4` and has no DNS interface at all.

So Branch A is a genuine improvement for your phones, laptops and roughly a third of televisions, and
it is not enforcement. Without a port 53 redirect there is nothing making the other two-thirds comply.
Do it anyway, because it takes five minutes, and then decide whether Branch B or C is worth it.

## Branch B: bridge mode

If the gateway can be put into bridge mode, it stops routing and becomes a modem, and a router you
control does the work. This gives you everything on the enforcement page with none of the compromises
below it.

Go to [OpenWrt](openwrt.md) or [pfSense and OPNsense](pfsense-opnsense.md) and follow that page
instead. Bridge mode is the end of your involvement with this file.

**What breaks:** any service the gateway itself provides. Carrier-supplied telephony and IPTV often ride
on the gateway's routing, and bridge mode can kill both. Some carriers require the gateway to remain in
router mode for provisioning. Check what your line includes before you switch.

**To undo:** turn bridge mode off. Expect to re-run the gateway's setup wizard.

**Our research notes record no per-carrier bridge mode paths**, and there are too many firmware
variants to guess at. Check your exact model's manual or ask your provider. If you work out the path
for a common gateway, [that is a useful contribution](../../CONTRIBUTING.md).

## Branch C: double NAT

Plug your own router's WAN port into a LAN port on the gateway, give your router its own subnet, and
move the devices you care about onto your router's network. The gateway keeps doing whatever it insists
on doing, and your router enforces the rules for everything behind it.

This works. Double NAT is the thing people are warned about in general networking advice, and the
warning does not apply to this project, because **nothing here needs inbound reachability**. You are
not hosting a game server or forwarding a port. You are intercepting outbound port 53 and rejecting
outbound 853, and both work identically behind two layers of NAT.

What you get behind your own router is the full set: DHCP option 6, the port 53 redirect with its
self-exclusion and its IPv6 twin, the 853 reject, and per-client query attribution in your resolver's
log. That last one is what makes a device report possible.

**What breaks:** anything that needs the television and a controller on the same subnet. Casting,
screen mirroring, phone-as-remote apps, and smart home integrations all break across the boundary. The
answer to that is a multicast DNS reflector, and a reflector partially undoes the isolation, because LG
sets enumerate LAN devices and a reflector hands that surface back.
[Router enforcement §6](../router-enforcement.md#6-vlan-isolation) covers the tradeoff.

**To undo:** move the device back to the gateway's Wi-Fi. Nothing on the television changes.

### Do not run two DHCP servers on one segment

If the gateway will not let you turn its DHCP server off, do not put a second DHCP server on the same
network segment and hope. Two servers racing to answer the same broadcast produces intermittent
failures that depend on which one replies first, and the symptoms move around for weeks.

Your own router's LAN is a different segment, so its DHCP server is fine there. That is the point of
Branch C. If you want the DHCP server and the filtering in one process,
[AdGuard Home has a built-in DHCP server](../resolvers/adguard-home.md#own-dhcp-option-6-without-touching-the-router),
which means you can own option 6 on your segment without any router configuration at all.

## Branch D: per-device DNS

If you cannot change the network, change the device. On-device DNS capability falls into three tiers,
and which tier you are in decides whether this branch is worth opening.

| Tier | Platforms | What you do |
| --- | --- | --- |
| DNS separate from IP | tvOS, Samsung Tizen | Set a DNS server and leave addressing on automatic |
| DNS only inside a full static IP form | Everything Android-derived, plus webOS, Vizio, VIDAA, Panasonic, Philips, Sharp, Toshiba | Pin an address, gateway and prefix by hand, then set DNS |
| No DNS setting at all | **Roku OS, every version, including Roku TVs. Chromecast before Google TV** | Nothing |

Exact menu paths per platform are on the vendor pages, since they move between firmware versions and
regions. Start at [Find your TV](../README.md).

**What breaks in the middle tier:** pinning a static address by hand is where households cause
themselves real trouble. Pick an address outside the gateway's DHCP pool or you get an address
conflict, and get the gateway and prefix length right or the set loses the internet. Write down what
was there before you changed it.

**To undo:** set addressing back to automatic on the device.

**Two warnings specific to this branch.** Some Fire OS builds silently ignore a custom Wi-Fi DNS
setting, so the field accepts your value and the device keeps using its own. Tizen OS 9 has a reported
bug where DNS reverts to Auto after you leave the IP Settings screen. In both cases the setting looks
applied and is not, which is why [Verify it works](../verify-it-works.md) matters more on this branch
than anywhere else.

## Branch E: when the answer is no

Some readers reach this line with nothing left. That is the honest outcome and it is better to say so
than to pad the page.

If your gateway has no upstream DNS field, no bridge mode, no usable LAN port, and your device is a
Roku or a pre-Google-TV Chromecast, then **there is no network-level fix available to you.** Not a
harder one. None. The device has no DNS field, your gateway has no interception, and every remaining
technique on the enforcement page needs one or the other.

What you can still do:

1. **Tier 0, in the television's own menus.** This is not a consolation prize. A 2024 study of Samsung
   and LG sets found that after opting out, traffic to every content recognition domain the researchers
   had identified stopped completely, and no new ones appeared ([Anselmi et al., IMC 2024][imc24]). The
   menus work. Start at [Find your TV](../README.md).
2. **Do not connect the device.** A television used as an HDMI display with no network cannot report
   anything. Content recognition has been observed running on HDMI input on sets that are online, so
   if the set does not need the internet, this is the complete fix rather than a partial one. It costs
   you the built-in apps, which is a real cost if that is how you watch things.
3. **Use a streaming device you can control instead**, and leave the television offline. That moves the
   problem to hardware where Branch D applies.
4. **Buy a cheap router for Branch C when you next can.** Branch C needs one router and an hour, and it
   turns a no into a yes permanently.

If your carrier gateway does expose something we have said it does not, we have the wrong model of your
hardware. [Tell us which gateway](../../CONTRIBUTING.md) and this page gets better for the next person
with that box.

## Sources

- [Mazhar and Shafiq, IoTDI 2020][iotdi] §IV-C, for the 68% figure and the 46% figure for games
  consoles.
- [Anselmi et al., IMC 2024][imc24], for opt-out being effective.
- [RFC 2132][rfc2132] §3.8, the DHCP option this page is mostly about not having.

[iotdi]: https://arxiv.org/abs/2001.08288
[imc24]: https://arxiv.org/html/2409.06203v1
[rfc2132]: https://www.rfc-editor.org/rfc/rfc2132.html
