# Verify it works

**A configured block and a working block are different things.** Most people stop at the first one and
never find out.

Seven checks, in increasing rigour. Step 1 needs nothing but a laptop. Step 5 is the only one that
catches a television dialling a hardcoded IP address. Do as many as you have patience for, in order,
and stop when you are satisfied.

## Before you start: timing matters

**Start any packet capture before the television boots.** The IMC 2024 team note that most DNS requests
fire in the first seconds after activation. Start the capture late and you lose the mapping between
hostnames and addresses for the whole session, which means you see a set of IP addresses and cannot tell
what they were.

Power the TV down, start capturing, then power it up.

## A note on the tools

Our source material pins the *targets* of these checks, ports 53, 853 and UDP 443 on the LAN side, and
everything on the WAN side. It does not pin a specific capture tool or command line, so we are not
publishing one. Use whatever your platform gives you: the packet capture page in your firewall's web
interface, or `tcpdump` on a router that has it, or a mirrored port into anything you already know.

For the lookup steps, whatever your machine has is fine. `nslookup <name> <resolver>` and
`dig @<resolver> <name>` both do the job.

## Step 1. The canary record

The cheapest useful test, and the only one that needs no capture at all.

**Do this.** On your own resolver, create a DNS record that exists nowhere else. Any hostname under a
domain you control, or a purely local name, with any address. Then, from a laptop on the LAN, ask a
*public* resolver for that name. Point the lookup at `8.8.8.8`, or `1.1.1.1`, or anything that is not
your resolver.

**Pass.** You get your own record back. That proves the query never left the network. Your redirect
intercepted it and your resolver answered, even though the client asked somebody else.

**Fail means.** You get NXDOMAIN, or nothing. The query reached the public resolver, which has never
heard of your record. Your port 53 redirect is missing, is on the wrong interface, or exists only for
IPv4 while the laptop asked over IPv6.

## Step 2. Query a public resolver and check your log

**Do this.** Same lookup as Step 1, but this time watch your resolver's query log while you run it.

**Pass.** The query appears in the log, attributed to the laptop's address.

