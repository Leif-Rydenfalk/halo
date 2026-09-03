# Qorvo Ultra-Wideband FAQs (Wayback snapshot 2023-01-31)

Source: https://web.archive.org/web/20230131001459/https://www.qorvo.com/innovation/ultra-wideband/resources/faqs
Fetched: 2026-09-03 (live qorvo.com returns HTTP 429 / Vercel security checkpoint)

 Partners 
 Community Forum 
 Wi-Fi 
 Innovation Menu
 Getting Started 
 Expand All 
 Collapse All 
 Which one of your partners has a working product that I could test now?
 We have various partners with working products who may be able to help you. Please see the UWB Partners page for a searchable list of our current partners and contact them directly. 
 If you have further questions or are not able to find what you're looking for please contact us . 
 What Qorvo UWB documents are best to study the DWM1000 hardware?
 To understand the hardware we advise you to study the following documents: 
 DW1000 and DWM1000 Data Sheets. These documents explain various aspects of the DW1000 and DWM1000 like connectivity, application information, capabilities of the DW1000/DWM1000 and much more. 
 DW1000 User Manual. 
 Please see the DW1000 and DWM1000 product pages for this documentation. 
 What Qorvo UWB documents are best to study the DWM1000 software?
 Application Note APS013 ("Implementation of Two-Way Ranging with the DW1000"). This document explains the implementation of an example two-way ranging application. 
 Application Note APU001 ("Configuring the DW1000 for Data Sheet Use Cases"). This document gives directives on the DW1000 depending on the use case. 
 DW1000 User Manual. This is a 250+ page comprehensive document, but we suggest starting with Chapter 2 (Overview of the DW1000) and Chapter 12 (Two-Way Ranging). 
 In addition, we advise you to read the source code guides and/or APIs for the sample programs. This API contains various basic procedures for sending and receiving messages. 
 Please see the DW1000 and DWM1000 product pages for the software API and sample code. 
 Expand All 
 Collapse All 
 DW1000 
 Expand All 
 Collapse All 
 Is the DW1000 RoHS compliant?
 Yes, the DW1000 meets RoHS 6 requirements as specified by the 2011/65/EU RoHS2 Directive. 
 How can I minimize the carrier frequency offset between different DW1000 devices to improve receiver sensitivity?
 Minimizing the carrier frequency offset between different DW1000 devices improves receiver sensitivity. 
 The DW1000 allows trimming to reduce crystal initial frequency error. 
 For more details, see the section on Crystal Oscillator in the DW1000 Data Sheet and for registers to use see the DW1000 User Manual, Section 8.1 ("IC Calibration - Crystal Oscillator Trim"). 
 Please see the DW1000 product page for this documentation. 
 How can I configure the output power of the DW1000 transmitter?
 This can be done in software. The output power configuration and control can be altered by using register map register file 0x1E. 
 The use of this register is explained in great detail in the DW1000 User Manual and Application Note APS023 ("Transmit Power Calibration & Management"). 
 Please see the DW1000 product page for this documentation. 
 Is it possible to get quality diagnostic information from the DW1000?
 For every received frame the DW1000 receiver provides a set of frame-related diagnostic information. 
 For more information on these diagnostics and other transmit / receive error information, see the DW1000 Software API Guide and the DW1000 User Manual Chapter 4, which describes diagnostic registers. 
 Please see the DW1000 product page for this documentation. 
 Expand All 
 Collapse All 
 DWM1000 
 Expand All 
 Collapse All 
 Is the DWM1000 certified e.g. by FCC, CE, ETSI?
 As there is no microprocessor on the DWM1000 module, it cannot be certified as shipped by Qorvo because its mode of operation is not defined. The mode of operation is defined only when a customer connects a microprocessor and programs the module as part of their end application. 
 Is the DWM1000 RoHS Compliant?
 Yes, the DWM1000 meets RoHS 6 requirements as specified by the 2011/65/EU RoHS2 Directive. 
 What kind of tests has the DWM1000 been through during production?
 As part of the DWM1000 production, the crystal has been trimmed and its trim value is stored in the OTP. TX power and RX sensitivity are tested but not calibrated. Further information can be found in the DW1000 User Manual, Chapter 8 ("DW1000 Calibration"). 
 Please see the DW1000 product page for this documentation. 
 Expand All 
 Collapse All 
 EVK1000 / EVB1000 
 Expand All 
 Collapse All 
 Is it possible to access the raw positioning data from EVB1000 (EVK1000)?
 The EVK1000 application outputs ranging and some debug information over the virtual COM port. 
 For more information, please see the Decaranging Source Code Guide. 
 Can the USB port be used to program the ARM microprocessor on the EVB1000?
 The EVB1000 does not support reprogramming of the on-board STM32F microcontroller via USB. The EVB1000 has a 20-pin JTAG header which should be used to do this. 
 Is it possible to output the distance measured by the EVB1000 via UART or SPI?
 The EVB1000 has no physical UART interface. EVB1000 outputs the results of two-way ranging over the USB port and also to the LCD display. The on-board STM32F microcontroller does have an UART peripheral. To enable UART functionality on the EVB1000, both software and hardware changes are required to use this peripheral and output data on it. Please contact Qorvo for details on how to do this. 
 Moreover, the DW1000 SPI interface is accessible through the J6 connector. For further information, see the EVK1000 User Manual for the use of the external SPI. Also, the on-board USBtoSPI application can be used to read/write data to the DW1000. Please see the DecaRanging Source Code Guide for more information on using the USB VC protocol to write and read DW1000 SPI data. 
 For which channel is the EVK1000 calibrated?
 EVK1000 boards are calibrated for the default use cases of channel 2 and 5 to have output powers of just below -41.3 dBm/MHz at the SMA connection point. 
 For more details see the EVK1000 User Manual, available on the EVK1000 product page. 
 Expand All 
 Collapse All 
 Antenna 
 Expand All 
 Collapse All 
 Is antenna delay calibration affected by temperature?
 Antenna delay does vary with temperature. Consult the DW1000 User Manual where the following is quoted: 
 "For enhanced ranging accuracy the ranging software can adjust the antenna delay to compensate for changes in temperature. Typically the reported range will vary by 2.15 mm / ?C and by 5.35 cm / VBATT." 
 The DW1000 User Manual is available on the DW1000 product page. 
 What is the difference between antenna supplied with the EVK1000 and the antenna on the DWM1000?
 The antenna supplied with the EVK1000 and the Partron chip antenna supplied with the DWM1000 are both omnidirectional antennas. The gain of both antennas is frequency dependent with the gain of the EVK1000 antenna higher than the Partron antenna. 
 Information on the DWM1000 antenna radiation pattern data as measured by Qorvo can be found in the DWM1000 Data Sheet available on the DWM1000 product page. 
 Is there a specific value for antenna delay calibration?
 Antenna delay is a generic term used to refer to: 
 the delay between the time a signal arrives at the receiving antenna and the time the arriving message is time-stamped inside the DW1000 
 the delay between the time an outgoing message is time-stamped inside the DW1000 and the time the signal leaves the antenna 
 Antenna delay will vary slightly between different units of the same design. Depending on the accuracy you require you may decide that you do not need to calibrate out this inter-unit difference. Further information on antenna calibration can be found in Application Note APS014 ("Antenna Delay Calibration of DW1000-Based Products and Systems") and Application Note APS012 ("Production Tests for DW1000-Based Products"). 
 Expand All 
 Collapse All 
 Performance of DW1000-Based Systems 
 Expand All 
 Collapse All 
 How many times per second do the anchor and tags send / measure distance?
 In Qorvo's demonstration application, the tags and anchors use the Two-Way Ranging protocol to exchange messages and calculate range/distance between them. To calculate a single range a minimum of 3 messages are needed. If the tag needs to be told of the range result, then either this information can be sent via the next response message or an additional 4th message can be used (e.g. ToF report). 
 DW1000 supports various data rates and preamble combinations. Depending on the preamble length and data rate used, a single message can vary between 190 µs (6.81 Mbps, 27 bytes, 128 preamble) to 3.4 ms (110 kbps, 27 bytes, 1024 preamble). This means that time to calculate a single range can vary from couple of milliseconds to tens of milliseconds. 
 In TDoA systems the blink frame (with preamble length of 64-symbols) and 12 octets of message payload, is around 110 µs. This means that RTLS system can support 1700 blinks per second for 1 device or 170 blinks per second for 10 devices, etc. 
 For more information, please see the DW1000 User Manual Chapter 9 section on node density and air utilization. This document is available on the DW1000 product page. 
 How many tags can be supported in a DW1000-based RTLS system?
 This depends on the RTLS scheme employed, the tag blink rate, the message duration per tag and a number of other factors including: 
 Data rate; 
 Number of data bytes; 
 Preamble length; 
 For more information, please see the DW1000 User Manual Chapter 9 section on node density and air utilization. This document is available on the DW1000 product page. 
 If a tag blinks and two different anchors respond at the same time, then there is chance of a collision. Is there any way to avoid on-air message collisions?
 It may not be necessary to take any avoiding action depending on the tag density and the tag update rate. If these are sufficiently low then the probability of collisions will be very low and ALOHA-type access rules can be employed. 
 If tag density is high and high update rates are required then you can avoid collisions between ranging exchanges by dividing time into slots (using TDMA) for each tag's activities. One of the anchors can act as a "controller" node monitoring on-air activity and assigning "allowed" transmission periods to each tag. 
 What is the power consumption of the DW1000 while transmitting / receiving?
 There are various factors which influence the power consumption of the DW1000 during transmission and reception such as preamble length, data rate, number of data bytes and so on. 
 Detailed information on power consumption in the various different DW1000 states is available in the DW1000 Data Sheet, Application Note APS001 ("DW1000 Power Consumption") and APH005 ("DW1000 Power Source Selection Guide"). These documents are available on the DW1000 product page. 
 Is communications range or ranging accuracy impacted when a tag is kept close to the body?
 The human body introduces approximately 30 dB of insertion loss so the transmitted signal from the tag will be heavily attenuated. Depending on the proximity of the tag antenna to the body the level of attenuation may be such that: 
 no signal at all is received at the intended receiver or the direct path signal is heavily attenuated and only a reflected signal is received at the intended receiver thereby giving an incorrect distance measurement 
 the direct path signal is heavily attenuated but is still received correctly at the intended receiver in which case the distance measurement will be correct. 
 Most monopole antennas are designed to operate in free space (i.e. not in proximity to the body). Proximity to the body reduces antenna efficiency and fidelity factor. This could distort the UWB pulse and thereby give an incorrect range measurement. The solution here is to design an antenna which takes the body proximity in account. Consult Qorvo for more information on this. 
 For more information on non-line-of-sight propagation see the three application notes: APS006 Part 1 ("Channel Effects on Communications Range and Time Stamp Accuracy in DW1000-Based Systems"), APS006 Part 2 ("Non Line-of-Sight Operation and Optimizations to Improve Performance in DW1000-Based Systems") and APS011 ("Sources of Error in DW1000-Based Two-Way Ranging (TWR) Schemes"). 
 These documents are available on the DW1000 product page. 
 Is it possible to read the RSSI value and if so, how can I read it?
 RSSI values can be calculated. See Chapter 4.7 (Assessing the quality of reception and the RX timestamp) in the DW1000 User manual. This document is available on the DW1000 product page. 
 Expand All 
 Collapse All 
 System Design Implementation 
 Expand All 
 Collapse All 
 We are starting our design. What hints can you provide to minimize power consumption of our DW1000-based design?
 Our Application Note APS002 ("Minimizing Power Consumption in DW1000-Based Systems") explains the different design considerations to take care of when power consumption is of importance. 
 This document is available on the DW1000 product page. 
 What is the recommended soldering profile for the DW1000 IC?
 As the package is an industry standard 48 pin QFN 6 x 6 mm with 0.4 mm pitch and exposed ground paddle, we refer customers to JEDEC specification J-STD-020.1 (March 2008). 
 Could you recommend a crystal, other than those you mention in the DW1000 datasheet?
 Qorvo and the IEEE 802.15.4a standard specify +/-20ppm crystals. Other crystals meeting this specification should also work provided the guidelines in the DW1000 Data Sheet are followed. Of course, alternative crystals should be tested before committing to a design. 
 We are starting our design. What hints could you give us to maximize the range?
 Our Application Note APS017 ("Maximizing Range in DW1000-Based Systems") which explains the different design considerations to maximize communications range. 
