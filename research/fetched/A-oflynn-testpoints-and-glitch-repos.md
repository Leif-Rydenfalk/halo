# FETCHED: Apple AirTag Teardown & Test Point Mapping — Colin O'Flynn

- **Source URL:** https://colinoflynn.com/2021/05/apple-airtag-teardown-test-point-mapping/
- **Published:** 2021-05-08 by Colin O'Flynn
- **Companion repo:** https://github.com/colinoflynn/airtag-re (licensed CC-BY-4.0 — photos usable commercially with attribution to Colin O'Flynn)
- **Date fetched:** 2026-09-03
- **Note:** Blog body converted from HTML to text; images are not inlined. Comment spam / site nav trimmed at the end.

---

Apple AirTag Teardown & Test Point Mapping
May 8, 2021
—
by
Colin O’Flynn
in Hardware Hacking

What’s inside of Apple’s new AirTag? There was already an iFixIt teardown (which I swear was missing a few items that are there now), but of course was curious to see what sort of protection was enabled. Notably the nRF chip used is likely vulnerable to a known bypass of security as well. With that in mind, I set out to see how we could dump some data from this thing – the good news is you can access a lot of interesting stuff (including the SPI flash) right from the backside, which requires you to simply pop the first plastic cover off. This is super-easy to do without damaging anything. Going further than that is tricky to keep it all intact.

Apple AirTag with Numbered Test Points
If you want to jump right to the answers, check out my AirTag-RE repo on github where I list the known test points that will be of interest. You can also see my twitter thread where I started the teardown:
OK I didn't appreciate how jam-packed this thing is from @iFixit teardown photos. Also it's 0.3mm PCB so I'm pretty sure I broke some solder joints getting it out. Test pads are accessible w/o removing PCB so if this one isn't working will test another one. pic.twitter.com/KmqGUDWkP6
— Colin O'Flynn (@colinoflynn) May 6, 2021
To remove the board from the AirTab, the best way is to bend the case to the side like this:

The center PCB with plastic enclosure just pops out. The plastic part includes the various antennas which are printed onto it – if you remove the PCB from the black plastic enclosure you will rip the antenna solder points. Once you do that, you’ll be rewarded with the back view of the PCB:

Back view of PCB
The solder joints at the edges are the antenna connections which ripped off (4x at upper center and 2x bottom left-of-center). The nRF chip has a NFC and Bluetooth antenna present. If you try to use the board like this, you need at minimum to add the bluetooth antenna back as shown here:

From a later test – a nice bluetooth antenna.
I pulled some of the chips off to investiate any connections between the test points and the chips, using a printed view of the nrf chip while I looked under a microscope as a reference:

To make probing easier, you can also see how I added some of the test points into wires that then go into my field of view:

The SPI flash chip had 10 pins on it – it was missing some center pins. Luckily if you check Digikey for SPI flash in WLCSP with 10 pins, there is one single hit: GD25LQ32DLIGR. And from that datasheet you can find the pinout:

I did a simple dead-bug on the chip to connect up the required pins, here is the center part:

They just run over to some header pins to the right:

Then you just wire the breakout board up to a SPI reader – I’m using a Segger J-Link due to it’s wide support of various flash chips & very high speed. To provide power I use my own CW308 base board which has a 1.8V regulator:

Segger J-Flash SPI detects it as a GD25LQ32C device. I read it twice & verified it, so looks like this worked ok. Apple gives you a good warning at the start of the file:

Interestingly it seems to have a lot of firmware in there – at least the U1 chip firmware, but it looks like nRF firmware as well! I won’t go into that here as wanted to explore how you could talk to this device more easily. But you can see @stacksmashing / @ghidraninja explore this more on a twitter thread:
Continuing the tweet-chain of @colinoflynn on AirTag hacking, we will look at the flash contents now! https://t.co/jctUI3IDBd
— stacksmashing (@ghidraninja) May 7, 2021
But if you just want to read/write the SPI flash to play along you can get away with using the test points I linked from the github. All you need is:
	•	3.0 to 3.3V to power unit (be sure to power BOTH positive battery tabs – they are NOT connected on the PCB even though you would expect that).
	•	1.8V to the SPI power (test point 21)
	•	SPI connections for the SPI Chip

