# Convergence against the real AirTag

Generated 2026-09-04. **3 open · 8 cannot determine · 2 measured but Apple's value unknown · 10 match**

| parameter | target | current | delta | state |
|---|---|---|---|---|
| Bluetooth antenna resonant frequency (round-board variant) | 2.44 GHz | 5.54 GHz | +3.1 GHz  (127.0%) | **OPEN** |
| Antenna substrate effective permittivity used for length | whatever the stack actually is — the point is that it was assumed | 1.573 - | — | **OPEN** |
| PCB thickness | 0.30 mm — deliberately NOT matched | 0.6 mm | — | **OPEN** |
| Bluetooth antenna resonant frequency | 2.44 GHz | — | source case FAILED | **CANNOT DETERMINE** |
| Sounder output at 25 cm | 60 Phon | — | — | **CANNOT DETERMINE** |
| Implied effective permittivity (physics sanity) | must exceed ~1 — a dielectric cannot speed a wave up | — | source case FAILED | **CANNOT DETERMINE** |
| Antenna realized gain | -3.2 dBi | — | source case FAILED | **CANNOT DETERMINE** |
| Peer ranging error | n/a — AirTag ranges to a phone, not to another tag | — | — | **CANNOT DETERMINE** |
| Sleep current | CANNOT DETERMINE — Apple does not publish it | — | — | **CANNOT DETERMINE** |
| Battery life | 12 months | — | — | **CANNOT DETERMINE** |
| Antenna radiation efficiency | CANNOT DETERMINE — Apple publishes gain, not efficiency | — | source case FAILED | **CANNOT DETERMINE** |
| NFC coil inductance | CANNOT DETERMINE — Apple's coil not measured | 1.331 uH | target unknown | **NO TARGET** |
| NFC coil Q | CANNOT DETERMINE — Apple's coil not measured | 142.6 - | target unknown | **NO TARGET** |
| Find My advertisement byte layout | PASS | PASS | 0 | **MATCH** |
| Overall stack height | 7.98 mm | 7.98 mm | +0 mm  (0.0%) | **MATCH** |
| PCB outline diameter (bare board) | 26 mm | 26 mm | +0 mm  (0.0%) | **MATCH** |
| Coin cell survives the transmit pulse | PASS | PASS | 0 | **MATCH** |
| Shell outer diameter | 31.87 mm | 31.87 mm | +0.004 mm  (0.0%) | **MATCH** |
| Sounder drive current model | PASS | PASS | 0 | **MATCH** |
| Unit cost at 1000 units | 10 USD | 6.09 USD | -3.91 USD  (39.1%) | **MATCH** |
| NFC tank resonance model | PASS | PASS | 0 | **MATCH** |
| Supply decoupling model | PASS | PASS | 0 | **MATCH** |
| Layer count | 4 layers | 4 layers | +0 layers  (0.0%) | **MATCH** |
