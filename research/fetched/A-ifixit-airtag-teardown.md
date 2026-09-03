# FETCHED: AirTag Teardown: Yeah, This Tracks — iFixit

- **Source URL:** https://www.ifixit.com/News/50145/airtag-teardown-part-one-yeah-this-tracks
- **Author:** Sam Goldheart, iFixit
- **Published:** 2021-05-01 (updated with "Don't get bored, we've got boards" section ~2021-05-03)
- **Date fetched:** 2026-09-03
- **Note:** Text extracted from HTML. Images/X-ray videos not inlined — see the article and https://valkyrie.cdn.ifixit.com/ URLs cited in the dossier. iFixit teardown text is normally CC BY-NC-SA; archived here as a research reference.

---

AirTag Teardown: Yeah, This Tracks

Article by:
Sam Goldheart
@sam
	•	May 1, 2021
	•	Filed under: Teardowns, Tech News
	•	43 Comments
Share

The long-rumored, tiniest Apple product (that isn’t a dongle) is finally here. Welcome, AirTag! With the entire iPhone network at its back and a truly user-replaceable battery—the first in any Apple product in years—we’re interested to see how AirTags track against tried-and-tested tech.
Note: If you already caught Part One of this teardown, scroll down to “Don’t get bored, we’ve got boards” for the new additions.
Apples to not-Apples

Today’s subjects/victims: Tile Mate, Galaxy SmartTag, Apple AirTag, and one U.S. quarter for scale.
We snagged the market veteran Tile Mate, plus Samsung’s Galaxy SmartTag to judge our AirTag against its competition. Of the three, the AirTag’s Mentos-esque puck is the tiniest. About the size of a half-dollar coin, it’s not much larger than the battery that powers it. The Tile is the thinnest of the bunch, the AirTag about 1.5 times as thick as the Tile, and the SmartTag at least two Tiles high when sideways. Likely spurred by Apple’s penchant for compactness, AirTag literally cuts corners by eliminating the keyring hole (a problem we intend to remedy). It goes without saying that Apple has a history of turning essential functions into premium, add-on accessories. 
But we’re not just here to size these trackers up—you’re getting a 3-for-1 teardown deal today! First up, let’s look inside from the outside, with the help of Creative Electron’s X-ray skills.

X-rays of the Tile Mate, Galaxy SmartTag, Apple AirTag, and not even close to legal tender, via Creative Electron (minus that last one).
As always, these X-rays have a lot to say. AirTags are indeed tiny—about the smallest they can get, judging by the density. Speaking of density, the relative darkness of the AirTag is due to a hefty central speaker magnet and its steel battery cover—both fairly opaque to X-rays. (For a more complete view, check out this amazing 360-degree animated spin.) The other trackers seem sprawling by comparison—and they don’t even include magnets (keep reading to learn why).
The AirTag in X-ray and 360 degrees, via Creative Electron
While the AirTag is impressively compact, it manages to pack in ultra-wideband (UWB) functionality—an interesting technology in and of itself. Samsung just launched a UWB version of its tracker, dubbed the SmartTag+, but two weeks after the official release date it’s still MIA stateside. We tried to secure one for our teardown, but struck out.
Opening salvo

All three trackers open up with finger power—no other tools required! That said, the AirTag is by far the most difficult, especially if you indulged in a snack earlier and have greasy digits. Imagine opening a stubborn pickle jar with just two slippery thumbs, and you’ve got the idea. The other trackers have dedicated divots for separating the pieces with a fingernail—moisturize to your heart’s content!

The ultimate white whale: a tool-free user-replaceable battery in an Apple product! It even comes with written instructions.
Competing devices have replaceable batteries, so Apple may have been pressured to match the market standard in that respect. Still, we commend Apple for building the AirTag to last longer than a battery from the beginning—Tile took six years and 15 million devices to get there. Apple could have included an annoyingly-placed Lightning port or built-in (wasteful, inefficient) wireless charging functionality so the AirTag could charge from the Apple Watch puck charger—but they didn’t, and we’re here for it. That said, early patent filings showed AirTags recharging with an inductive charger. A sign of tech to come? Or more supporting evidence for an Apple product that never was?
Power hour: battery showdown

AirTags feature the shiny new model number A2187 (quick, name that movie reference), and included amongst its regulatory markings is a reminder of the battery type, CR2032. Handy! Both AirTags and SmartTags use 3-volt CR2032 coin cell batteries, while the Tile uses the smaller CR1632 cell. Based on standard button cell nomenclature, all use Lithium battery chemistry, but the 20 mm cells have a .66 Wh capacity, while the Tile’s 16 mm cell only has about .39 Wh. At a glance these may look similar to batteries we’ve found in teeny tiny earbuds, but these are meant to sip power for a long time, so that tracks.

