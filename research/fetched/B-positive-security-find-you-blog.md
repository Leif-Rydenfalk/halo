Find You: Building a stealth AirTag clone | Positive Security
HOME
About
Services
Blog
Contact
Find You: Building a stealth AirTag clone
February 21, 2022
By
Fabian Bräunlein
After AirTags are reportedly used more and more frequently for malicious purposes, Apple has published a statement that lists its current and future efforts to prevent misuse
We built an AirTag clone that bypasses all those tracking protection features and confirmed it working in a real-world experiment (source code available
here
)
We encourage Apple to include AirTag clones/modified AirTags into their threat model when planning the next changes to the Find My ecosystem
Introduction
Recently, reports about AirTags being used to track other people and their belongings were
becoming
much
more
frequent
.
In one exemplary stalking case
, a fashion and fitness model discovered an AirTag in her coat pocket after having received a tracking warning notification from her iPhone.
Other times
, AirTags were placed in expensive cars or motorbikes to track them from parking spots to their owner’s home, where they were then stolen.
On February 10, Apple addressed this by publishing
a news statement
titled “An update on AirTag and unwanted tracking” in which they describe the way they are currently trying to prevent AirTags and the Find My network from being misused and what they have planned for the future.
Admittedly, I might be slightly more familiar with AirTags than the average hacker (having
designed
and
implemented
a communication protocol on top of Find My for arbitrary data transmission), but even so I was quite surprised, that when reading Apple’s statement I was able to immediately devise quite obvious bypass ideas for every current and upcoming protection measure mentioned in that relatively long list.
The following section will discuss each anti-stalking feature and how it can be bypassed in theory. Thereafter I will describe how I implemented those ideas to build a stealth AirTag and successfully tracked an iPhone user (with their consent of course) for over 5 days without triggering a tracking notification.
The goal of this blog post is to raise awareness of these issues to hopefully also guide future changes. In particular, Apple needs to incorporate non-genuine AirTags into their threat model, thus implementing security and anti-stalking features into the Find My protocol and ecosystem instead of in the AirTag itself, which
can run modified firmware
or not be an AirTag at all (Apple devices currently have no way to distinguish genuine AirTags from clones via Bluetooth).
The source code used for the experiment can be found
here
.
Edit: I have been made aware of a research paper titled
"Who Tracks the Trackers?"
(from November 2021) that also discusses this idea and includes more experiments. Make sure to check it out as well if you're interested in the topic!
Table of Contents
-- MARKDOWN --
- [In Theory](#in-theory)
- [Current Features](#current-features)
- [Serial number](#serial-number)
- [Beeping](#beeping)
- [iPhone notifications](#iphone-notifications)
- [Android notifications](#android-notifications)
- [Side note: Apple-ID for querying location reports](#side-note-apple-id-needed-to-query-location-reports)
- [Upcoming Features](#upcoming-features)
- [New privacy warnings during AirTag setup](#new-privacy-warnings-during-airtag-setup)
- [Addressing alert issues for AirPods](#addressing-alert-issues-for-airpods)
- [Updated support documentation](#updated-support-documentation)
- [Precision Finding](#precision-finding)
- [Display alert with sound](#display-alert-with-sound)
- [Refining unwanted tracking alert logic](#refining-unwanted-tracking-alert-logic)
- [Tuning AirTag’s sound](#tuning-airtag’s-sound)
- [In Practice](#in-practice)
- [Test setup](#test-setup)
- [Android detection](#android-detection)
- [Tracker Detect](#tracker-detect)
- [AirGuard](#airguard)
- [iOS detection](#ios-detection)
- [Closing Thoughts](#closing-thoughts)
-- /MARKDOWN --
In Theory
Let’s take a look at all of Apple’s (planned) tracking protection features and how we could bypass them with an
OpenHaystack
-based AirTag clone.
Current Features
Serial number
From the news statement:
“Every AirTag has a unique serial number, and paired AirTags are associated with an Apple ID. Apple can provide the paired account details in response to a subpoena or valid request from law enforcement. We have successfully partnered with them on cases where information we provided has been used to trace an AirTag back to the perpetrator”
Why this does not affect our scenario:
The microcontroller used to build the AirTag clone (e.g. an ESP32) does not have an AirTag serial number (neither in software nor on the hardware).
OpenHaystack-based clones are already not paired with an Apple ID (as this is not necessary as a result of the privacy-focused design).
Beeping
Initially, an AirTag that has not been in Bluetooth reach of its paired Apple device for over 3 days started to beep. With an update in June 2021, Apple decreased this to a random time frame between 8 and 24 hours.
This one is easy: Our ESP32 does not even have a speaker. Furthermore the OpenHaystack firmware does not implement
the BLE service to remotely trigger the sound
, so the “Play Sound”-button is not even shown.
As a side note, there is already a market for so-called “Silent AirTags” (modified AirTags that had their speaker removed/disconnected).
Searching for “silent airtag” on
ebay.de
currently shows several options for AirTags with deactivated speakers
iPhone notifications
From the
docs
:
“If any AirTag, AirPods, or other Find My network accessory separated from its owner is seen moving with you over time, you'll be notified”
Here, things are becoming more interesting. From the news reports linked in the beginning, this also seems to be the most common way unwanted AirTags are detected.
Here, we have an interesting and quite unique trade-off between privacy and... privacy:
On the one hand, Apple wants AirTags to be indistinguishable from each other via Bluetooth to prevent identification of a specific AirTag over a longer period of time to thwart continuous tracking of specific AirTags (or iPhones, etc.) via a network of distributed Bluetooth receivers
On the other hand, Apple wants to identify specific AirTags over some period of time to distinguish between one AirTag traveling with the user (where it should send a notification), and the user walking through a busy area constantly receiving pings from different nearby AirTags (where it should not alert the user)
By programming an AirTag (clone) to continuously broadcast new, never-seen-before public keys (just once per public key), we can simulate the second scenario with a single device.
For the below PoC/experiment, the AirTag clone was iterating over a list of 2000 preloaded public keys and sending 1 beacon per public key every 30s (more details in the next section).
Android notifications
With the initial launch of AirTags, besides the beeping there was no way for Android users to be notified of unwanted tracking devices traveling with them. In December 2021, Apple released an Android app called
Tracker Detect
that could be used to actively scan for nearby tracking devices.
This however has two issues:
The app does not run in the background; an Android user would need to perform an active scan when they are close to the AirTag
In case the app tries to prevent false positives from a single received beacon from a passing Find My device, it is vulnerable to the same “1-beacon-per-public-key-attack” described above
(There is also a (better) alternative app by the OpenHaystack team called AirGuard, which we will also discuss shortly in the next section)
Side note: Apple ID needed to query location reports
While OpenHaystack-based AirTag clones are not paired with an Apple ID, the retrieval of location reports requires authentication. Such an account however can be created anonymously using an email address without any identity/KYC-verification.
The OpenHaystack team currently
even considers running a server
that proxies those location report requests, which in the future might take away the need to create an account oneself.
Upcoming features
Let’s take a look at each item listed in the news statement’s “Advancements Coming” section:
New privacy warnings during AirTag setup
Irrelevant as it won’t deter criminals and is not seen when using OpenHaystack.
Addressing alert issues for AirPods
Irrelevant as it just changes the warning message content in case an alert is triggered by AirPods.
Updated support documentation
Irrelevant as it does not include any technical changes.
Precision Finding
Precision Finding requires Apple’s U1 Ultra Wideband chip in the tag. As the AirTag clone microcontroller does not include such an UWB chip, those simply can’t be found using Precision Finding.
Display alert with sound
”When AirTag automatically emits a sound to alert anyone nearby of its presence and is detected moving with your iPhone, iPad, or iPod touch, we will also display an alert on your device that you can then take action on, like playing a sound or using Precision Finding, if available. This will help in cases where the AirTag may be in a location where it is hard to hear, or if the AirTag speaker has been tampered with.”
This notification can simply be skipped in a clone implementation (as it’s currently the case with OpenHaystack).
Refining unwanted tracking alert logic
“Our unwanted tracking alert system uses sophisticated logic to determine how we alert users. We plan to update our unwanted tracking alert system to notify users earlier that an unknown AirTag or Find My network accessory may be traveling with them.”
This is very vague, but the most relevant point. The dilemma: if they don’t want to notify users every single time a location report is sent to Apple by their device, it will be hard to defend against constantly rotating public keys.
In any case, the conducted experiment shows that currently the tracking alert logic can be bypassed while still being able to track iPhone users.
Tuning AirTag’s sound
“Currently, iOS users receiving an unwanted tracking alert can play a sound to help them find the unknown AirTag. We will be adjusting the tone sequence to use more of the loudest tones to make an unknown AirTag more easily findable.”
This will only be helpful if already having received a tracking alert and does not apply to AirTag clones without a speaker.
In Practice
"In theory there is no difference between theory and practice. In practice there is."
- Benjamin Brewster
I decided to test my hypotheses (mainly on the single-use public keys) by building such a stealth AirTag and performing a real-world experiment.
Test setup
What we need:
An ESP32, a power bank and a USB cable
A custom ESP32 firmware that constantly rotates public keys
A way to retrieve and display the decrypted location reports for each broadcasted public key
For the experiment, I decided to pre-generate random key pairs on the correct elliptic curve and include the public keys in the firmware to be flashed. The corresponding private keys will be stored in an OpenHaystack-compatible .plist file. In theory, this allows using the vanilla (and even pre-compiled) OpenHaystack macOS client to import each possible public key as its own tag.
In practice, the client is not designed to handle thousands of tags (note that Apple is officially only allowing 16!), so I made a few changes to optimize for that use case (combining location report requests for different devices into a single HTTP request, skipping keychain operations, slightly optimizing a quadratic complexity operation).
The modified firmware and macOS retrieval application can be found at
https://github.com/positive-security/find-you
. The python script used for generating key pairs in the correct format has purposefully been omitted.
Some more notes/details:
For the experiment, I chose to iterate through 2000 key pairs and send one beacon every 30 seconds (a public key will therefore be repeated every ~17 hours)
Instead of a finite list of keypairs, a common seed and derivation algorithm could be used on the AirTag clone and in the Mac application to generate a virtually never-repeating stream of keys
When using a irreversible derivation function and always overwriting the seed with the next round’s output, Apple or law enforcement could not retrieve the tag’s previously broadcasted public keys or discovered locations, even with physical access in case the device is discovered
The tracked person was using an iPhone with iOS 15.3.1 with
all relevant settings configured
to receive Find My Safety Alerts
The stealth AirTag clone was with the tracked person for over 5 days, also when leaving their house
Previous prototype with a larger power bank (the logic analyzer just acts as a dummy load to hinder the power bank from turning off)
Android detection
Tracker Detect
Running Apple’s Tracker Detect’s active scan to search for Find My devices will not show the stealth AirTag at all, all the while location reports for the broadcasted public keys were uploaded and could be retrieved.
No results when scanning for trackers right next to the stealth AirTag clone. Side note: In case a tracker was found, Tracker Detect apparently enforces a 15 minute cooldown in the app until a sound can be played on an AirTag
While not having investigated this more, the likely reason is that the app is waiting for multiple beacons with the same public key before the tag is shown in the UI.
AirGuard
First released in August 2021 (>4 months before Tracker Detect) by SEEMOO, the TU Darmstadt lab also behind OpenHaystack,
AirGuard
provides an alternative way to scan for nearby Find My devices.
The advantage is that, similar to Apple’s iOS implementation, the app also supports continuous scanning in background. However, this feature is also implemented in a way that requires multiple beacons with the same public key to trigger an alert, and therefore can also be bypassed with a “1-beacon-per-public-key”-AirTag:
“Whenever a tracker gets detected multiple times the app will recognize this. It compares the locations where the tracker has been detected. If a tracker is detected at least 3 times and the locations have changed (to make sure [it's] not your neighbour) the app sends you a notification.”
In contrast to Tracker Detect, AirGuard's “Manual Scan” feature however will show the stealth AirTag clone (as one new device per received beacon):
The AirTag clone showing up as multiple devices (one device per beacon). Also note that the app does not provide the usual option to play a sound, as the AirTag clone does not offer
this BLE GATT service
.
iOS detection
The stealth AirTag clone was passed to the tracked person on February 16 and continuously stayed with them until February 21. During this time frame, the person spent a lot of time at their home, but we could also track several trips outside (not shown below for privacy reasons).
The modified macOS retrieval application running on an AWS instance and showing one device per broadcasted beacon
There is not much to say except that neither the tracked iPhone user, nor their iPhone-using roommate received any tracking alerts throughout that period. All the while, their iPhones were forwarding their location to Apple’s servers in a way that allowed me to retrieve and decrypt them.
Well, and the ESP32 obviously didn’t start to beep during that time.
Closing Thoughts
In the initially referenced news statement, Apple also writes:
"It’s why we innovated with the first-ever proactive system to alert you of unwanted tracking. We hope this starts an industry trend for others to also provide these sorts of proactive warnings in their products.”
I find it quite funny how they promote having tracking alerts for a tracking system that they have brought to life in the first place. They introduced the first-ever system for easy, cheap, worldwide tracking into a world where “unwanted tracking has long been a societal problem”, applaud themselves for implementing broken anti-stalking features, and now coerce others into also implementing protection against the tracking network they have rolled out.
The main risk does not lie in the introduction of AirTags, but in the introduction of the Find My ecosystem that utilizes the customer’s devices to provide this Apple service. Since Apple in the current Find My design can’t limit its usage to only genuine AirTags (and official partner’s devices), they need to take into account the threats of custom-made, potentially malicious beacons that implement the Find My protocol (or AirTags with a modified firmware). With a power bank + ESP32 being cheaper than an AirTag, this might be an additional motivation for some to build a clone themselves instead.
With the system’s current design, it seems very difficult to technically distinguish one malicious AirTag clone with constant public key rotations continuously traveling with you from you passing by a few genuine AirTags in your day-to-day life.
While the unusual behavior of constantly receiving Find My beacons from seemingly different devices every time could be detected by implementing some more logic, this probably falls down when the AirTag clone is then sending data in random intervals and, in case it’s needed to trick the behavioral analysis, a few beacons multiple times.
When performing the tests, only the active scan mode of the 3rd-party app AirGuard was detecting the stealth AirTag clone. While we don’t encourage misuse, we hope that sharing this experiment will yield positive changes to the security and privacy of the Find My ecosystem.
‍
Follow us on Mastodon (
@positive_sec
) to keep up to date with our posts.
‍
© 2025 Positive Security
Legal disclosure