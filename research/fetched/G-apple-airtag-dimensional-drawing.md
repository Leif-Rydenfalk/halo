# Apple — AirTag Dimensional Drawing (official)

Source: https://developer.apple.com/download/files/accessories/dimensional-drawings/airtag.pdf
Index page: https://developer.apple.com/accessories/dimensional-drawings/
Fetched: 2026-09-03. Drawing title block: "Apple Inc. | METRIC | DIMENSIONS ARE IN MILLIMETERS | THIRD ANGLE PROJECTION | SIZE D | SCALE NONE | TITLE: AirTag".
Drafter/designer date stamp: 04/20/21. PDF footer: "2021-04-23 | Copyright (c) 2026 Apple Inc. All Rights Reserved."

NOT REDISTRIBUTED. Apple's notice on the sheet reads: "NOTICE OF PROPRIETARY PROPERTY: THE INFORMATION CONTAINED HEREIN IS THE PROPRIETARY
PROPERTY OF APPLE INC. THE POSSESSOR AGREES TO THE FOLLOWING: (I) TO MAINTAIN THIS DOCUMENT IN CONFIDENCE (II) NOT TO REPRODUCE OR COPY IT
(III) NOT TO REVEAL OR PUBLISH IT IN WHOLE OR PART (IV) ALL RIGHTS RESERVED".
Only the extracted numeric dimensions are recorded here; the PDF itself is left in the scratchpad and must be re-downloaded from Apple by anyone who needs it.

## Notes block (transcribed from the sheet)

    NOTES: (UNLESS OTHERWISE SPECIFIED)
    [1] CASE SHOULD NOT OBSTRUCT ACOUSTIC AREA
    [2] ANTENNA KEEPOUT AREA. TO MAXIMIZE ANTENNA PERFORMANCE, NO METAL SHOULD
        BE CLOSER THAN THIS RADIAL KEEPOUT INCLUDING ABOVE AND BELOW THE DEVICE,
        MINIMIZE METAL OUTSIDE THE KEEPOUT AS WELL

    [1] SPEAKER KEEPOUT.
        DO NOT OBSTRUCT THIS AREA
        (Ø 25.75)

    Ø 37.31  [2] ANTENNA KEEPOUT AREA

## Plan view (steel-cover side) — concentric diameters, outermost first

    Ø 31.87   outer edge of the white shell (max OD; Apple's spec sheet rounds this to 31.9 mm)
    Ø 28.94   next step in
    Ø 27.84
    Ø 27.90
    Ø 25.55   innermost called-out circle

## Section / elevation view — Z ordinates from the datum

    0.00  (boxed datum, lowest point of the steel battery cover, on the axis)
    0.88
    0.94
    1.84
    1.89
    2.29
    7.98  (overall height; Apple's spec sheet rounds this to 8.0 mm)

    Ø 23.11              (diameter callout on the band between z = 1.89 and z = 2.29)
    0.05 CHAMFER ALL AROUND

## DETAIL A — "PROFILE ALL AROUND"

An ordinate-dimensioned profile of the full half section, vertical scale exaggerated.

Z ordinates (36 values, bottom to top):
0.00, 0.01, 0.02, 0.05, 0.08, 0.13, 0.19, 0.26, 0.33, 0.42, 0.52, 0.63, 0.75, 0.88,
2.29, 2.75, 3.38, 4.17, 4.98, 5.67, 6.18, 6.55, 6.82, 7.03, 7.20, 7.33, 7.44, 7.54,
7.62, 7.69, 7.75, 7.81, 7.85, 7.89, 7.92, 7.95, 7.95, 7.96, 7.97, 7.98

Radial ordinates (two interleaved rows on the sheet):
row A: 0.13, 0.58, 1.23, 1.97, 2.75, 3.55, 4.36, 5.18, 6.00, 6.83, 7.65, 8.48, 9.30,
       10.13, 10.96, 11.78, 12.61, 13.44, 14.27, 15.10, 15.93
row B: 0.00 (boxed), 0.24, 0.77, 1.46, 3.21, 4.18, 5.16, 6.13, 7.11, 8.09, 9.07,
       10.04, 11.02, 12.00, 12.98, 13.97, 14.95, 15.93

15.93 = 31.87 / 2, i.e. the radial ordinate spans a full radius. Which end is the axis is
resolved independently by the CC-BY DXF in reference/models/airtag-classicgod/ (see
G-airtag-profile-from-dxf.md): the axis of revolution is at radial ordinate 15.93 and the
outer surface at 0.00.
