# IPv6 leaks

**This is the top silent failure in DNS filtering.** Everything looks configured, the resolver is
running, the blocklists are loaded, and the television is not being filtered at all.

It gets its own page because it does not announce itself. There is no error message, no failed test, no
red light. Your IPv4 rules are correct and they are also irrelevant, because the device stopped using
IPv4 for DNS.

## What it looks like

Pick whichever of these matches you:

- The resolver's query log is empty for the television, while the television is plainly online and
  streaming.
- The log has queries from the TV but not many, and none of the domains you expected.
- Filtering works on your laptop and not on the TV, with identical settings.
- It worked for a week, then stopped, and nothing changed at your end. Your ISP enabled IPv6, or your
  router firmware updated and turned it on.

## The mechanism

A device can learn a DNS resolver over IPv6 through **two independent channels**. You have to close
both, and most people do not know the second one exists.

**Channel one: DHCPv6.** The IPv6 equivalent of the DHCP you already know. If your router runs a DHCPv6
server that advertises a resolver, devices take it.

**Channel two: Router Advertisements.** [RFC 8106](https://www.rfc-editor.org/rfc/rfc8106.html) defines
two options that a Router Advertisement can carry:

| Option | Type | What it carries |
| --- | --- | --- |
| RDNSS | 25 | Recursive DNS server addresses |
| DNSSL | 31 | DNS search list |

A Router Advertisement is not DHCP. It is part of IPv6 address autoconfiguration, and it happens whether
or not you run DHCPv6. So a device can be handed a resolver **with no DHCPv6 involved at all**, from a
router you never configured a DHCPv6 server on.

That is the whole leak. The moment either channel hands the television an IPv6 resolver, your IPv4-only
redirect is bypassed, because the traffic never touches an IPv4 rule. Turning off DHCPv6 and stopping
there is the most common half-fix.

## Fix 1. Give every interception rule an IPv6 twin

The correct fix, and the one that survives someone else changing the network later. If you redirect port
53 on IPv4, redirect it on IPv6. If you reject port 853 on IPv4, reject it on IPv6.

OpenWrt documents exactly this. These two lines are the IPv6 twin from the wiki's own interception
recipe:

```
uci set firewall.dns_int6.dest_ip="fd53::53"
uci set firewall.dns_int6.src_ip="!fd53::53"
```

`fd53::53` is the wiki's example address for the resolver. Substitute your resolver's IPv6 address in
both lines, and keep the `!` on the second one. That exclamation mark excludes the resolver from its own
redirect. Leave it out and the resolver's upstream queries are redirected back to the resolver, which
loops and takes DNS down for the whole network.

The same recipe sets `firewall.dns_int.family="any"` on the IPv4 redirect rule. The complete block, with
every field, is on the [OpenWrt page](routers/openwrt.md), reproduced verbatim from
[the OpenWrt wiki](https://openwrt.org/docs/guide-user/firewall/fw3_configurations/intercept_dns). It is
identical for fw3 and fw4.

For pfSense and OPNsense the shape is the same: whatever the IPv4 rule does, an IPv6 rule has to do too.
See [pfSense and OPNsense](routers/pfsense-opnsense.md).

## Fix 2. Stop advertising an upstream resolver in your Router Advertisements

If you cannot write IPv6 firewall rules, the next best thing is to stop handing out a resolver you do
not control. Either advertise your own resolver's IPv6 address in the RDNSS option, or advertise no
RDNSS option at all.

Advertising your own is better than advertising nothing, because a device that gets no resolver from the
network is a device that will fall back to something, and what it falls back to is not your choice.

Our source material does not contain a verified menu path for this on any consumer router, so we are not
publishing one. What you are looking for is the router advertisement or RA settings for the LAN
interface, and specifically the DNS server advertised there, which is a separate field from the DHCP DNS
server. If your router calls it something else, tell us what and on which firmware.

## Fix 3. Turn IPv6 off on the device VLAN

The blunt instrument, and a legitimate one if you cannot control the advertisements. No IPv6 on that
network segment means no IPv6 resolver to learn.

The cost is that IPv6 is genuinely useful and some services prefer it. If your televisions are on their
own VLAN this costs you very little, because a television does not need IPv6 to stream. If it means
turning IPv6 off for the whole house, prefer Fix 1 or Fix 2.

## Which fix

| Fix | Effort | Survives someone changing the network | Cost |
| --- | --- | --- | --- |
| IPv6 twin rules | Highest, needs firewall access | Yes | None |
| Advertise your own resolver in RAs | Medium | No, a firmware update can reset it | None |
| IPv6 off on the device VLAN | Lowest | Yes, on that VLAN | No IPv6 for those devices |

Do Fix 1 if you can. Do Fix 3 today and Fix 1 later if you cannot.

## One more setting, if you use IP-based blocklists

Some AdGuard Home configurations are reported to need IPv6 resolution disabled when you are blocking by
IP address rather than by hostname, so that a blocked host cannot be reached over its AAAA record
instead. **This is not in our source material and we have not verified it.** It is here because it comes
up, not because we can stand behind it.

If you can confirm or refute it with a version number and a config, that is a
[bug report](../../../issues/new?template=bug_report.yml) we want.

## Prove it is fixed, over IPv6 specifically

Every step below is the IPv6 version of a step in [Verify it works](verify-it-works.md). Doing the IPv4
version and assuming the IPv6 version passes is exactly the mistake this page exists to prevent.

1. **Check what the device was told.** On a laptop on the same network segment as the TV, look at the
   resolvers the operating system says it has. If an IPv6 address you do not recognise is in that list,
   something is still advertising it. Fix that before testing anything else.
2. **Canary lookup, over IPv6.** Ask a *public IPv6 resolver* for the record only your own resolver
   knows about. If you get your resolver's answer, the IPv6 redirect is working. If you get NXDOMAIN,
   the query reached the public resolver and your IPv6 rule is missing or wrong.
3. **Check your log for an IPv6 client address.** AdGuard Home records the client address on every
   query log record, so a query arriving over IPv6 shows an IPv6 client. If every record from the TV
   shows an IPv4 address and you know the TV has an IPv6 address, you are only seeing half its traffic.
4. **Capture, over IPv6.** On the LAN side, look for IPv6 traffic to port 53, port 853 and UDP 443 going
   anywhere other than your resolver. Port 853 traffic means the DoT reject rule is IPv4-only. Start the
   capture before the TV boots, because most of its DNS requests fire in the first seconds after it
   comes up.
5. **Repeat after the next router firmware update.** IPv6 settings are among the most likely to be
   reset by one.

## If you own a UniFi, GL.iNet, Firewalla or Asuswrt-Merlin router

The concepts on this page apply unchanged. The screens do not, because we could not read the
documentation for any of those four during research. All of them returned 403 or 404, and the Merlin
DNSFilter wiki rendered as an empty edit form, so we are not going to guess at menu names for you.

What you need to find on your device: the LAN router advertisement settings and the DNS server
advertised there, the DHCPv6 DNS server if you run one, and whether your firewall lets you write IPv6
rules at all.

If you work it out, please send it in as a
[guide request](../../../issues/new?template=guide_request.yml) with the model and firmware version. A
verified path for one of those four routers would help a lot of people.
