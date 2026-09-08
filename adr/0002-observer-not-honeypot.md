# 0002. The client is an observer, not a honeypot

**Status:** accepted, 2026-09-08

## Context

The original brief described the client-side component as a honeypot: something that would consume
and log the endpoints a television contacts.

## Decision

The client passively observes network metadata from the user's own device on their own network. It
is called an observer. The schema has no field for payload contents, so a submission cannot carry
one even by mistake.

## Why

Three activities get conflated under one word, and they sit at very different legal altitudes.

**Passive observation of your own device.** Solid ground. The one-party-consent provision at 18
U.S.C. 2511(2)(d) makes interception lawful where the person is a party to the communication, and
its only real condition is the absence of a criminal or tortious purpose. Every peer-reviewed study
this project builds on took this approach, and the IMC 2024 team chose black-box auditing
deliberately, listing payload analysis as future work.

**Redirecting a vendor domain to a local sink.** Probably lawful to do on your own network. The
problem is not the capture, it is the captured payload, which will contain viewing history and
device identifiers. That is personal data of the household under GDPR Recital 26. Capturing it is
the user's business. Redistributing it is a data protection act, and publishing it is a publication
of personal data.

**Defeating a protection to read the payload.** Patching certificate pinning, extracting keys,
rooting to dump binaries. DMCA section 1201 reaches circumvention of protection measures, the
interoperability exceptions are narrow, and circumvention tools stay restricted even where the
research itself is permitted.

The word "honeypot" implies deception of a third party. It invites the tortious-purpose question
under 2511(2)(d) and a framing this project does not want. It buys nothing and costs a lot.

## What this rules out

No payload field in the schema, at any depth, so a submission cannot carry one. No pinning bypass,
no certificate injection helper, no application patcher, none of which we ship or link. No raw
packet captures or resolver logs accepted, since both carry client addresses and the hostnames of
other devices. No impersonation of a vendor endpoint in anything the project ships.

## Consequences

We can never say what a television sent, only which endpoint it contacted and how often. That is a
real limit on what the dataset can prove, and it is the same limit the state of the art operates
under. Stating it plainly is better than overclaiming and being dismissed.