**Fail means.** If Step 1 passed and this fails, something is answering the query that is not your
resolver, or per-client logging is off. If the query appears but is attributed to the router's address
rather than the laptop's, your redirect masquerades the source. That is what the pfSense outbound NAT
rule does, and it costs you per-client attribution permanently. See
[why-dns](why-dns.md#one-warning-about-attribution).

## Step 3. Filter the log to the television

Now the device you actually care about.

**Do this.** Leave the TV on for ten minutes, using it normally. Then filter the query log to the TV's
address or client name.

**Pass.** You see the TV's queries. Some of them are marked blocked. The domains look like the ones on
your [vendor page](README.md).

**Fail means.** An empty log while the television is online is the diagnosis, not a mystery. The TV is
not using your resolver. Two causes, and they need different fixes:

- **A hardcoded resolver.** The TV ignores the DNS server your router advertises. This is normal
  behaviour for 68% of televisions ([Mazhar and Shafiq, IoTDI 2020](https://arxiv.org/abs/2001.08288)).
  Fix it with a port 53 redirect, not with a DHCP setting.
- **Encrypted DNS, or an IPv6 resolver.** The TV is talking DoT on 853, DoH on 443, or plain DNS to a
  resolver it learned over IPv6. Steps 4 and 7 tell you which. [IPv6 leaks](ipv6-leaks.md) is the more
  likely of the two.

## Step 4. Capture on the LAN side

**Do this.** Capture on the interface facing the television. Look for three things: TCP or UDP port 53
to any address other than your resolver, anything on port 853, and UDP 443.

**Pass.** Port 53 traffic goes to your resolver and nowhere else. Nothing on 853. UDP 443 only to hosts
you recognise.

**Fail means.**

| What you see | What it is | Fix |
| --- | --- | --- |
| Port 53 to an address that is not your resolver | The redirect is not catching this device | Check the rule's source zone and that it covers this VLAN |
| Anything on port 853 | DNS-over-TLS, and your reject rule is missing or IPv4-only | Reject 853, both families |
| Sustained UDP 443 to one host, with no DNS query for it | Likely DNS-over-HTTPS | Add HaGeZi's DoH hostname and IP lists. See [why-dns](why-dns.md#dns-over-tls-is-easy-to-stop-dns-over-https-is-not) |
| A query for `_dns.resolver.arpa` | RFC 9462 auto-upgrade. The device is trying to discover an encrypted resolver | Nothing yet, but please report it |

## Step 5. Capture on the WAN side

**This is the step that finds hardcoded IP dials, and no other step can.**

**Do this.** Capture on the router's internet-facing interface, or on the firewall's WAN interface, with
the television as the only thing powered on if you can manage it.

**Pass.** Every outbound connection has a DNS query in front of it that you can find in the query log.

**Fail means.** A connection to a bare IP address with no preceding lookup is a hardcoded dial. DNS
filtering cannot touch it, ever, because there was never a question to answer. Only a firewall rule on
the destination address and port stops it.

Two documented examples to compare against, both from a rooted LG OLED65G5WUA on the
[Level1Techs wiki](https://forum.level1techs.com/t/lg-tv-block-mini-how-to/255178):

| Address | What it is |
| --- | --- |
| `156.147.69.32:8080` | LG over-the-air update fallback |
| `54.186.247.229:443` | LG live telemetry |

If you find one we do not have, it belongs in
[`data/hardcoded/`](../data/hardcoded/) and it is one of the most valuable things you can contribute,
because nobody can find these without doing exactly this capture.

## Step 6. The browser leak test

**Do this.** Open one of the public DNS leak test sites in a browser on a machine on the same network.

**Pass.** It reports your resolver, or your upstream, and not a resolver you did not choose.

**Fail means.** Something on that machine is using a different resolver.

**The caveat that makes this step nearly useless for televisions.** It tests the browser. Browsers ship
their own DoH settings and their own resolvers, independent of the operating system, and a television
app's traffic has nothing to do with any of it. A pass here says nothing about your TV. Run it because
it is quick, not because it is evidence.

## Step 7. Do all of it again over IPv6

Every step above has an IPv6 version, and passing the IPv4 version tells you nothing about the IPv6
one. A device can learn a resolver over IPv6 through DHCPv6 or through a Router Advertisement carrying
the RFC 8106 RDNSS option, so a network you never configured for IPv6 DNS can still be handing one out.

The IPv6 walkthrough is on [its own page](ipv6-leaks.md#prove-it-is-fixed-over-ipv6-specifically),
because this is the most common reason a correct-looking setup does nothing.

## Diagnostic table

| What you see | Most likely cause | Go to |
| --- | --- | --- |
| Query log empty, TV clearly online | Hardcoded resolver, or a resolver learned over IPv6 | [why-dns](why-dns.md), [ipv6-leaks](ipv6-leaks.md) |
| Queries from the TV, none of them blocked | Blocklists loaded but not applied to that client, or the client sits in a group with no filtering | [choose-a-resolver](choose-a-resolver.md) |
| Blocked entries appear and the TV works normally | Working as designed. Content recognition hosts are usually not load-bearing | [what-breaks](what-breaks.md) |
| Blocked entries appear and something broke | You blocked a load-bearing host. Bisect it | [what-breaks](what-breaks.md#how-to-bisect-a-break) |
| TV says it has no internet connection | Your resolver answers SERVFAIL, or the firewall drops instead of rejecting. Some firmware reads either as "no internet" and retries hard | Switch to NXDOMAIN and REJECT |
| Nothing on port 53, steady UDP 443 | DNS-over-HTTPS | [why-dns](why-dns.md) |
| Outbound connection to a bare IP, no DNS query for it | Hardcoded IP dial | Step 5 |
| DNS dead for the entire house right after you added the redirect | The `!` self-exclusion is missing, so the resolver's own queries loop back to it | [OpenWrt](routers/openwrt.md) |
| Works for the laptop, not for the TV, identical settings | The TV is doing something the laptop is not. Step 4 will say what | Step 4 |
| Casting stopped working after a VLAN change | Multicast DNS is link-local and does not cross a router boundary | [what-breaks](what-breaks.md#5-casting-stopped-working) |
| Everything passed last month, nothing is blocked now | Router firmware update, or your ISP enabled IPv6 | [ipv6-leaks](ipv6-leaks.md) |

## What this method cannot tell you

You are auditing hostnames, ports, protocols and byte counts. Not contents.

Decrypting the traffic is deliberately out of scope, and the state of the art agrees with that choice.
mitmproxy's own documentation says pinned applications will not accept its certificates, and the
workarounds are all app-patching tools. A 2021 IMC baseline found 11 of 32 IoT devices interceptable,
about a third, which is not a methodology you can build a dataset on. The IMC 2024 team adopted
black-box auditing explicitly and listed payload analysis as future work.

So a pass on all seven steps means "this device has no unfiltered DNS path off my network". It does not
mean "I know what this device is saying".

## Getting the details for a bug report

If a check fails and you want to tell us, we need the model and firmware version. On a Roku that is
easy from another machine on the LAN: Roku's ECP service answers `GET /query/device-info` on port 8060
with the model, software version, timezone and locale, and `GET /query/apps` lists the installed
channels.

Strip the serial number, device ID and MAC addresses out of that response before you paste it anywhere.
The [collector](../collector/router/) does that for query logs automatically and shows you the file
before it sends anything.

## When everything passes

Two things worth doing while it is fresh.

Re-run Step 3 and Step 5 after the next television firmware update. Whether updates quietly re-enable
content recognition is undocumented, widely repeated, and nobody has measured it. You are now in a
position to.

Then send us what you found. A [device report](../../../issues/new?template=device_report.yml) from a
verified setup is worth more than ten from unverified ones, because we know your log is actually seeing
the device's traffic.
