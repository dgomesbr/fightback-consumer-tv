# Security

Two different things land here. Read the right section.

## A vulnerability in this project's own code

The collector, the blocklist generator and the site are the only code we ship. If you find a
vulnerability in one of them, open a [private security
advisory](../../security/advisories/new) rather than a public issue.

The highest-severity class for us is anything that causes the collector to emit data it should have
redacted. A bypass of the hostname templating or the never-collect field list is a privacy incident,
not a bug, and we will treat it that way.

## A vulnerability in a television

**Do not open an issue. Do not post it in a discussion.**

We are a documentation and measurement project. We are not a disclosure coordinator, and this
repository does not host exploit code. If you have found a vulnerability in a TV, streaming device or
its firmware:

1. **Report it to the vendor**, or to a CERT that will coordinate for you. Most TV vendors now have a
   security contact page.
2. **Give them a disclosure window.** Ninety days is the norm.
3. **After it is fixed or the window has expired**, we would like to link your writeup, and to record
   the observable behaviour in the per-model page.

What we will publish, once disclosure has run its course:

- The endpoints a device contacts and the class of data involved.
- That a vulnerability existed, its CVE if one was assigned, and a link to your advisory.
- The vendor's response, including their own wording if they provide it.

What we will not publish, ever:

- Exploit code, payloads, or a reproduction chain.
- A method whose primary use is unauthorised access to someone else's device.

This is not squeamishness. The section 1201 security research exceptions are conditioned on good-faith
disclosure, and circumvention *tools* stay restricted even where the research itself is permitted. See
[LEGAL.md](LEGAL.md).

## Prior art we point people at

The 2023 webOS vulnerabilities were disclosed properly and are a good model. Bitdefender found an
authorisation bypass, a privilege escalation to root through the analytics reporting service, and two
command injections, chained through the service listening on ports 3000 and 3001, with over 91,000
devices exposing that LAN-intended service to the public internet. They coordinated with LG, CVEs were
assigned, and the writeup came afterwards.

We link that. We do not reimplement it.

One useful consequence of their work is a mitigation any LG owner can apply with no developer mode and
no risk, which is in the [LG guide](guides/vendors/lg-webos.md) as a Tier 0 step: turn off mobile
device access, which disables that listener entirely.

## Reporting a data problem in the published dataset

If you find something identifying in our published data, that is urgent and it is not a normal bug.
Open an issue titled `DATA: <what you found>` without quoting the identifying value, and we will
remove the affected rows and fix the redaction rule. See the residual risk section of
[PRIVACY.md](PRIVACY.md).

## Scope

| In scope | Out of scope |
| --- | --- |
| `collector/`, `tools/`, `site/` | Vulnerabilities in televisions |
| Redaction and schema bypasses | Vulnerabilities in Pi-hole, AdGuard Home, NextDNS, PCAPdroid |
| A blocklist entry that breaks a device | Vendor cloud services |
| Identifying data in the published corpus | Anything requiring physical access to your own TV |

For upstream projects, report to that project.