Example of talking to the SPI chip with minimum required connections to the test pads.
You’ll need something that supports the GD25LQ32C device to talk to it. Note the nrF is still running here – so it may conflict, but I found the tag is often asleep and our “force power” of the SPI means the nRF isn’t trying to talk to the SPI chip (since the nRF is asleep).
If you want to do fancy emulation stuff (such as with spispy or em100pro-g2), you’ll need to remove the on-board SPI flash. If you want to minimize antenna damage, you can cut through the black plastic as here to pop off the SPI device:

The super-thin PCB quickly heats up, so a short blast of hot air is enough to then pop off the package without damaging anything else. This will leave the antenna for the U1 chip + bluetooth exactly as they were originally.
The repo includes some additional test points including the SWD/SCLK for the nRF chip. But as those are less interesting for intro hardware hacking, I’ve mostly kept to the SPI in this blog post.
As a bonus – if you want to use the test points w/o soldering onto the test points, I created a simple 3D printed jig. You’ll need to modify it for the test points you want and the pogo pins you are using, I just had a few I was exploring in the default file. The jig when assembled will look something like this:

You can find the design files for this in the repo linked earlier. Have fun!
AirTag  hardware hacking  SPI
14 responses to “Apple AirTag Teardown & Test Point Mapping”
	1	 ANTALIFE May 13, 2021  Awesome writeup, love the STOP in the FW ;^)  Reply 
	2	 Hackaday Podcast 118: Apple AirTag Hacked, Infill Without Perimeters, Hair-Pulling Robots, and Unpacking the 555 – Ham Kar Chan May 14, 2021  […] Apple AirTag Teardown & Test Point Mapping – Colin O’Flynn […]  Reply 
	3	 Hackaday Podcast 118: Apple AirTag Hacked, Infill Without Perimeters, Hair-Pulling Robots, and Unpacking the 555 – News Bazzar May 14, 2021  […] Apple AirTag Teardown & Test Point Mapping – Colin O’Flynn […]  Reply 
	4	 Researchers Create Covert Channel Over Apple AirTag Network – A2M1N May 18, 2021  […] and alternative uses for the devices. Hardware hacker Colin O’Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	5	 Dark Reading | Security | Protect The Business – Cyber Bharat May 18, 2021  […] and alternative uses for the devices. Hardware hacker Colin O’Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	6	 Researchers Create Covert Channel Over Apple AirTag Network – IT LinesIT Lines May 18, 2021  […] and alternative uses for the devices. Hardware hacker Colin O’Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	7	 Researchers Create Covert Channel Over Apple AirTag Network – RECON Technologies May 18, 2021  […] and alternative uses for the devices. Hardware hacker Colin O’Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	8	 Researchers Create Covert Channel Over Apple AirTag … May 19, 2021  […] vulnerabilities and alternative uses for the devices. Hardware hacker Colin O'Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	9	 Researchers Create Covert Channel Over Apple AirTag Network – Cyber Security Resource May 21, 2021  […] and alternative uses for the devices. Hardware hacker Colin O’Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	10	 Researchers Create Covert Channel Over Apple AirTag Network – ThreatsHub Cybersecurity News May 23, 2021  […] and alternative uses for the devices. Hardware hacker Colin O’Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	11	 Researchers Create Covert Channel Over Apple AirTag … – CyberSecDN May 27, 2021  […] and alternative uses for the devices. Hardware hacker Colin O’Flynn, for example, tore down the AirTags and mapped out the components. Another hardware hacker used the information to dump the firmware […]  Reply 
	12	 Teardown: Apple AirTag – EDN – Savvysavingreviews January 11, 2022  […] The topside, which we saw before when it was still within the case, is dominated by (among other things) five 100 µF electrolytic capacitors (the packaged devices labeled “J107S”). VCC contacts for the shared battery are on both sides (upper corners, to be precise) of the GND connection. Also visible is a Bosch BMA280 (PDF) accelerometer, along with a whole mess of test points. […]  Reply 
	13	 Teardown: Apple AirTag – EDN – Top Snapdeal January 11, 2022  […] The topside, which we saw before when it was still within the case, is dominated by (among other things) five 100 µF electrolytic capacitors (the packaged devices labeled “J107S”). VCC contacts for the shared battery are on both sides (upper corners, to be precise) of the GND connection. Also visible is a Bosch BMA280 (PDF) accelerometer, along with a whole mess of test points. […]  Reply 
	14	 Teardown: Apple AirTag – EDN – JWEasyTech January 12, 2022  […] The topside, which we saw before when it was still within the case, is dominated by (among other things) five 100 µF electrolytic capacitors (the packaged devices labeled “J107S”). VCC contacts for the shared battery are on both sides (upper corners, to be precise) of the GND connection. Also visible is a Bosch BMA280 (PDF) accelerometer, along with a whole mess of test points. […]  Reply 
