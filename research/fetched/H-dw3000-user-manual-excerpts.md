# Qorvo/Decawave DW3000 User Manual v1.1 (2019) - excerpts

Source PDF: https://raw.githubusercontent.com/br101/zephyr-dw3000-decadriver/master/doc/DW3000_User_Manual.pdf (255 pp)
Fetched: 2026-09-03

## 1.1 About the DW3000 (feature list + variant table)
```

1 Introduction
1.1       About the DW3000
The DW3000 is a family of fully integrated low power, single chip CMOS radio transceivers IC implementing
HRP UWB PHY as specified by the IEEE802.15.4 standard [1], including the BPRF mode specified by the
IEEE802.15.4z amendment [2]. There are currently two versions a non-PDoA and an PDoA device with
0xDECA0302 and 0xDECA0312 device identifiers respectively.

•     Supports UWB channels 5 and 9 (6489.6 MHz and 7987.2 MHz)
•     Supports 2-way ranging, TDoA and optionally PDoA location schemes
•     Low external component count
•     Supports enhanced Time-of-Flight security modes
•     Integrated AES CCM* and AES GCM 128/192/256 functionality
•     Worldwide UWB Radio Regulatory compliance
•     Low power consumption (suitable for coin cell battery powered applications)
•     Data rates of 850 kb/s, and 6.8 Mb/s.
•     Packet length from zero to 1023 octets.
•     Integrated MAC support features
•     Up to 38 MHz SPI interface to host MCU
•     Provides precision location and data transfer simultaneously
•     Asset location to an accuracy of 10 cm
•     High multipath fading immunity
•     Supports high tag densities in RTLS
•     QFN40 (5mm x 5 mm) and WLCSP52 (3.1 mm x 3.5 mm) package options



                                          Table 1: DW3000 variants

                                                                           Operating
                      IC Variant   Type of package     PDoA support
                                                                          Temperature

                      DW3110          WLCSP52                   No

                      DW3120          WLCSP52               Yes

                                                                         -40℃ to +85℃
                      DW3210           QFN40                    No


                      DW3220           QFN40                Yes




    © Decawave Ltd 2019                           Version 1.1                                Page 7 of 255
   DW3000 User Manual


1.2       About this document
```

## 11 Location schemes (TDoA vs ToF vs PDoA)
```
There are three general methods of doing location. These are time difference of arrival (TDoA) based
location, time of flight (ToF) based location and Phase Difference of Arrival (PDoA). The main operational
points of each are outlined below. In either case the calculation of location, combining measurements from
multiple anchors, is typically done by a software functionality called the central location engine.

Time of flight location requires two-way communication from the mobile node (tag) to each of the anchor
nodes in its vicinity. Periodic message exchanges are used to measure the round trip delay and hence
calculate the one way flight time between tag and anchor. The ToF times multiplied by the speed of light
(and radio waves) gives the distance between the tag and the anchor. Each distance estimate defines a
spherical surface, centred on the anchor, on which the tag must lie. The tag’s 3D location is yielded by the
intersection of the spheres resulting from ToF measurements to the four anchors.

In time difference of arrival (TDoA) location the mobile tag blinks periodically and the blink message is
received by the anchor nodes in its vicinity. When the anchor nodes have synchronised clocks so that the
arrival time of the blink message at all nodes can be compared, then for each pair of anchors the time
difference in the arrival of the blink message defines a hyperbolic surface on which the sending tag must lie.
The tag’s 3D location is yielded by the intersection of the hyperbolic surfaces defined by the TDoA of the
blink at four pairs of anchors.

Phase Difference of Arrival involves determining the phase difference at which the radio signal from the tag
arrives at the anchor relative to a predefined direction. By measuring PDoA at a number of anchors whose
position is known the source of the transmission can be determined. For low power RTLS deployments the
TDoA scheme has benefits in that the tag needs to only send a single message in order for it to be located.
In contrast in the ToF scheme the tag has to send and receive multiple messages with multiple anchors, and
it needs to know what anchors are in the vicinity so it can address each of them in turn correctly. ToF does
not need synchronised anchors, and may suit the case where a hand held device calculates its own location
as part of a navigation system. The TDoA is a lower power solution as there are fewer messages involved,
and this also suits higher density deployments. The TDoA anchor clock synchronisation may be achieved via
a wired clock distribution. Alternatively there are wireless techniques for clock synchronisation. Wired
synchronisation may suit higher tag densities as it allows anchors to listen all the time so no tag blinks are
missed or collide with the wireless clock sync messages (potentially disrupting synchronisation). Anchors
should be wired for power and also with Ethernet to communicate the arrival times to the central location
engine.

 © Decawave Ltd 2019                              Version 1.1                                  Page 246 of 255
   DW3000 User Manual


Two-way ranging (ToF) is good for proximity detection and separation alarms, especially when both parties
in the exchange are mobile nodes.

In an RTLS the accuracy of the DW3000’s RX timestamps can give sub 10 cm resolution. Note, however that
the geometry of anchors with respect to the tag can smear the accuracy of the calculated location when
individual measurements are combined. Having additional anchors in range of the tag can offset this if it
allows the system to select anchors with best geometry and best receive signal quality with respect to the
tag being located.




 © Decawave Ltd 2019                            Version 1.1                                 Page 247 of 255
   DW3000 User Manual

```