Opening up the Tile Mate, Galaxy SmartTag, and Apple AirTag.
Battery replacement marks the end of the user-serviceable portion of all these devices—from here, we’ll need more than our fingers.
The Tile and SmartTag come apart readily with a spudger and a splash of heat, while the AirTag requires more persuasion. That said, Apple showed surprising restraint in sealing the AirTag. It’s no tool-free wonderland, but three clips and some glue isn’t too bad. It helps to squeeze the AirTag gently with a vise to open up the seams a bit—from there, a poke from a plastic pick convinces it to come apart. If you plan to venture this far into an AirTag, tread carefully! The gluey clips are prone to break rather than release. 
Samsung’s SmartTag is the only tracker here with no official ingress protection rating, which is surprising, considering it has the thickest adhesive barrier protecting its circuit board. Worst of all possible worlds? Or just Samsung being careful not to promise too much, à la iPhone 6S?
Apple refuses to speak easy

It’s circles all the way down as you head inside the AirTag. Did you notice the “button” on the underside of the cover? That’s not a clickable button, like the Mate and SmartTag have, but rather the magnet we saw earlier in the X-ray. It sits right inside the donut-shaped logic board, nested into a coil of copper to form a speaker. You read that right—the AirTag’s body is essentially a speaker driver. Power is sent to the voice coil, which drives the magnet mounted to the diaphragm—in this case, the plastic cover where the battery lives—which makes the sounds that lead you to your lost luggage. 
But why bother putting a real driver in here at all? Magnets not only add weight, they take up a lot of space. The dinky piezoelectric speakers in the Mate and SmartTag made just as much, if not more, noise in our testing, so pure volume isn’t the answer. Looks like one corner Apple refused to cut on this tiny disk is sound quality. Piezo speakers are tiny and cheap, and sound like it—we’re talking McDonald’s happy meal speakers here. Knowing Apple, and knowing how seriously they take their noisemakers, sound quality can never be compromised, not even here.

Prying and Opening Tool Assortment
Assorted prying tools for all types of enclosure opening, cable unhooking, digitizer removal and more. A complete set of opening tools all in one kit, perfect for electronic repairs. For professionals and beginners alike.
$9.95 On Sale
$9.95
Shop Now
No loophole? We found a loophole
Ready for a teardown intermission? Unlike the keychain-ready competition, the AirTag’s perfectly round exterior provides no place for you to thread a keyring—at least not easily. The official method to attach one of these to your keys is (wait for it): purchase accessories. But if you can hold a drill steady—and are willing to take a $29 risk—we’ve got a DIY hack for you.
After some reconnaissance inside our first AirTag, we grabbed a 1/16” drill bit and carefully punched a hole through the second tracker in our four-pack—after removing the battery, of course. We miraculously managed to avoid all chips, boards, and antennas, only drilling through plastic and glue. The best part? The AirTag survived the operation like a champ and works as if nothing happened. 

If you like it, put a (key) ring on it. Just make sure you remove the battery first. And don’t expect it to maintain its IP67 capabilities.
Amazingly, the sound profile didn’t seem to change much: measuring the decibel level  at one iPhone-Mini-length away from the AirTag, the Hole-y One™ was within a +/- 1 dB margin of error from a brand new ‘Tag (about 78-80 dB). Considering Apple is using the plastic dome itself as the speaker diaphragm, this comes as a pleasant surprise.
One last warning before we share our drilling secrets: attempt this at your own risk! Drilling in the wrong place can cause serious damage, so don’t try this at home unless you’re willing to potentially turn your tracker into a very light paperweight. With that out of the way, here’s a hastily-masked video demonstration of the “safe zones” as we see them.

To drill through your AirTag safely, you’ll need to bore through one of the notches in the circuit board / antenna shield (more on those parts coming soon!) made for the clips that hold the tag together. We’ve highlighted the three notches in the video above. You can see they roughly correspond to the clips for the metal battery cover, so you can sort of use those as a guide. In a perfect world you’ll miss the clip itself (like we happened to) and only go through glue, but if you do go through a clip, it isn’t the end of the world—or your AirTag.
While Apple sells an AirTag holder for $13, and cheaper third-party models are already filling up online store listings, a DIY hole gets an AirTag onto a keyring or loop with as little extra space and mass as possible. Even in the tiniest single-purpose device, there is room to hack, and we’ll fight for your right to do it.
Don’t get bored, we’ve got boards