Leave a Reply
Your email address will not be published. Required fields are marked *
Comment *
Name *

Email *

Website

Save my name, email, and website in this browser for the next time I comment.

←Previous: Analog Discover Pro Teardown
Next: New England Hardware Security Day 2022 Talk→
Colin O'Flynn
Embedded Security, Electronics & More!
About
	•	Team
	•	History
	•	Careers
Privacy
	•	Privacy Policy
	•	Terms and Conditions
	•	Contact Us
All Blog Categories & Posts

Circuit Cellar Articles

Experimenting with Metastability and Multiple Clocks on FPGAs

FPGA Board Design Tips

Programmable Logic in Practice

Circuit Cellar 25th Anniversary Edition

Design a FIR Filter in an FPGA in 30 mins using High Level Synthesis

Electronics & Production

Announcing my "Small Scale Electronics Production" Book

My 2003 Low Cost SMD Soldering Guide

Intel LGA1700 (12th/13th gen, i9 3900k) Top Resistors/Capacitors

Analog Discover Pro Teardown

MeatBag PnP – Simple Pick-n-Place

A Low-Cost X-Y Scanner using 3D Printer

Low-Cost SMD Soldering Setup

ESC SV 2015 – USSSSSB: Talking USB From Python

Experiments with Seek Thermal Camera

USB Inrush Testing

Driver Signing Notes

SMD Solder Paste Stencil Creation with Silhouette Cameo

Hackaday Project and Latest Circuit Cellar Columns

EELive! (ESC) Conference Slides + Programs

Selecting an Oscilloscope

Making a USB-HID Keyboard Encoder Board for PicoScope

Making a Simple Scope Probe Holder

Split Ground Plane: Example of failing high-speed signals

Bed of Nails Test Bed

JCOP

QTabWidget in PySide Automatically Resize

AtMega Card (Funcard) SmartCard Programming & Fuse Setup

Getting started with GIT Revision Control

High-Speed ADC with Variable Gain Amp Input

Avnet Spartan-6 LX9 Board: Or How ChipScope is your Saviour

Turbo Coding Tutorial

LPCXpresso LPC1114 J4 JTAG Pinout

Interfacing to 34401A

Compass Circles

Making AT90USBKEY Run on 5V (Easy Way)

FIP is IPv6 Ready

FIP – The Flexible IP(v6) Stack

Addition of IMU / MLX90609 Code

Moving electronics projects from old site

Updated 15dot4-tools

Hardware Hacking

Dumping Parallel NAND with Glasgow

RECON 2023: Adventures of My Oven (Pinocchio) with ChipWhisperer

New England Hardware Security Day 2022 Talk

Apple AirTag Teardown & Test Point Mapping

BAM BAM!! On Reliability of EMFI for in-situ Automotive ECU Attacks

Square Terminal Teardown

