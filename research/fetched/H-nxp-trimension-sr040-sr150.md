# NXP Trimension SR150 / SR040 fact sheet + SR150 short data sheet - excerpts

Sources:
- https://iotdesignpro.com/sites/default/files/component_datasheet/ultra-wideband-IC-Datasheet.pdf (NXP fact sheet, Trimension SR150 and SR040)
- http://download.91chip.com/datasheets/NXP/SR150-datasheet.pdf (SR150 product short data sheet, Rev 1.0, 13 Oct 2021)
Fetched: 2026-09-03

## Fact sheet
```
                                                                                                        FACT SHEET
                                                                 TRIMENSION™ SR150 AND TRIMENSION SR040




SECURE ULTRA-WIDEBAND (UWB)
POSITIONING AND RANGING
OPTIMIZED FOR IoT USE CASES
Designed for fast time-to-market,
Trimension™ SR150 and Trimension SR040
ICs are dedicated IoT solutions for highly
precise positioning and secure ranging, even
in battery-powered tags used for location.

LOW RISK
• Standards-based IC from ultra-high-volume supplier
• Fully interoperable with IEEE® 802.15.4 HRP UWB
• In accordance with FiRa™ certification development

HIGH SECURITY
• Enhanced ultra-wideband ranging technique based on
  IEEE 802.15.4z
• Integrated hardware crypto accelerators for side-channel
  resilience
• Strong eSE integration, with pre-loaded applets, for
  secure use cases

PRECISE LOCALIZATION                                            EXCEPTIONAL SIGNAL STRENGTH
• 6 to 8.5 GHz, 500 MHz bandwidth per channel                   • Tx peak power: more than +10.5 dBm
• Worldwide coverage using channels 5, 6, 8, and 9              • Receiver noise figure: +4 dB
• Integrated time-of-flight (ToF), time-difference of arrival   • High Rx sensitivity: -97 dBm @ 10% PER
  (TDoA) and angle-of-arrival (AoA) algorithms
                                                                • HPRF mode for lower power, higher link budget
• Dual-Rx for AoA functionality (SR150)
                                                                Note: Performance and power numbers are indicative.
• Range accuracy (nLOS): ±10 cm
                                                                TARGET APPLICATIONS
• Software support for up to 3 antennas
                                                                • Trackers and TDoA tags (SR040)
• Support for 3D positioning using 3 antennas
                                                                • Secure, hands-free access control
• Optimized for use with CR2032 coin battery (SR040)
                                                                • Location service anchors
                                                                • Smart home control
                                                                • Consumer electronics
                                                                • Ecosystems for secure transactions (payment, transit, etc.)
FACT SHEET UWB IoT ICs TRIMENSION SR150 AND TRIMENSION SR040

LOCALIZATION WITH UWB                                                          TRIMENSION SR150 FOR IOT DEVICES AND ANCHORS
The fine ranging and positioning capabilities of UWB                           The Trimension SR150 IC is both forward and backward
technology bring precise location and convenience to a                         compatible with IEEE 802.15.4 HRP UWB. The 500-MHz
variety of use cases, including secure access control, indoor                  bandwidth, with a pulse rate of 2 ns, supports high-resolution
positioning, and device-to-device communication for item                       ranging, with LoS accuracy within a range of ±10 cm. The Tx
tracking and tag location.                                                     peak power is more than +10 dBm and the receiver noise
                                                                               figure is +4 dB.
UWB securely determines the relative position of peer
devices with a high degree of accuracy. The use of                             Delivered in a WLCSP68 package, the Trimension SR150
wideband spectrum means UWB uses little power to send                          has, at its core, an Arm® Cortex®-M33 CPU with TrustZone®.
signals and provides stable connectivity with minimal                          Integrated security hardware accelerators protect overall
interference.                                                                  operation for high-level RF security. A dual-Rx antenna
                                                                               setup enables two channels for AoA functionality, and an
UNMATCHED ACCURACY                                                             onboard CoolFlux® BSP32 DSP is used for ToF, AoA, and
Compared to other wireless technologies, including Wi-Fi®                      radar algorithms.
and Bluetooth®, which can narrow an item’s location to                         Building on IEEE 802.15.4z, the Trimension SR150 IC comes
within an area of about 150 cm under ideal conditions,                         with an added level of security, especially when used for
UWB has a location accuracy of 10 cm, and requires fewer                       access control to protect the privacy that comes with the
anchors to cover the same area.                                                exchange of access credentials. The added protections make
UWB can be used outdoors to locate objects very precisely,                     the Trimension SR150 IC more resistant to attempts to trick
down to the centimeter level, and can be used indoors,                         the system, in what’s known as a relay attack, where hackers
where GPS has difficulty operating, to extend navigation                       attempt to intercept and amplify the wireless signal and
capabilities.                                                                  thereby open a lock, even though the key is not close by.

NXP achieves excellent precision and robustness with UWB                       Several Trimension SR150 IC devices can be placed in a
and was first to offer a system-level UWB solution backed                      room as UWB anchors to help localize people and objects
by a comprehensive software offering and strong security                       as they move within the room.
integration based on NXP’s market-proven embedded
secure elements (eSEs), and near-field communication (NFC)
integration.




   Ranging with Bluetooth® LE, Wi-Fi®                           Ranging with UWB                         Ranging and localization with NXP UWB incl.
                                                                                                         angle of arrival (AoA) technology

             Device to                                                                                                  +/- deg
             be located
                                          +/- 150 cm                                   +/- 10 cm




 Measuring
 device

                                           Certainty range:
                                         Zone where device to
                                         be loacted might be,
                                        based on measurement



NXP UWB delivers exceptionally precise positioning, with or without LoS




www.nxp.com                                                                                                                                            2
FACT SHEET UWB IoT ICs TRIMENSION SR150 AND TRIMENSION SR040

TRIMENSION SR150 + EDGELOCK™ SE051W FOR                         IN ACCORDANCE WITH FIRA CERTIFICATION
SECURE USE CASES                                                DEVELOPMENT
NXP simplifies the development of secure UWB solutions          NXP is a founding member of the FiRa Consortium, a
by offering pre-integration with the EdgeLock SE051W eSE.       collaboration designed to grow the ecosystem for UWB
Cryptographic binding of the eSE and the Trimension SR150       technology so new use cases for fine-ranging capabilities
takes place in the customer’s factory, by setting up a secure   can thrive. Our deep involvement with the FiRa Consortium
channel between the EdgeLock SE051W and the TrustZone           not only gives us a leading role in FiRa activities—such as
of the Trimension SR150’s Cortex-M33. This prevents physical    the development of interoperability standards, expansion
unbinding and ensures all communication is protected. Keys      of the UWB ecosystem, and the pursuit of new use
to set up the secure channel never leave the eSE or the         cases—it also ensures that all our UWB solutions are both
TrustZone. Key generation for dynamic scrambled time stamp      interoperable and state-of-the-art.
takes place in the eSE, while the dynamic STS generation
happens in the Cortex-M33 TrustZone. The EdgeLock SE051W
can also be shared with other IoT applications running in the
device, such as secure cloud onboarding, device-to-device
authentication, device integrity protection, attestation and    THE NXP DIFFERENCE
proof-of-origin.
                                                                UWB is a natural extension of NXP’s portfolio for secure
SR040 FOR BATTERY OPERATION                                     connectivity and mobility. The secure location services
                                                                provided by our UWB technology build on the experience
The Trimension SR040 is a specialized IC for battery-operated
                                                                we’ve gained as a recognized innovator in secure wireless
IoT devices, including UWB trackers and tags. Optimized to
                                                                overall, including secure contactless applications, silicon-
work with small batteries such as a CR2032 coin cell.
                                                                based platform protection using eSEs, and the convergence
                                                                of security and connectivity using eUICCs/eSIMs.
COMPREHENSIVE SOFTWARE SUPPORT
NXP supplies all the firmware and middleware needed to          NXP is also the only true one-stop-shop for secure
```

