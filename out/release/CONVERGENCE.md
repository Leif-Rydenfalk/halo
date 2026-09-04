# Convergence against the real AirTag

Generated 2026-09-05. **4 open · 4 cannot determine · 3 measured but Apple's value unknown · 13 match**

| parameter | target | current | delta | state |
|---|---|---|---|---|
| Solver convergence on the antenna case | 1.0 | 1 | — | **OPEN** |
| Implied effective permittivity (physics sanity) | 0.64 to 1.56 — the band a correct model can land in for this geometry | 0.891 - | — | **OPEN** |
| Antenna substrate effective permittivity used for length | whatever the stack actually is — the point is that it was assumed | 1.573 - | — | **OPEN** |
| PCB thickness | 0.30 mm — deliberately NOT matched | 0.6 mm | — | **OPEN** |
| Sounder output at 25 cm | 60 Phon | — | — | **CANNOT DETERMINE** |
| Peer ranging error | n/a — AirTag ranges to a phone, not to another tag | — | — | **CANNOT DETERMINE** |
| Sleep current | CANNOT DETERMINE — Apple does not publish it | — | — | **CANNOT DETERMINE** |
| Battery life | 12 months | — | — | **CANNOT DETERMINE** |
| NFC coil inductance | CANNOT DETERMINE — Apple's coil not measured | 1.331 uH | target unknown | **NO TARGET** |
| Antenna radiation efficiency | CANNOT DETERMINE — Apple publishes gain, not efficiency | 72.1 % | target unknown | **NO TARGET** |
| NFC coil Q | CANNOT DETERMINE — Apple's coil not measured | 142.6 - | target unknown | **NO TARGET** |
| Bluetooth antenna resonant frequency | 2.44 GHz | 2.447 GHz | +0.006852 GHz  (0.3%) | **MATCH** |
| Find My advertisement byte layout | PASS | PASS | 0 | **MATCH** |
| Overall stack height | 7.98 mm | 7.98 mm | +0 mm  (0.0%) | **MATCH** |
| Antenna in-band match | -6 dB | -8.076 dB | -2.076 dB  (34.6%) | **MATCH** |
| PCB outline diameter (bare board) | 26 mm | 26 mm | +0 mm  (0.0%) | **MATCH** |
| Coin cell survives the transmit pulse | PASS | PASS | 0 | **MATCH** |
| Shell outer diameter | 31.87 mm | 31.87 mm | +0.004 mm  (0.0%) | **MATCH** |
| Antenna realized gain | -3.2 dBi | 0.521 dBi | +3.721 dBi  (116.3%) | **MATCH** |
| Sounder drive current model | PASS | PASS | 0 | **MATCH** |
| Unit cost at 1000 units | 10 USD | 6.09 USD | -3.91 USD  (39.1%) | **MATCH** |
| NFC tank resonance model | PASS | PASS | 0 | **MATCH** |
| Supply decoupling model | PASS | PASS | 0 | **MATCH** |
| Layer count | 4 layers | 4 layers | +0 layers  (0.0%) | **MATCH** |
