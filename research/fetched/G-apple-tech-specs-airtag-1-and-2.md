# Apple tech specs — AirTag (2021) and AirTag 2nd generation (2026)

Fetched 2026-09-03.

## AirTag (1st gen) — https://support.apple.com/en-us/111847

    Size and Weight
      Diameter: 1.26 inches (31.9 mm)
      Height:   0.31 inch (8.0 mm)
      Weight:   0.39 ounce (11 grams)

    Splash, Water, and Dust Resistance
      Rated IP67 (maximum depth of 1 meter up to 30 minutes) under IEC standard 60529

    Connectivity
      Bluetooth for proximity detection
      Apple-designed U1 chip for Ultra Wideband and Precision Finding
      NFC tap for Lost Mode

    Sensor
      Accelerometer

    Battery
      User-replaceable CR2032 coin cell battery

    Operating Temperature
      -4 deg F to 140 deg F (-20 deg C to 60 deg C)

    In the Box
      AirTag with CR2032 coin cell battery installed

    System Requirements
      Apple Account; iPhone / iPod touch with iOS 14.5 or later, or iPad with iPadOS 14.5 or later

    Accessibility
      VoiceOver, Invert Colors, Larger Text, braille displays via the Find My app

## AirTag (2nd generation) — https://support.apple.com/en-us/126203

    Size and Weight
      Diameter: 1.26 inches (31.9 mm)
      Height:   0.31 inch (8.0 mm)
      Weight:   0.42 ounce (11.8 grams)

    Splash, Water, and Dust Resistance
      Rated IP67 (maximum depth of 1 meter up to 30 minutes) under IEC standard 60529

    Connectivity
      Bluetooth for proximity finding
      Apple-designed, second-generation Ultra Wideband chip and expanded Precision Finding connectivity
      NFC tap for Lost Mode

    Speaker
      Built-in speaker   [no loudness figure is given on the spec page]

    Battery
      User-replaceable CR2032 coin cell battery

    Operating Temperature
      -4 deg F to 140 deg F (-20 deg C to 60 deg C)

    In the Box
      AirTag with battery installed

**Mechanically the two generations are dimensionally identical** — same 31.9 x 8.0 mm envelope,
same IP67, same operating range, same CR2032. The only spec-sheet difference is mass:
11 g -> 11.8 g, +0.8 g (+7%). The teardowns attribute the added mass to a physically larger
speaker voice coil and more adhesive (see G-teardown-mechanical-quotes.md).

## Battery replacement procedure — https://support.apple.com/en-me/102600 (via search snippet, 2026-09-03)

    "Press down on the polished stainless steel battery cover of your AirTag and rotate
     counterclockwise until the cover stops rotating. Remove the cover and battery.
     Insert a new CR2032 lithium 3V coin battery ... with the positive side facing up.
     You'll hear a sound ..."

Two mechanically load-bearing facts follow from that wording:
1. The door needs **press-down AND rotate** — two independent, simultaneous hand motions.
2. The AirTag **beeps the moment the cell is seated, before the cover is refitted**, so every
   battery contact is made against the cell by the PCB/carrier assembly. The steel cover is a
   retention and sealing part, not a battery terminal.
