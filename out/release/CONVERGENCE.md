# Convergence against the real AirTag

Generated 2026-09-04. **4 open · 4 cannot determine · 3 measured but Apple's value unknown · 10 match**

| parameter | target | current | delta | state |
|---|---|---|---|---|
| Bluetooth antenna resonant frequency (round-board variant) | 2.44 GHz | 5.54 GHz | +3.1 GHz  (127.0%) | **OPEN** |
| Implied effective permittivity (physics sanity) | must exceed ~1 — a dielectric cannot speed a wave up | 0.9657 - | — | **OPEN** |
| Antenna realized gain | -3.2 dBi | -8.333 dBi | -5.133 dBi  (160.4%) | **OPEN** |
| PCB thickness | 0.30 mm — deliberately NOT matched | 0.6 mm | — | **OPEN** |
| Sounder output at 25 cm | 60 Phon | — | — | **CANNOT DETERMINE** |
| Peer ranging error | n/a — AirTag ranges to a phone, not to another tag | — | — | **CANNOT DETERMINE** |
| Sleep current | CANNOT DETERMINE — Apple does not publish it | — | — | **CANNOT DETERMINE** |
| Battery life | 12 months | — | — | **CANNOT DETERMINE** |
| NFC coil inductance | CANNOT DETERMINE — Apple's coil not measured | 1.331 uH | target unknown | **NO TARGET** |
| Antenna radiation efficiency | CANNOT DETERMINE — Apple publishes gain, not efficiency | 7.822 % | target unknown | **NO TARGET** |
| NFC coil Q | CANNOT DETERMINE — Apple's coil not measured | 142.6 - | target unknown | **NO TARGET** |
| Bluetooth antenna resonant frequency | 2.44 GHz | 2.425 GHz | -0.015 GHz  (0.6%) | **MATCH** |
| Find My advertisement byte layout | PASS | PASS | 0 | **MATCH** |
| Overall stack height | 7.98 mm | 7.98 mm | +0 mm  (0.0%) | **MATCH** |
| Board outline diameter | 31.87 mm | 31.87 mm | +0 mm  (0.0%) | **MATCH** |
| Coin cell survives the transmit pulse | PASS | PASS | 0 | **MATCH** |
| Sounder drive current model | PASS | PASS | 0 | **MATCH** |
| Unit cost at 1000 units | 10 USD | 7.17 USD | -2.83 USD  (28.3%) | **MATCH** |
| NFC tank resonance model | PASS | PASS | 0 | **MATCH** |
| Supply decoupling model | PASS | PASS | 0 | **MATCH** |
| Layer count | 4 layers | 4 layers | +0 layers  (0.0%) | **MATCH** |