## 12 Two-way ranging appendix (SS-TWR / DS-TWR)
```
Transmission timestamp and 3.3 – Delayed transmission for details of this.

In all of the schemes that follow one node acts as Initiator, initiating a range measurement, while the other
node acts as a Responder listening and responding to the initiator, and calculating the range.

12.2 Single-sided two-way ranging
Single-sided two-way ranging (SS-TWR) involves a simple measurement of the round trip delay of a single
message from one node to another and a response sent back to the original node.

                                                        Tround
                       Device A                                                      time
                              TX                                      RX



                                           Tprop                             Tprop

                       Device B
                                RX                                   TX
                         RMARKER                        Treply


                                     Figure 31: Single-sided two-way ranging

The operation of SS-TWR is as shown in Figure 31, where device A initiates the exchange and device B
responds to complete the exchange and each device precisely timestamps the transmission and reception
times of the packets, and thus can calculate times Tround and Treply by simple subtraction. And the resultant
time-of-flight, Tprop may be estimated by the equation:

                                                     1
                                             𝑇̂𝑝𝑟𝑜𝑝 = (𝑇𝑟𝑜𝑢𝑛𝑑 − 𝑇𝑟𝑒𝑝𝑙𝑦 )
                                                     2

The times Tround and Treply are measured independently by device A and B using their respective local clocks,
which both have some clock offset error eA and eB from their nominal frequency, and so the resulting time-
of-flight estimate has a considerable error that increases as Treply increases. DW3000 however is able to
measure the clock offset of the remote transmitter, (see REG_DRX_DIAG3), and this may be used to
compensate for that error, using the modified equation below, to produce results that are as good as can be
achieved using DS-TWR where the reply times are not too long, (i.e. < 5 ms).

                                                 1
                                      𝑇̂𝑝𝑟𝑜𝑝 =     (𝑇    − 𝑇𝑟𝑒𝑝𝑙𝑦 (1 − 𝐶𝑜𝑓𝑓𝑒𝑠𝑡 ))
                                                 2 𝑟𝑜𝑢𝑛𝑑
 © Decawave Ltd 2019                                   Version 1.1                             Page 248 of 255
   DW3000 User Manual


12.3 Double-sided two-way ranging
        Using four messages

Double-sided two-way ranging (DS-TWR) is an extension of the basic single-sided two-way ranging in which
two round trip time measurements are used and combined to give a time-of-flight result which has a
reduced error even for quite long response delays.

                                  Tround1                                                      Treply2
        Device A                                                                                                                time
                TX                             RX                        RX                              TX



                          Tprop                               Tprop                   Tprop                             Tprop

        Device B
                 RX                          TX                         TX                                RX
          RMARKER                 Treply1                                                      Tround2


                       Figure 32: Double-sided two-way ranging with four messages

The operation of DS-TWR is as shown in Figure 32, where device A initiates the first round trip measurement
to which device B responds, after which device B initiates the second round trip measurement to which
device A responds completing the full DS-TWR exchange. Each device precisely timestamps the transmission
and reception times of the messages.

        Using three messages

The four messages of DS-TWR, shown in Figure 32, can be reduced to three messages by using the reply of
the first round-trip measurement as the initiator of the second round-trip measurement. This is shown in
Figure 33.

                                                    Tround1                     Treply2
                   Device A                                                                                      time
                          TX                                   RX                         TX



                                            Tprop                       Tprop                            Tprop

                   Device B
                            RX                                TX                           RX
                      RMARKER                       Treply1                     Tround2


                       Figure 33: Double-sided two-way ranging with three messages

The resultant time-of-flight estimate, Tprop, in both the three and four message cases may be calculated using
the expression:

                                                (𝑇𝑟𝑜𝑢𝑛𝑑1 × 𝑇𝑟𝑜𝑢𝑛𝑑2 − 𝑇𝑟𝑒𝑝𝑙𝑦1 × 𝑇𝑟𝑒𝑝𝑙𝑦2 )
                                   𝑇̂𝑝𝑟𝑜𝑝 =
                                                (𝑇𝑟𝑜𝑢𝑛𝑑1 + 𝑇𝑟𝑜𝑢𝑛𝑑2 + 𝑇𝑟𝑒𝑝𝑙𝑦1 + 𝑇𝑟𝑒𝑝𝑙𝑦2 )
```
