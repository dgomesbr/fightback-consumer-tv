# Why do it at the router

**The switches on your TV stop what the vendor agreed to let you stop. The router covers the rest.**

This page exists so you can decide how much work to do before you do any of it. It compares the four
places you can filter a television, states what each one cannot reach, and ends with the four steps in
order of effort.

If you have not done the free part yet, do that first. [Start here](start-here.md) takes five minutes
and a 2024 study found it works completely for content recognition
([Anselmi et al., IMC 2024](https://arxiv.org/html/2409.06203v1)).

## The four places you can filter

| | Router-level resolver | On-TV DNS field | Public filtered DNS | On-device blocker |
| --- | --- | --- | --- | --- |
| **Coverage** | Every device on the LAN, including ones with no DNS setting | That one device, and only its DNS lookups | Whatever you point at it. Whole house from the router, one device from the TV | That one device, and on Android every app on it |
| **Beats a hardcoded resolver** | Yes, with a port 53 redirect. Handing out DHCP option 6 on its own does not | No. That is what "hardcoded" means | No on its own. Yes only if a router redirect forces traffic into it | Yes on Android. All traffic enters the tunnel |
| **Beats a hardcoded IP address** | No. Only a firewall rule reaches those | No | No | Sees them. No shipping tool in our sources is proven to block them on a TV |
| **Beats DNS-over-TLS** | Yes. Reject port 853 | No | No | Sees the flow. Blocking it is unproven in our sources |
| **Beats DNS-over-HTTPS** | Mostly. Blocklist of DoH hostnames and server IPs | No | No | No. Same 443 problem |
| **Ease for a normal person** | Half an hour, and you need the router's admin password | Easiest, except that every platform but Tizen and tvOS makes you pin a full static IP first | Highest. No hardware, nothing to keep running | Low. See the gotchas below |
| **Cost** | Free software, sometimes a small always-on machine | Free | Free tiers exist. NextDNS gives 300,000 queries a month | Free apps exist |
| **Per-device policy** | Yes, on every resolver we recommend | Per-device by construction, with no policy engine behind it | NextDNS yes. AdGuard public DNS no. ControlD free keeps no individual logs | Per-app, the finest granularity available |
| **Query logs you can analyse** | Yes, exportable, per client | Only if it points at your own resolver, which is the router option with extra steps | NextDNS 1 hour to 2 years, with a storage region choice and a resumable log stream. AdGuard public and ControlD free, effectively none | Best of the four. Per-app attribution and resolved hostnames |
| **How it fails** | Silently, when the device learns an IPv6 resolver you did not intercept, or when the redirect omits its self-exclusion and loops | Silently. Tizen OS 9 has a reported bug where DNS reverts to Auto after you leave IP Settings | NextDNS fails open past its free cap, answering normally instead of blocking, and nothing tells you | The platform has no VpnService at all, or a debloat script removed the system VPN consent dialog |
| **What it misses** | Hardcoded IP dials, DoH to endpoints not on your list, anything inside TLS | Roku has no field. Chromecast before Google TV has no field and hardcodes 8.8.8.8 and 8.8.4.4 | Everything the TV does not send there, which by measurement is most televisions | Every platform that is not Android or tvOS 17 and later |

## Reading the matrix

Three of those four columns depend on the television choosing to cooperate. Only the router column
works on a device that does not.

That is not a theoretical worry. Mazhar and Shafiq instrumented more than 200 homes and found **68% of
smart TVs and 46% of game consoles reached Google Public DNS directly**, ignoring the resolver their
router advertised ([IoTDI 2020](https://arxiv.org/abs/2001.08288) §IV-C). The widely repeated "72%"
figure is a mis-citation of that same paper, so if you see it quoted, the source is this study and the
number is 68.

The on-device blocker column is the strongest one technically and the narrowest one practically. On
Android TV a VpnService app is the only way a third-party tool sees another app's traffic, and it does
work on real hardware: a
[Blokada log from a Sony Android TV](https://github.com/blokadaorg/blokada/issues/134) shows it
blocking `googleads.g.doubleclick.net` and `securepubads.g.doubleclick.net`. Android's own
documentation is explicit that "if you don't create allowed or disallowed lists, the system sends all
network traffic through the VPN", so a hardcoded resolver does not help the TV.

What stops it being the recommendation is everything around it. Always-on VPN frequently has no UI on
Android TV, and the Nvidia Shield "does not have that option". Third-party VPN interfaces are often not
navigable with a D-pad. Only one VPN can be active at a time, so the tool fights with any commercial
VPN you already use. A VPN service on some older Sony firmware caused boot loops. And if you have
already run a popular Sony debloat script, it may have removed `com.android.vpndialogs`, the system VPN
consent dialog, after which `VpnService.prepare()` can never be granted on that device again and no
network observer will ever work on it.

Roku, Tizen, SmartCast, VIDAA and webOS have no equivalent at all. tvOS 17 has half of one: Apple's
documentation shows `NEPacketTunnelProvider`, `NEVPNManager` and `NETunnelProviderManager` available
from tvOS 17.0, which gives whole-device DNS and SNI visibility, but `NEDNSSettingsManager`,
`NEDNSProxyProvider`, `NEFilterDataProvider` and `NEAppProxyProvider` are all still unavailable. So no
per-app attribution, no content filtering, no system-wide DNS setting, and it needs the managed
entitlement.

## The recommendation ladder

Four steps. Stop at whichever one matches the effort you want to spend.

### Step 1. Free, five minutes, no hardware

Do the TV's own switches, then set your router's DHCP to hand out a filtered public resolver. AdGuard's
default addresses are `94.140.14.14` and `94.140.15.15`.

This reaches every device that honours the DNS server your router advertises, which by the numbers
above is roughly a third of televisions and a little over half of game consoles. It reaches your
phones and laptops too, which is most of the household's ad load.

### Step 2. Own the resolver, thirty minutes

Run AdGuard Home, Pi-hole or Blocky on your LAN and advertise it with DHCP option 6, defined in
[RFC 2132](https://www.rfc-editor.org/rfc/rfc2132.html) §3.8. On OpenWrt that is three commands:

```
uci add_list dhcp.lan.dhcp_option='6,192.168.1.2'
uci commit dhcp
service dnsmasq restart
```

Nothing is enforced yet. What you gain is per-client query logs, so you can see which of your devices
ignore you instead of guessing. Compare [the resolvers](choose-a-resolver.md) before you install one,
because the choice determines whether you can get the data out again.

### Step 3. Enforce it

Redirect TCP and UDP port 53 from the LAN to your resolver, excluding the resolver's own queries, and
reject port 853. Give both rules an IPv6 twin. Prefer NXDOMAIN over SERVFAIL for blocked answers and
REJECT over DROP for blocked connections, because some firmware reads a SERVFAIL or a silently dropped
connection as "no internet" and retries aggressively.

This is the step that survives a television which ignores DHCP. The recipes are on
[OpenWrt](routers/openwrt.md) and [pfSense and OPNsense](routers/pfsense-opnsense.md). The
self-exclusion is the part people forget, and omitting it causes a redirect loop that takes DNS down
for the whole house.

### Step 4. Close what is left

Add HaGeZi's DoH endpoint lists to your blocklists, 3,324 DoH hostnames or 16,372 including VPN and
proxy hosts, and its 1,451 DoH server IPs as a firewall alias. Add explicit firewall rules for the
hardcoded dials we know about, such as LG's `156.147.69.32:8080` and `54.186.247.229:443`. If you go as
far as putting televisions on their own VLAN, read [what breaks](what-breaks.md) first, because that
is the change that stops casting.

## The honest limits

### DHCP option 6 is advice, not instruction

The mechanism is boring. Option 6 is a field in a DHCP lease. The client reads it and is then free to
use whatever resolver it likes. There is no enforcement anywhere in the protocol, which is why 68% of
televisions in a 200-home study simply did not use it.

Known and suspected hardcoders, with their evidence quality:

| Device | Behaviour | Evidence |
| --- | --- | --- |
| Chromecast before Google TV | Hardcodes 8.8.8.8 and 8.8.4.4, and has no DNS UI at all | Documented |
| Roku | Reported to fall back to Google's resolvers since Roku OS 5.4 | Reddit, which we could not fetch. **Unverified** |
| Fire TV Stick | Widely reported to reach 8.8.8.8 regardless of DHCP | Anecdotal. **Unverified** |
| webOS | Some firmware said to hardcode 8.8.8.8 | Level1Techs wiki, a secondary source |

A claim circulates that Samsung and LG ship a specific hardcoded DoH bootstrap IP set. It comes from a
single site whose packet captures are unpublished and whose IP list is just the usual public
resolvers. We do not cite it, and we would rather you did not either.

### Hardcoded IP addresses are invisible to DNS filtering

No lookup means no filtering decision. There is nothing for a resolver to see.

Two documented examples, from a rooted LG OLED65G5WUA on the
[Level1Techs wiki](https://forum.level1techs.com/t/lg-tv-block-mini-how-to/255178): an over-the-air
update fallback to `156.147.69.32:8080` and live telemetry to `54.186.247.229:443`. Neither generates a
DNS query. No resolver, hosted or self-hosted, will ever log them. Only a firewall rule matching the
destination address and port stops them.

This is also why [verify-it-works](verify-it-works.md) asks you to capture on the WAN side and not just
the LAN side. A LAN-side DNS capture cannot show you a call that never asked a question.

### DNS-over-TLS is easy to stop. DNS-over-HTTPS is not.

DoT runs on its own port, 853. One reject rule ends it, and a client that cannot reach 853 falls back
to plain DNS on 53, which your redirect catches.

DoH is HTTPS on 443, and on the wire it looks like every other HTTPS connection. You cannot block the
protocol without blocking the web. What you can block is the endpoints, which makes it a list problem
rather than an enforcement problem. HaGeZi maintains that list: 3,324 DoH hostnames, 16,372 with VPN
and proxy hosts included, and 1,451 DoH server IPs suitable for a firewall alias. Rebuilt several times
daily, and that cadence is the point, because a vendor only has to add one endpoint to win until
someone notices.

Treat DoH as an arms race you are participating in, not a hole you have closed.

### RFC 9462 is the problem arriving next

[Discovery of Designated Resolvers](https://www.rfc-editor.org/rfc/rfc9462.html) lets a client query
`_dns.resolver.arpa` and upgrade itself to an encrypted resolver with no user configuration and no
hardcoded endpoint. Today a television that wants DoH has to ship an address you can eventually find.
Under RFC 9462 it can discover one at runtime.

Nothing to do about it yet beyond watching for `_dns.resolver.arpa` in your query log. If you see it
from a TV, that is a finding worth reporting.

### Intermittent blocking buys you delay, not privacy

Gamers Nexus and Level1Techs reported an LG G5 that kept recording after its network cable was pulled
and uploaded the audio once connectivity came back (coverage links are in
[the project README](../README.md#what-we-know)).

The mechanism is visible in LG's own software. The webOS Homebrew Channel neutralises crash and
diagnostic uploads by read-only bind-mounting `/tmp/rdxd`, `/tmp/uploadd`, `/var/spool/rdxd` and
`/var/spool/uploadd/*`, which are spool directories, meaning queues that survive being offline.

Recognition itself is continuous. On LG sets, frames are sampled every 10 ms, batched, and sent every
15 seconds, peaking every minute. On Samsung sets, frames are sampled every 500 ms and sent about
every minute, peaking every five minutes ([IMC 2024](https://arxiv.org/html/2409.06203v1)). A filter
that works four days out of five does not remove four fifths of the data. It delays it.

## What you can and cannot guarantee

**You can guarantee plain DNS and DNS-over-TLS.** Redirect 53, reject 853, twin both rules over IPv6,
and a device on that network has no unencrypted and no DoT path off it. That is enforcement, and you
can prove it with a packet capture.

**You can only mostly enforce against DNS-over-HTTPS.** "Mostly" means "as good as your endpoint list
is this week".

**You cannot touch a hardcoded IP dial with DNS at all.** Firewall rules for the addresses you know
about are the whole of the answer, and the list of addresses you know about is short.

Say this to yourself before you tell a housemate the TV is handled.

## If anyone in the house owns a Roku or an old Chromecast, router-level is mandatory

Roku OS has no DNS field and no static IP form, in every version, including Roku-branded televisions
from TCL, Hisense, Philips and Sharp. Chromecast before Google TV has no DNS interface at all and
hardcodes Google's resolvers.

For those two devices, "change the DNS on the device" is not a step that exists. There is no menu to
open. A router-level resolver plus a port 53 redirect is the only option, and the redirect matters more
than usual, because the redirect does not change what the device asks for. It changes who answers.

## Carrier-grade NAT is a red herring

CGNAT sits between your router and the internet, and it has no effect on outbound DNS leaving your
LAN, because your interception happens before the traffic ever reaches it. It comes up constantly in
threads about this and it is irrelevant. Ignore it.

## One warning about attribution

The pfSense recipe needs three rules, and the third is outbound NAT, which masquerades the source
address. After that your resolver sees every query as coming from the router. Per-client attribution in
the query log is gone.

If all you want is blocking, that is a fair trade. If you want to know which device asked for a domain,
or you want to send us a device report, it is not, because a report with no device attribution is a
report about a router. Prefer a topology that does not need the masquerade. Source for the recipe and
the caveat: [LabZilla](https://labzilla.io/blog/force-dns-pihole).

## Where to go next

- Pick the software: [Choose a resolver](choose-a-resolver.md)
- Then the recipe for your router: [OpenWrt](routers/openwrt.md),
  [pfSense and OPNsense](routers/pfsense-opnsense.md), or
  [an ISP gateway you cannot change](routers/isp-gateway.md)
- Before you trust any of it: [Verify it works](verify-it-works.md)
- The failure that catches almost everyone: [IPv6 leaks](ipv6-leaks.md)
