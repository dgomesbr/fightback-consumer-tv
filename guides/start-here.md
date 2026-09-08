# Start here

**Five minutes, no hardware, no terminal.** Three switches in your TV's own menus stop most of what
you read about. Do them in this order.

You need the TV, its remote, and nothing else. Every step here is reversible, and none of it voids a
warranty or changes anything you cannot change back the same way you changed it.

| Step | What it stops | Time |
| --- | --- | --- |
| 1. Turn off content recognition | The TV recording what is on screen and sending it home | 2 min |
| 2. Turn off ad personalisation | Your viewing being matched to an advertising profile | 2 min |
| 3. Decide about the router | Everything the TV does that ignores its own settings | 0 min today |

## Step 1. Turn off content recognition

Content recognition means the TV samples the picture on screen, every fraction of a second, and sends
those samples to a server that identifies what you are watching. It runs on whatever is on the screen,
including a games console or a laptop plugged into an HDMI port.

Find the switch on your vendor's page. It is usually not called "content recognition", which is why
people miss it.

| Your TV | The setting is called | Page |
| --- | --- | --- |
| LG | **Live Plus** | [lg-webos](vendors/lg-webos.md) |
| Samsung | **Viewing Information Services** | [samsung-tizen](vendors/samsung-tizen.md) |
| Roku TV | **Use info from TV inputs**, under Smart TV Experience | [roku](vendors/roku.md) |
| Vizio | **Viewing Data** | [vizio](vendors/vizio.md) |
| Hisense | **Personalised Ads**, and see the page for the rest | [hisense-vidaa](vendors/hisense-vidaa.md) |
| Sony | There is no single switch. Sony sets ship Samba TV as an app, so this one takes the extra step on the page | [sony](vendors/sony.md) |
| Amazon Fire TV | **Device Usage Data** and **Collect App Usage Data** | [amazon-fire-tv](vendors/amazon-fire-tv.md) |
| Apple TV | Nothing to turn off. Apple's TV software has no content recognition | [apple-tvos](vendors/apple-tvos.md) |
| Something else | Work out the platform first | [Find your TV](README.md) |

A Roku player, the stick or box rather than a Roku-branded television, has no Smart TV Experience
setting, because it has no TV inputs to watch.

### This actually works

A 2024 peer-reviewed study measured Samsung and LG televisions before and after using these switches.
After opting out, the researchers found a complete absence of traffic to every content recognition
domain they had identified, and no new domains appeared to replace them
([Anselmi et al., IMC 2024](https://arxiv.org/html/2409.06203v1); code and data at
[SafeNetIoT/ACR](https://github.com/SafeNetIoT/ACR)).

The switch is not decoration. The vendor honours it. That is the single most encouraging finding in
this whole project, and it is why Step 1 comes before anything involving your router.

On a Vizio set the switch exists because a regulator forced it. The FTC's 2017 order requires Vizio to
get affirmative express consent before collecting viewing data
([press release](https://www.ftc.gov/news-events/news/press-releases/2017/02/vizio-pay-22-million-ftc-state-new-jersey-settle-charges-it-collected-viewing-histories-11-million)).
Turning Viewing Data off is a right you were given, not a hack.

## Step 2. Turn off ad personalisation

This is a different setting in a different menu, and turning off content recognition does not turn it
off. On most platforms it sits near a "reset advertising ID" button, which is worth pressing at the
same time. Resetting the ID breaks the link between everything collected so far and everything
collected from now on.

Your vendor page lists the exact path. On LG look for Limit Ad Tracking. On Samsung, Interest-Based
Advertisements sits on the same screen as Viewing Information Services. On Roku it is Limit ad
tracking, or Personalize ads on newer builds. On Fire TV it is Interest-based Ads.

## Step 3. Two or three more switches, while you are in there

**The microphone.** Every platform with voice control has a switch for it. LG puts voice recognition
under General > AI Service. Samsung has Voice Recognition Services on the privacy screen. Roku has
Channel microphone access under Privacy > Microphone. If you use the remote's voice button, leaving it
on is a real trade, so make it deliberately.

**Let the TV stop talking to your phone.** If you never control the TV from a phone app, turn that off.
On a Roku, it is "Control by mobile apps", and from Roku OS 14.1 it gates most control commands. On an
LG, the equivalent switch closes a network listener on ports 3000 and 3001, which is the same service
that four 2023 Bitdefender vulnerabilities were chained through, with over 91,000 devices found
exposing it to the open internet
([writeup](https://www.bitdefender.com/en-us/blog/labs/vulnerabilities-identified-in-lg-webos)).
Your LG page has the exact toggle.

**If you own a Hisense, do not use the TV's web browser.** Security researchers found the browser can
be made to install an application with no notification to you, and to read files off the set,
including the Wi-Fi configuration ([bananamafia.dev](https://bananamafia.dev/post/hisensehax/)). Use a
phone, a laptop, or anything else.

Every path on the vendor pages is marked either verified on real hardware or needs-confirmation.
Most privacy paths are currently needs-confirmation, because several vendors' own privacy pages
returned errors or could not be read when we checked them. If a path is wrong on your model, telling
us is a two-minute fix for everyone with that model.

## Do you need to do anything at the router?

Steps 1 to 3 are the most effective five minutes available to you, and for many people that is enough.
Here is the honest limit.

A peer-reviewed measurement across more than 200 homes found that **68% of smart TVs ignore the DNS
server their router hands them** and talk to Google's resolver directly
([Mazhar and Shafiq, IoTDI 2020](https://arxiv.org/abs/2001.08288)). A television that ignores your
router's instructions is also a television whose behaviour you cannot see and cannot change from the
sofa.

So the two halves of this do different jobs, and neither one replaces the other:

- **The switches on the TV** stop the collection at the source, for the things the vendor has agreed
  to let you stop. Content recognition is one of those things, and the study above shows it stops
  completely.
- **Filtering at the router** covers everything else the TV contacts, covers every other device in the
  house, and shows you what is actually happening rather than what the menu claims.

The router step takes about thirty minutes and does not touch the TV at all. If you have a Roku, or a
Chromecast made before Google TV, it is the only step available to you, because neither device has a
DNS setting anywhere in its menus.

## What to do next

1. If you stopped at Step 3, you are done for today. Put a note in your calendar to re-check the
   switches after the next firmware update, and tell us what you find. Whether updates quietly turn
   content recognition back on is an open question nobody has measured, and it is one of the things
   this project is trying to answer.
2. If you want to see what your TV contacts, read [Why do it at the router](why-dns.md). It explains
   what filtering can and cannot reach before you spend any time on it.
3. If you already know you want to filter, go straight to
   [Choose a resolver](choose-a-resolver.md). The free, no-hardware, no-account option is the first
   one on that page.
4. If a menu path on your vendor page was wrong, or a setting had a different name on your model, open
   a [bug report](../../../issues/new?template=bug_report.yml) with the model number and firmware
   version. Corrections are the contribution we want most.
