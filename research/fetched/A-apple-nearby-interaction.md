# FETCHED: Apple "Nearby Interaction with UWB" + NINearbyObject API semantics

- **Source URLs:** https://developer.apple.com/nearby-interaction/ and https://developer.apple.com/documentation/nearbyinteraction
- **Date fetched:** 2026-09-03 (docs body read via Apple's own JSON API at developer.apple.com/tutorials/data/documentation/*.json, because the HTML page is a JS app)
- **Why it matters:** proves direction is computed by the *phone* about the *peer*, and that the accessory protocol is vendor-gated, not published.

## Verbatim, from developer.apple.com/nearby-interaction/

Nearby Interaction with UWB

Allow people to interact with connected accessories in completely new and exciting ways by leveraging the Ultra Wideband (UWB) chipset in a supported iPhone or Apple Watch. The Nearby Interaction framework makes it easy to integrate UWB in your apps and accessories.

App developers
Build apps that interact with accessories simply by being in close proximity to an Apple UWB-enabled product. Taking advantage of UWB allows you to create more precise, directionally aware app experiences.

Accessory manufacturers
Implement the Nearby Interaction accessory protocol with a Nearby Interaction-enabled UWB chipset to make accessories that interact with supported Apple products. Contact your UWB chipset vendor to confirm feature support.

Chipset vendors
Enable Apple UWB interoperability in your chipsets by implementing the Nearby Interaction specification.

## NINearbyObject — API members and Apple's abstracts (from the documentation JSON)

Framework abstract: "Locate and interact with nearby devices using identifiers, distance, and direction."
NINearbyObject abstract: "Location information for a peer device in an interaction session."
  - "A nearby object refers to a peer Apple device or third-party accessory."
  - "When the framework is ready to provide your app with information about a nearby object's relative position, it calls your delegate's implementation."
  - "If a session can't provide peer direction or distance, it sets the values to [nil]. In Objective-C, the session uses the [NINearbyObjectDirectionNotAvailable] and [NINearbyObjectDistanceNotAvailable] values to indicate missing direction or distance."

| member | abstract |
|---|---|
| direction | A vector that points from the user's device in the direction of the peer device. |
| distance | The distance from the user's device to the peer device in meters. |
| horizontalAngle | An angle in radians that indicates the azimuthal direction to the nearby object. |
| verticalDirectionEstimate | The estimation of a nearby object's vertical position as it relates to the user's device. |
| NINearbyObject.VerticalDirectionEstimate | Estimations of a nearby object's vertical position in relation to the user's device. |
| NINearbyObjectAngleNotAvailable | A value that indicates that a nearby object's horizontal angle is unavailable. |
| NINearbyObjectDirectionNotAvailable | A value that indicates that a nearby object's direction is unavailable. |
| NINearbyObjectDistanceNotAvailable | An object that indicates the peer's distance is unavailable. |