The Tile (left) and Samsung (right) offerings give up their boards almost too easily, while the AirTag taunts us from a distance.
Now that we’ve talked batteries and had our curiosity hole-y satisfied with a little drilling, it’s on to the brains of the operation: the boards themselves. The Mate’s motherboard (left) is a handsome black, and rests in a molded plastic frame, lifting right out. The SmartTag by Samsung (right) is the only tracker of the three to use any screws: two of them secure the board. That somewhat subverts expectations given Samsung’s infatuation with glue.

The AirTag is the feistiest of the three when it comes to giving up the gold. It’s stubbornly glued in place, and there’s not a lot of safe harbor for a pick. A delicately soldered antenna housing surrounds the board, and a very fragile copper voice coil lines the middle of the donut. The board is clearly designed to stay put. If you’re following in our footsteps and made it this far, it’s probably not to fix anything.

Like an ogre many Apple products, the AirTag board is layered. At left is the whole assembly as seen from the top, with the copper voice coil in the center, still attached via two solder joints. The board nests inside a gilded plastic antenna frame, which we’ve flipped over for a better look (center, with voice coil removed); and on the far right we’ve got the underside of the board, where the heavy hitters live.

The first side of AirTag’s logic board, home to a Bosch Sensortec BMA28x 3-axis accelerometer—also seen in other Apple products.
Side one of the board is home to a 3-axis accelerometer, battery contact pins, and those voice coil solder points, which work with the aforementioned magnet to make the Tag speak. 

Beneath those utilities, on the flip side of the board, we find these chips, sensors, and other teensy contraptions:
	•	Apple U1 ultra-wideband transceiver
	•	Nordic Semiconductor nRF52832 Bluetooth low-energy SoC w/NFC controller
	•	GigaDevice GD25LE32D 32 Mb serial NOR flash
	•	Maxim Integrated MAX98357B class AB digital audio amplifier
	•	Texas Instruments TLV9001  1-MHz, rail-to-rail I/O operational amplifier
	•	ON Semiconductor FPF2487 over-voltage protection load switch
	•	Texas Instruments TPS62746 300 mA DC-DC buck converter
	•	Likely ON Semiconductor DC-DC converter
	•	Likely Texas Instruments DC-DC converter
Apple made a lot of noise in their AirTag announcement about the lengths they have gone to ensure this tracker meets their privacy standards. To prevent malicious use, an iPhone will alert its user if an AirTag not registered to their iCloud account seems to be following them. Additionally, an AirTag separated from its owner for an extended period of time will play a sound when moved to draw attention to it. 
So, back to speaking—what if a malicious someone disabled the speaker in an AirTag before sending it off to track? We investigated, and feel it’s important to share: there are a couple relatively easy ways to disable the speaker and keep the AirTag functional. For obvious reasons we’re not going to get into how one would accomplish this. But it’s something to keep in mind—especially considering that not everybody has an iPhone that can be notified about a “muted” AirTag following them. By way of comparison, the piezoelectric speakers in the Tile Mate and Galaxy SmartTag are equally easy to disable, though they don’t seem to tout the same security features.
We found the end of the teardown
While we can’t say why the AirTag took so long to get to market, we can say a lot of care was taken to get it done right. This doesn’t look like a first generation product. Can improvements be made? Probably, but looking at the market standard Tile, the AirTag looks every bit as well-thought-out. Compared to Samsung’s offering, the AirTag is a slick, futuristic EVE to SmartTag’s clunky, but functional Wall-E.
Speaking of improvements, while Apple likes products that “just work,” sometimes they need a little help making them work for real humans. Turns out the DIY keyhole is pretty feasible and won’t rob you of features (other than ingress protection, but a couple dabs of Sugru should help remedy that). On the flipside, one of AirTag’s headline security features was pretty easy to DIY disable—a grim reminder of how digital privacy and security remain an endless, uphill effort these days.
So which tracker wins the prize? Hardware-wise it’s somewhat of a wash, but if you rock an iPhone 11 or better (minus the iPhone SE 2020), the AirTag’s added UWB pointing functionality is a nice plus. Repairability-wise, they’ve all got replaceable batteries and not much else—could be worse! The AirTag looks the most impressive to be sure, and has a slick speaker setup. To each their own, but we think Apple’s on the right track.
Which trackers did we miss? How many trackers do you use, and how long are they lasting? Show us your newly holed AirTags, and keep your eyes open for more spring teardowns to come!

Recent Stories