Amazon Echo Dot Gen 3 – Microphone Disable Circuitry

A Call for Time Travel Resistant Cryptography (TTRC)

USB Triggering & Hacking

FICHSA ChipWhisperer Tutorial Requirements

Glitching Trezor using EMFI Through The Enclosure

Embedded World 2019 Conference Talk

More Research, More Fun – I'm now an Assistant Professor

Breaking Electronic Door Locks Like You're on CSI: Cyber – Black Hat 2017 Talk

PhD Thesis Finally Done

Philips Hue, AES-CCM, and more!

Philips Hue – R.E. Whitepaper from Black Hat 2016

Black Hat Slides – PIN-Protected HD Enclosure / MB86C311A Research

Getting Root on Philips Hue Bridge 2.0

SECT-2015 Talk Slides

DEFCON Talk Slides

Side-Channel Power Analysis of AES Core in Project Vault

AtlSecCon Presentation Slides

Breaking IEEE 802.15.4 Networks: Paper/Presentation

Product Reviews

Rigol DP832 Review

PicoScope 2204A Review

PicoScope 5000 (5444) Review

PicoScope 6000 (6403D) Review & Comparison

Quit wasting time debugging USB: Using TotalPhase Triggers

Metcal MX-500P Soldering Station Review & Repair

Springer / SpringerLink MyCopy Review

Steam Engine

Danni Build – Feb 11/23

Uncategorized

Modifying Welding Pedal for a Miller 6-Pin Connector (ArcCaptain Pedal)

Fixing Ubiquiti Dream Machine (UDM) SE Hard Drive Not Detected Errors

Nova Scotia Embarrassment –

New Site Layout Live

Splitting of NewAE & ColinOflynn.com

Meet me Live, Site Updates, and Book Updates

TikiWiki Upgrade

Articles Posted

YouTube Posts

Square Terminal Teardown

Amazon Echo Dot Gen 3 – Microphone Disable Circuitry

Designed with WordPress

---

## Appendix: verbatim README of https://github.com/colinoflynn/airtag-re (fetched 2026-09-03, CC-BY-4.0, Colin O'Flynn)

**NOTE 1: please fork this repo if using for your own use. I don't intend for this to be a central resource for airtag RE, more just some useful references for you to build on.**

**NOTE 2: This repo will not have any firmware or similar. Issues are disabled because the repo does not have any issues, it's perfect.**

## Test Points

![](images/frontside-tpnames.jpg)


|Name | Description                         |
|-----|-------------------------------------|
|VCC1 | +3.0V input (1 of 2 - both needed)* |
|VCC2 | +3.0V input (2 of 2 - both needed)* |
|GND  | Ground                              | 
|     |                                     |
| 5   | VCC2 (Connects to VCC2 input)       |
| 6   | VCC1 (Connects to VCC1 input)       |
| 7   | GND                                 |
| 8   | nRF ball E2 (P0.16)                 |
| 9   | nRF ball D3 (P0.26)                 |
| 19  | 1.8V SPI Flash - Data In (COPI) / nRF ball H3 (P0.16)    |
| 20  | 1.8V SPI Flash - Data Out (CIPO) /nRF ball H4 (P0.15)    |
| 21  | 1.8V SPI Flash VCC                  |
| 22  | 1.8V SPI Flash - SCLK / nRF ball G3 (P0.17)              |
| 24  | 1.8V SPI Flash - Chip Select (CS)/ nRF ball F4 (P0.11)   |
| 29  | Apple Logo :) GND                   |
| 30  | nRF ball H1 (P0.21/nRST)            |
| 31  | nRF ball H2 (P0.18/SWO)             |
| 34  | 1.8V from nRF                       |
| 35  | nRF ball F1 (SWCLK)                 |
| 36  | nRF ball G1 (SWDIO)                 |

*NOTE: The big pads under the VCC1/VCC2 battery terminals are NOT connected.
So if you remove the battery terminals you need to solder to the smaller pads where
the terminals connected! I just apply 3.3V here, it's assumed the device will be designed to work with some variation.

