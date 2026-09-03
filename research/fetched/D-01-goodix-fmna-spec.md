# Goodix BLE Knowledge Base — "Apple Find My Technical Solution" (FMNA)

- URL: https://goodix-ble-wiki-en.readthedocs.io/latest/DesignRef/FMNA.Case/Apple%20FindMy%E6%8A%80%E6%9C%AF%E6%96%B9%E6%A1%88.html
- Fetched: 2026-09-03
- Why it matters: the clearest public statement of what an Apple-certified Find My accessory
  must contain in hardware and firmware, and how Apple's per-unit Token is provisioned.

## Required hardware (verbatim from the page)

- "Goodix Bluetooth LE SoC, external crystal (32m), and Bluetooth antenna"
- "Battery (non-rechargeable battery such as CR2032/rechargeable battery) and ADC sample battery voltage"
- "G-Sensor（I2C）"  <- accelerometer is REQUIRED (motion detection for unwanted-tracking)
- "Speaker Driver (PWM) and Speaker (piezoelectric sounder/buzzer)"

No secure element is listed. Crypto is software: "Wolfssl加解密库" (wolfSSL crypto library).

## Firmware footprint on Goodix GR551x

- Flash: "112.7 KB + 4 KB (Token saving) = 116.7 KB"
- RAM: "21.5 KB"
- Recommended parts: GR5513 (512 KB Flash / 128 KB RAM), GR5515 (1 MB / 256 KB), GR533x (512 KB / 96 KB)

## MFi / certification steps (verbatim)

1. "MFi qualification application: Only partners with Apple MFi qualification can officially start"
2. "Accessory plan submission: Submit the accessory product plan on the MFi Portal"
3. "Complete FMCA and reference implementation test cases and export test results"
4. "Contact the lab for a quote and to schedule testing services"
5. "Prepare certification materials (Bluetooth certificate, product, English manual, test firmware)"

## The Token — the actual gate on the Find My network

- "Submit the accessory product plan on the MFi Portal to get the information assigned by
  Apple, such as PPID, Token, UUID, Product Value, Product Category."
- Tokens are "issued by Apple" and must be "decoded by Base64, and stored in the accessory
  Flash through pre-burning in the factory production line."
- "every time the Token is re-paired, the Apple server will send the updated Token."

## Reading for haytag

The certified path costs: MFi membership + a PPID + per-unit Tokens burned at the factory +
lab test fees. The hardware itself is unremarkable — a mid-range BLE SoC with ~120 KB free
flash, a 32 MHz crystal, an I2C accelerometer, a PWM-driven piezo, and a coin cell.