## SR150 short data sheet - power modes / ranging cycle
```
5       Functional description
                           The SR150 can be connected to a host controller through SPI bus. SR150 is fully
                           controllable by firmware. The SR150 has its own power management Unit which is
                           supplied by the host PIMC with 1.8V. SR150 can be connected to external embedded
                           Secure element though Host (AP) using secure channel. SR150 has 2 RX and one TX
                           these can be connected via external switched to antenna matrix.

                  5.1 SYSTEM MODES
                           The SR150 has 6 power modes that are specified: Host power down mode, Deep power
                           down mode, Deep power down retention mode, Sleep, Active mode and Hardware
                           configuration Autoload. A description of the states can be found in Table 2.

Table 2. System Power states description
System power state                 Description
Active mode                        The device is running and supplied by the Platform PMU, in this mode several active
                                   states are available: Idle, TX, RX and Dual RX.
Deep power down mode (DPD)         The device is in low power mode and supplied by the Platform PMU, the memory is
retention mode                     supplied, a configured wake up can bring the device back to the Active mode, for this a
                                   firmware reload is necessary, no RF communication is possible.
Sleep                              Specific parts can be active or inactive, this sleep mode can be configured by firmware
                                   which enables several power states, no RF communication is possible.
Hard power down mode               The device is powered down and supplied by the PMU, it can by activated by the chip
                                   enable signal.
Hardware configuration Autoload The devices is supplied by the platform PMU and is loading the Hardware configuration
                                and firmware into the memory.




SR150                                    All information provided in this document is subject to legal disclaimers.            © NXP B.V. 2021. All rights reserved.

Product short data sheet                             Rev. 1.0 — 13 October 2021
COMPANY PUBLIC                                                 709010                                                                                      7 / 22
NXP Semiconductors
                                                                                                                                                                 SR150
                                                                                                                                        Ultra-Wideband Transceiver


                  5.2 State Diagram and Power modes
                                                                            PoR




                                       CE = 0                       HW_CONFIG_                   CE = 1
                                                                     AUTOLOAD
                                                                                                                                         Interruption
                                                                                                                                           on NVIC

                                                   CE = 1

                                                                 CE = 0                                                                  SWI/SWE
                                 HPD                                                                     ACTIVE                                                        SLEEP

                                                                                                                                   Wake-Up
                                                                                                                                  Source trigs

                                                                                no                              FW activate DPD


                                                                                                        Wake-Up                   yes
                                                                                                                                                 DPD
                                                                                                       Source OK


                                                                                         CE = 0


                                                                                                  CE = 0
                                                                                                                                                                      aaa-038730

                           Figure 2. SR150 power modes state diagram


                5.2.1 Power Mode Entry and Exit conditions
                           Table 3. SR150 Power state conditions
                           Power State           Entry Condition                                                             Exit Conditions
                           HPD                   Two possible methods                                                        • Assert CE to high
                                                 • Software command
                                                 • Assert CE low for > 80us
                           DPD with              • Software command                                                          Exit to HPD State:
                           memory                                                                                            • Assert CE low for > 80us
                           retention mode                                                                                    Exit to ACTIVE state:
                                                                                                                             • Wakeup timer expired
                                                                                                                             • Temperature sensor event
                                                                                                                             • SPI NSS Negative Edge, GPIO (3,5)
                                                                                                                               event
                           ACTIVE                • Enod of System Boot after wake up • Software command
                                                 • Wakeup timer expired              • Assert CE low for > 80us
                                                 • Temperature sensor event
                                                 • SPI NSS Negative Edge, GPIO
                                                   (3,5) event

                           The time required for SR150 to go into DPD from is <100us controlled by the firmware.
                           Similarly, the required time for SR150 to enter HPD state is less than 100us starting
                           for the instance that CE is de-asserted, in both modes VDD_DIG is turned OFF. The
                           Wakeup timing from DPD state is around 370 us, the wakeup form HPD state is triggered
                           once CE is asserted and takes around 380us.
                           Figure 3 shows the full system power cycle from wakeup until ranging.
SR150                                           All information provided in this document is subject to legal disclaimers.                              © NXP B.V. 2021. All rights reserved.

Product short data sheet                                    Rev. 1.0 — 13 October 2021
COMPANY PUBLIC                                                        709010                                                                                                        8 / 22
NXP Semiconductors
                                                                                                                                                  SR150
                                                                                                                               Ultra-Wideband Transceiver


                                                                                                ACTIVE                                Ranging Round




                                                                RNG_START_CMD

                                        Wake up UWB + FW loaded
                                                600 msec        IDLE
                                                                                                                DPD
                                                                             ~25 mA


                                              FW Download                              DPD Entry                    DPD wakeup
                                                                                                                    time: ~10 ms                       aaa-038731


                           Figure 3. Typical system behavior form power on to ranging


                  5.3 CPU Subsystem
                           The digital control of the device is done with an ARM® Cortex®-M33 processor (see [3]).
                           The 32-bit microcontroller implements the ARM® TrustZone extension. It is designed to
```