### SPI Connections

The SPI connections (SCK/DI/DO/CS) are as above. If talking to the SPI flash chip note the following:

* You need to apply 1.8V on test point 21 to force the flash on.
* The nRF occasionally talks to SPI flash (especially when stuff like adding a device happens) which will interrupt this. But most of time the flash is powered off and thus the pins are tri-stated.

The nrf controls power to the SPI flash, so you need to override it by supplying 1.8V on test point 21.

## Images

See repo for higher resolution.

![](images/backside-1000px.jpeg)
![](images/frontside-1000px.jpeg)

## License

This repo is licensed CC-BY-4.0 (to say explicitly - photos can be used commercially and only require attribution to *Colin O'Flynn*, no additional permission request is needed).
---

## Appendix: verbatim README of https://github.com/pd0wm/airtag-dump (fetched 2026-09-03)

# Airtag dumper
Simple utility to glitch and dump the nRF52832 firmware on an airtag using cheap hardware. Requirements:
 - An airtag
 - A bluepill STM32F103 eval board running https://github.com/pd0wm/airtag-glitcher
 - A `probe-rs` compatible debug adapter such as a J-Link

Connect the following pins from the STM to the airtag (`[test point numbering](https://github.com/colinoflynn/airtag-re#test-points)):
| Function | STM | Airtag |
|----------|-----|--------|
| Glitch output | PB7 | 28 (using an NFET) |
| Trigger | PB8 | 34 (1.8V) |
| Power | PB9 | VCC1 + VCC2 |

Just run `cargo run` to start the process.
 
## Credits
 - [Colin O'Flynn](https://twitter.com/colinoflynn) for documenting the test points: https://github.com/colinoflynn/airtag-re
 - [stacksmashing](https://twitter.com/ghidraninja) for his video explaining the procedure: https://www.youtube.com/watch?v=_E0PWQvW-14
 - [LimitedResults](https://twitter.com/LimitedResults) for their original research into glitching the NRF52: https://limitedresults.com/2020/06/nrf52-debug-resurrection-approtect-bypass/

---

## Appendix: verbatim README of https://github.com/itewqq/airtag-firmware-dump (fetched 2026-09-03)

# Airtag glitcher and dumper

## Hardware prerequisites:
- An airtag
- A `probe-rs` compatible debug adapter such as a J-Link
- A Raspberry Pi 3b+ 
- An NFET

>Other versions of Pi will also work, but you need to adjust the corresponding pins yourself.

# Usage

### 1. Setting the hardware connection
Connect the following pins from the Raspberry Pi 3b+ to the airtag (`[test point numbering](https://github.com/colinoflynn/airtag-re#test-points)):
| Function | Raspberry Pi 3b+  | Airtag |
|----------|-----|--------|
| Glitch output | wiringPi 3 | 28 (using an NFET) |
| Trigger | wiringPi 2 | 34 (1.8V) |
| Power | wiringPi 0 | VCC1 + VCC2 |

### 2. Start the glitcher

Copy the ```airtag-glitcher``` folder to your Raspberry Pi 3b+, enter it and execute the ```run.sh```.

### 3. Start the dumper

Copy the ```airtag-dump``` folder to your computer where the SWD adapter connected and run ```Cargo run```. Next, pray that your glitch will succeed :)

# Credits
 - [pd0wm](https://github.com/pd0wm/airtag-dump) for his original stm32-version dumper
 - [LimitedResults](https://twitter.com/LimitedResults) for their original research into glitching the NRF52: https://limitedresults.com/2020/06/nrf52-debug-resurrection-approtect-bypass/
 - [Colin O'Flynn](https://twitter.com/colinoflynn) for documenting the test points: https://github.com/colinoflynn/airtag-re
 - [stacksmashing](https://twitter.com/ghidraninja) for his video explaining the procedure: https://www.youtube.com/watch?v=_E0PWQvW-14
