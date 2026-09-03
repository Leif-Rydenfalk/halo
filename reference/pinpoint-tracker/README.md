# tracker
The PinPoint tracker module pcb and cad files

This repository contains all the KiCAD EDA files and Fusion 360 CAD designs for the PinPoint tracker modules

### Features
- nRF52832-based board - [Ebyte E73-2G4M08S1E](https://www.cdebyte.com/products/E73-2G4M08S1E/2)
- Compatible with Apple's FindMy network through [OpenHaystack](https://github.com/seemoo-lab/openhaystack)
- Small form factor (ideally less than 30x30x10mm)
- Location Pin shape
- RGB led for flair
- piezo buzzer for finding


### Repository structure
- `pcb/` contains the KiCAD EDA files for the tracker module
- `cad/` contains the Fusion 360 CAD files for the tracker module
- `docs/` contains the datasheets and other documentation for the components used in the tracker module
- `LICENSE` contains the license information for the repository
- `README.md` contains the information about the repository

### Board To-Do
- [x] battery holder
- [x] mounting holes
- [x] SWD connector
- [x] piezo buzzer
- [x] USB interface
- [x] RGB led
- [x] Push button

### License

This project is licensed under the TAPR Open Hardware License. See [LICENSE.txt](/LICENSE.txt) for more information.

