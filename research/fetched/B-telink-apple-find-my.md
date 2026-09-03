Apple Find-My - Telink wiki
Toggle navigation
Chip Series
TLSR952x Series
TLSR922x Series
TLSR921x Series
TLSR951x Series
TLSR827x Series
TLSR825x Series
TLSR8208 Series
TLSR835x Series
TLSR836x Series
IDE and Tools
Telink IoT Studio
Burning and Debugging Tools for TLSR9 Series
Burning and Debugging Tools for TLSR9 Series (Linux)
Burning and Debugging Tools for all Series
Manufacturing and Testing
Manufacturing Jigs
BQB Test Guide
RF-Test-Guide
Protocols
Bluetooth
®
Classic
Bluetooth
®
LE
Bluetooth
®
Mesh
Zigbee
Matter
Thread
2.4G Proprietary
Apple HomeKit
Apple Find-My
RF4CE
Telink Mesh
Zephyr
Solutions
Smart Lighting & Home Automation
Wireless Audio
Remote Controls
Location Services
Wearables
Eletronic Shelf Labels
Human Interface Devices
Hardware
B92 Generic Starter Kit
B91 Generic Starter Kit
B87 Audio RCU Starter Kit
B85 Mesh Starter Kit
B80 Generic Starter Kit
Chip Series
TLSR952x Series
TLSR922x Series
TLSR921x Series
TLSR951x Series
TLSR827x Series
TLSR825x Series
TLSR8208 Series
TLSR835x Series
TLSR836x Series
IDE and Tools
Telink IoT Studio
Burning and Debugging Tools for TLSR9 Series
Burning and Debugging Tools for TLSR9 Series (Linux)
Burning and Debugging Tools for all Series
Manufacturing and Testing
Manufacturing Jigs
BQB Test Guide
RF-Test-Guide
Protocols
Bluetooth
®
Classic
Bluetooth
®
LE
Bluetooth
®
Mesh
Zigbee
Matter
Thread
2.4G Proprietary
Apple HomeKit
Apple Find-My
RF4CE
Telink Mesh
Zephyr
Solutions
Smart Lighting & Home Automation
Wireless Audio
Remote Controls
Location Services
Wearables
Eletronic Shelf Labels
Human Interface Devices
Hardware
B92 Generic Starter Kit
B91 Generic Starter Kit
B87 Audio RCU Starter Kit
B85 Mesh Starter Kit
B80 Generic Starter Kit
Apple Find-My Solution
Contents
Introduction
Find My Network Architecture
Features
Resources
Introduction
The Find My Network Accessory Specification defines how an accessory communicates with Apple devices to help owners locate their accessories privately and securely by using the Find My network. The Find My app displays the location of findable items and includes additional features to protect users’ devices, such as playing sound and using Lost Mode. The Find My network accessory protocol uses Bluetooth LE as the primary transport to interact with Apple devices.
Find My Network Architecture
The accessory and the owner device generate a cryptographic key pair after Find My network pairing by Apple ID. The owner device has access to both the private and the public key, and the accessory has the public key.
An accessory subsequently broadcasts a rotating key (derived from the public key) as a Bluetooth beacon. This beacon can be picked up by nearby Apple devices enabled Find My network. The Apple devices publish the key received in the Bluetooth beacon, along with its own location encrypted using that same key, to Apple servers. Because the private key is stored only on the owner device, the location information is accessible only to the device owner. The data stored in Apple servers is end-toend encrypted, and Apple does not have access to any location information.
Features
Unwanted tracking detection
Unwanted tracking detection (UT) notifies the user of the presence of an unrecognized accessory that may be traveling with them over time and allows them to take various actions, including playing a sound on the accessory if it’s in Bluetooth LE range.
Lost mode
An owner can use the Find My app to place their accessory in Lost Mode. They can set a phone number and select a message from a predefined list.
When someone finds someone else’s lost accessory, they can access to the contact details set by the owner by using NFC or Bluetooth LE to help the owner recover the lost item.
Play sound
The Play sound feature allows users to play sound from their Apple device to locate the accessory. This action may be initiated from an owner or non-owner device:
Users can play a sound from the Find My app on an owner device.
Users can play a sound from a non-owner Apple device when a UT alert appears on that device.
The Apple device creates Bluetooth LE connections to initiate the actions.
Resources
Telink provides Apple Find-My solutions on the TLSR9 and TLSR8 series SoC platforms for developing typical applications.
Part Number
SDK
Dev Kit
Hardware Design Guide
Reference Design
TLSR827x
Please contact Telink Sales Team
B87 Generic Starter Kit
B87 Hardware Design Guideline
B87 Development Board
TLSR921x
Please contact Telink Sales Team
B91 Generic Starter Kit
B91 Hardware Design Guideline
B91 Development Board
Telink only provides the SDK and support for qualified clients with valid MFi license,
Please contact Telink Sales Team
for more details.
Copyright © 2021 Telink. All rights reserved.
Privacy Policy
×
Close
Keyboard Shortcuts
Keys
Action
?
Open this help
n
Next page
p
Previous page
s
Search