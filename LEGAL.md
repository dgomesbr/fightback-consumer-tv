# Legal position and scope

Not legal advice. This page explains where we have drawn the line and why, so contributors know what
belongs here.

## What this project does

It records which internet endpoints a television contacts, and when. Hostnames, ports, protocols,
byte counts. Nothing else.

## What this project does not do

It does not decrypt traffic. It does not bypass certificate pinning. It does not impersonate any
vendor service. It does not modify device firmware. It is not a circumvention tool and it ships no
exploit code.

## Passive observation of your own device

Watching traffic on a network you control, from a device you own, is well-established ground in the
US. [18 U.S.C. 2511(2)(d)](https://www.law.cornell.edu/uscode/text/18/2511) provides that it is not
unlawful for a person not acting under colour of law to intercept an electronic communication where
that person is a party to the communication, unless the interception is for the purpose of committing
a criminal or tortious act.

The operative constraint is that tail clause. Our purpose is documentation and consumer protection,
which is why the schema has no payload field and why we do not accept captures of anything but our own
metadata.

Every peer-reviewed study this project builds on used the same approach:

| Study | Approach |
| --- | --- |
| [Information Exposure From Consumer IoT Devices][imc19], IMC 2019 | 34,586 controlled experiments across 81 devices, encrypted traffic observed but not decrypted |
| [Watching You Watch][ccs19], CCS 2019 | Desktop as access point, top 1,000 channels on Roku and Fire TV |
| [The TV is Smart and Full of Trackers][pets20], PETS 2020 | Residential gateway traffic plus a controlled testbed |
| [Watching TV with the Second-Party][imc24], IMC 2024 | Explicitly black-box; payload analysis listed as future work |
| [IoT Inspector][imwut20], IMWUT 2020 | Crowdsourced from 44,956 devices under IRB approval |

The IMC 2024 authors chose black-box deliberately, noting that a white-box study "requires
reverse-engineering and/or jailbreaking". We follow that choice.

## Three things we will not host

**Payload capture.** Redirecting a vendor domain to a local server that logs what arrives may be
lawful on your own network. The captured payload is a different question: it will contain viewing
history, device identifiers and possibly account references, which is personal data of your household
under GDPR Recital 26. Capturing it is your business. Redistributing it is a data protection act, and
publishing it is a publication of personal data. So the schema has no payload field, and we do not
accept payloads from anyone for any reason.

**Circumvention tools.** [The EFF's reverse engineering FAQ][eff] notes that DMCA section 1201 reaches
circumvention of authentication handshakes, protocol encryption, code obfuscation and code signing,
that the interoperability exceptions are narrow, and that circumvention *tools* stay restricted even
where the underlying research is permitted. So we do not ship or link a pinning bypass, a CA injection
helper, or an APK patcher.

**Root and exploit procedures.** Tier 4 of every vendor guide explains what root achieves, what it
risks, and links to the upstream project. It does not reproduce the steps. That keeps this repository
a privacy toolkit rather than an exploit host, and it means bricked-TV reports go to the people who
actually maintain those exploits.

## The DMCA exemption for smart TVs

For US readers, the relevant provision is worth quoting in full. [37 CFR
201.40(b)(10)](https://www.ecfr.gov/current/title-37/section-201.40) exempts from the section 1201
anti-circumvention prohibition:

> Computer programs that enable smart televisions to execute lawfully obtained software applications,
> where circumvention is accomplished for the sole purpose of enabling interoperability of such
> applications with computer programs on the smart television, and is not accomplished for the purpose
> of gaining unauthorized access to other copyrighted works. For purposes of this paragraph (b)(10),
> "smart televisions" includes both internet-enabled televisions, as well as devices that are
> physically separate from a television and whose primary purpose is to run software applications that
> stream authorized video from the internet for display on a screen.

Three points. The definition covers streaming sticks and boxes, not only televisions. It is scoped to
interoperability of lawfully obtained applications, and does not authorise bypassing content DRM. It
is US-only, and it does not displace a contract: the EFF flags that end-user licence terms prohibiting
reverse engineering have been enforced, as in *Blizzard v. BnetD*.

## Europe

The provision that matters for content recognition is Article 5(3) of the ePrivacy Directive, the
terminal-equipment rule, which requires consent before storing or accessing information on a user's
device regardless of whether it is personal data. It is the same provision that governs cookies.

This is not abstract. The IMC 2024 researchers measured materially different content recognition
behaviour between their UK and US units of the same models, and vendors use separate regional
endpoints. Vendors can ship a no-recognition configuration when the law requires one, because they
already do.

## Warranty and hardware risk

Developer mode on LG, Samsung, Roku, Fire TV and Android TV is an official vendor feature. Using it
modifies no firmware.

Disabling a preinstalled package with `pm disable-user` modifies no firmware either and a factory
reset undoes it. It can still leave a device unbootable. Documented cases include
`com.google.android.webview`, `com.sony.dtv.tvx` and `com.google.android.katniss` on Sony sets, and
several Amazon metrics packages on specific Fire OS builds. Every Tier 3 instruction carries a
factory-reset recovery path.

Rooting and bootloader unlocking are genuine modifications. Treat them as warranty-voiding. The webOS
homebrew maintainers describe software rooting as safe to attempt, and in the same breath warn that
writing to the kernel, root filesystem or TV service partitions is a guaranteed brick. We link their
warnings rather than paraphrasing them.

## If we find a vulnerability

See [SECURITY.md](SECURITY.md). Coordinated disclosure, 90 days, no exploit code in this repository,
and the vendor gets right of reply in the per-model report.

## Claims we will not make

The IMC 2019 authors publicly corrected press coverage of their own work, insisting that because the
traffic was encrypted they did not know whether personal data was being sent.

We hold to the same line. "This television contacted an advertising endpoint 1,400 times while idle"
is a claim we can support. "This television sent your viewing history to an advertiser" is not, unless
someone has shown the payload. Contacted is not the same as exfiltrated, and overstating it is the
fastest way to be dismissed.

[imc19]: https://moniotrlab.khoury.northeastern.edu/publications/imc19/
[ccs19]: https://blog.citp.princeton.edu/2019/09/18/watching-you-watch-the-tracking-ecosystem-of-over-the-top-tv-streaming-devices/
[pets20]: https://arxiv.org/abs/1911.03447
[imc24]: https://arxiv.org/html/2409.06203v1
[imwut20]: https://arxiv.org/abs/1909.09848
[eff]: https://www.eff.org/issues/coders/reverse-engineering-faq
