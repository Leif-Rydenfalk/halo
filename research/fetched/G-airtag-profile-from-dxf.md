# AirTag revolved profile, decoded from a CC-BY DXF

Source file: `reference/models/airtag-classicgod/airtag_dimensions.dxf`
From Printables model 629265 "Yet another AirTag model." by **ClassicGOD**, licensed
**CC BY 4.0**, https://www.printables.com/model/629265-yet-another-airtag-model (fetched 2026-09-03).
The author states the model was made "to be sure that it is accurate"; every number below
reproduces a callout on Apple's own dimensional drawing, which is what makes it usable as a
redistributable stand-in for that drawing.

Coordinate convention in the DXF: **x = radial ordinate measured inward from the outer
surface** (x = 0 at the max diameter, x = 15.93 on the axis of revolution, so
`radius = 15.93 - x` and `diameter = 2*(15.93 - x)`); **y = height above the datum**
(y = 0 at the lowest point of the steel battery cover, y = 7.98 at the apex of the white dome).
This matches Apple's Detail A ordinate ranges exactly (0.00-15.93 radial, 0.00-7.98 axial).

Cross-checks that confirm the convention:
  * max radial ordinate 15.930 -> outer Ø = 2 x 15.93 = 31.86 ~ Apple's Ø31.87
  * LWPOLYLINE at x = 4.375 -> Ø = 2 x (15.93 - 4.375) = **23.11** = Apple's "Ø 23.11" callout
  * LWPOLYLINE at x = 1.460 -> Ø = 2 x (15.93 - 1.46)  = **28.94** = Apple's "Ø 28.94" callout
  * LWPOLYLINE at x = 3.155 -> Ø = 2 x (15.93 - 3.155) = **25.55** = Apple's "Ø 25.55" callout


## SPLINE  (125 points)   x -0.007..15.930   z 2.290..7.980

| x (radial ord.) | Ø (mm) | z (mm) |
|---|---|---|
| 15.930 | 0.00 | 7.980 |
| 15.598 | 0.66 | 7.977 |
| 14.935 | 1.99 | 7.968 |
| 14.272 | 3.32 | 7.960 |
| 13.609 | 4.64 | 7.954 |
| 12.946 | 5.97 | 7.933 |
| 12.282 | 7.30 | 7.909 |
| 11.621 | 8.62 | 7.883 |
| 10.963 | 9.93 | 7.850 |
| 10.301 | 11.26 | 7.820 |
| 9.636 | 12.59 | 7.776 |
| 8.978 | 13.90 | 7.726 |
| 8.319 | 15.22 | 7.678 |
| 7.656 | 16.55 | 7.621 |
| 6.999 | 17.86 | 7.558 |
| 6.339 | 19.18 | 7.483 |
| 5.679 | 20.50 | 7.398 |
| 5.024 | 21.81 | 7.308 |
| 4.369 | 23.12 | 7.202 |
| 3.720 | 24.42 | 7.070 |
| 3.077 | 25.71 | 6.912 |
| 2.443 | 26.97 | 6.725 |
| 1.825 | 28.21 | 6.489 |
| 1.236 | 29.39 | 6.185 |
| 0.702 | 30.46 | 5.793 |
| 0.278 | 31.30 | 5.284 |
| 0.032 | 31.80 | 4.669 |
| 0.015 | 31.83 | 4.006 |
| 0.236 | 31.39 | 3.379 |
| 0.647 | 30.57 | 2.859 |
| 1.169 | 29.52 | 2.453 |
| 1.460 | 28.94 | 2.290 |

## SPLINE  (70 points)   x 3.210..15.930   z 0.000..0.880

| x (radial ord.) | Ø (mm) | z (mm) |
|---|---|---|
| 3.210 | 25.44 | 0.880 |
| 3.326 | 25.21 | 0.864 |
| 3.597 | 24.67 | 0.826 |
| 3.986 | 23.89 | 0.775 |
| 4.377 | 23.11 | 0.725 |
| 4.768 | 22.32 | 0.677 |
| 5.159 | 21.54 | 0.630 |
| 5.548 | 20.76 | 0.585 |
| 5.936 | 19.99 | 0.541 |
| 6.326 | 19.21 | 0.499 |
| 6.718 | 18.42 | 0.459 |
| 7.110 | 17.64 | 0.420 |
| 7.501 | 16.86 | 0.382 |
| 7.893 | 16.07 | 0.346 |
| 8.285 | 15.29 | 0.315 |
| 8.677 | 14.51 | 0.287 |
| 9.068 | 13.72 | 0.260 |
| 9.458 | 12.94 | 0.232 |
| 9.847 | 12.17 | 0.203 |
| 10.237 | 11.39 | 0.177 |
| 10.629 | 10.60 | 0.153 |
| 11.022 | 9.82 | 0.130 |
| 11.414 | 9.03 | 0.108 |
| 11.806 | 8.25 | 0.088 |
| 12.198 | 7.46 | 0.073 |
| 12.589 | 6.68 | 0.061 |
| 12.982 | 5.90 | 0.050 |
| 13.377 | 5.11 | 0.037 |
| 13.772 | 4.32 | 0.025 |
| 14.166 | 3.53 | 0.016 |
| 14.558 | 2.74 | 0.012 |
| 14.949 | 1.96 | 0.010 |
| 15.341 | 1.18 | 0.008 |
| 15.694 | 0.47 | 0.004 |
| 15.891 | 0.08 | 0.001 |
| 15.930 | 0.00 | 0.000 |

## LWPOLYLINE  (6 points)   x 3.155..15.930   z 0.880..1.890

| x (radial ord.) | Ø (mm) | z (mm) |
|---|---|---|
| 3.205 | 25.45 | 1.890 |
| 15.930 | 0.00 | 1.890 |
| 15.930 | 0.00 | 0.880 |
| 3.205 | 25.45 | 0.880 |
| 3.155 | 25.55 | 0.930 |
| 3.155 | 25.55 | 1.840 |

## LINE  (15.930, 7.980) -> (15.930, 0.000)
    diameters: Ø0.00 -> Ø0.00 at z = 7.98

## LWPOLYLINE  (4 points)   x 4.375..15.930   z 1.890..2.290

| x (radial ord.) | Ø (mm) | z (mm) |
|---|---|---|
| 4.375 | 23.11 | 2.290 |
| 15.930 | 0.00 | 2.290 |
| 15.930 | 0.00 | 1.890 |
| 4.375 | 23.11 | 1.890 |

## LINE  (1.460, 2.290) -> (4.375, 2.290)
    diameters: Ø28.94 -> Ø23.11 at z = 2.29
