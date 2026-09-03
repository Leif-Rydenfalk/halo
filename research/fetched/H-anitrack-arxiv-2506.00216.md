# AniTrack: Power-Efficient Time-Slotted UWB Localization (arXiv:2506.00216) - excerpts

Source: https://arxiv.org/abs/2506.00216 / https://arxiv.org/html/2506.00216v1
ETH Zurich, 2025-05-30. Fetched: 2026-09-03

```
 Abstract: Accurate localization is essential for a wide range of applications, including asset tracking, smart agriculture, and animal monitoring. While traditional localization methods, such as Global Navigation Satellite System (GNSS), Wi-Fi, and Bluetooth Low Energy (BLE), offer varying levels of accuracy and coverage, they have drawbacks regarding power consumption, infrastructure requirements, and deployment flexibility. Ultra-Wideband (UWB) is emerging as an alternative, offering centimeter-level accuracy and energy efficiency, especially suitable for medium to large field monitoring with capabilities to work indoors and outdoors. However, existing UWB localization systems require infrastructure with mains power to supply the anchors, which impedes their scalability and ease of deployment. This underscores the need for a fully battery-powered and energy-efficient localization system. This paper presents an energy-optimized, battery-operated UWB localization system that leverages Long Range Wide Area Network (LoRaWAN) for data transmission to a server backend. By employing single-sided two-way ranging (SS-TWR) in a time-slotted localization approach, the power consumption both on the anchor and the tag is reduced, while maintaining high accuracy. With a low average power consumption of 20.44 mW per anchor and 7.19 mW per tag, the system allows fully battery-powered operation for up to 25 days, achieving average accuracy of 13.96 cm with self-localizing anchors on a 600 m2 testing ground. To validate its effectiveness and ease of installation in a challenging application scenario, ten anchors and two tags were successfully deployed in a tropical zoological biome where they could be used to track Aldabra Giant Tortoises (Aldabrachelys gigantea).
 Subjects: 
```

## Key claims
```
On the other hand, Wi-Fi and BLE are more suitable mainly for indoor RTLS ( RTLS ), where the installation of anchor infrastructure is feasible [ 7 , 8 ] .
Moreover, their localization accuracy remains limited to a range of meters.
More precisely, Wi-Fi has been shown to achieve 2.4   m 2.4\text{\,}\mathrm{m} accuracy [ 9 ] , while BLE reaches accuracies around 0.5   m 0.5\text{\,}\mathrm{m} in controlled environments [ 10 ] . 
 To address these limitations, the IEEE standard for UWB , IEEE 802.15.4z [ 11 ] , is emerging as a promising alternative.
 UWB offers sub 20   cm 20\text{\,}\mathrm{cm} accuracy [ 12 ] , high robustness against interference, and reliable performance in complex environments, making it significantly more accurate than Wi-Fi- or BLE -based solutions. 
 To perform UWB localization, various approaches can be implemented, such as localization through AoA ( AoA ) measurements  [ 13 ] , TDOA   [ 14 ] , ToF ( ToF )-based methods using either SS-TWR or DS-TWR ( DS-TWR )   [ 15 ] , or any combination of those  [ 16 ] .
However, TDOA techniques require precise time synchronization among anchors, which adds complexity to the system. Similarly, AoA -based localization demands sophisticated antenna arrays and calibration, while still relying on fixed anchor infrastructure.
In contrast, SS-TWR and DS-TWR offer a more straightforward implementation without precise anchor synchronization.
Independent of the chosen approach, UWB localization systems rely on a network of anchors, typically involving a time-intensive manual deployment process.
While different solutions focused on lowering the power consumption of tags [ 17 ] , the anchors typically remain continuously active to handle localization requests from mobile tags.
This high power demand on the anchor’s side requires a constant power supply and represents a fundamental limitation for system deployment. 
 Additionally, the system must be integrated into a communication network, allowing tags and anchors to upload position data to a server efficiently.
As a result, communication plays a key role in power consumption.
With the rise of IoT ( IoT ), LoRaWAN has been proven to bridge this gap, allowing power-efficient, reliable, and scalable data collection  [ 6 ] . 
 This paper presents the design and implementation of a power-optimized and self-localizing UWB RTLS system, based on SS-TWR .
The tag initiates the localization and follows a time-slotted approach, enabling positioning updates at intervals as short as 10   s 10\text{\,}\mathrm{s} with a 2D ( 2D ) average accuracy of 13.96   cm 13.96\text{\,}\mathrm{cm} .
To ensure fast availability of localization data, the system integrates LoRaWAN for energy-efficient data transmission. In particular, this article presents the following contributions: 
 • 
 Design and implementation of a hardware and software-based, power-optimized UWB localization system with a 2D average accuracy of 13.96   cm 13.96\text{\,}\mathrm{cm} combined with real-time data upload through LoRaWAN . 
 • 
 Introduction of a time-slotted localization schedule that reduces power consumption of our system to just 20.44   mW 20.44\text{\,}\mathrm{mW} for anchors and 7.19   mW 7.19\text{\,}\mathrm{mW} for tags at a localization interval of 40   s 40\text{\,}\mathrm{s} , enabling fully battery-powered operation for 25 days. 
 • 
 A scalable system architecture, tested and characterized over an area of 600   m 2 600\text{\,}{\mathrm{m}}^{2} using five anchors. 
 • 
 Successful field deployment, monitoring the real-time location of tags in a zoological setting. 
 II Related Work 
```
