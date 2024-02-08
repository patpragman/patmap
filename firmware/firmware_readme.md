# firmware readme
## last update 2/7/24

This contains the firmware for the PicoLTE board.  Configure the board by changing parameters in `config.py`.
Makre sure that the same `access.txt` file is on the board too for credentials.  Tooling to come later to automate
management of this.

## update 2/8/24

Added a blinken-lights function to strobe the neopixel under error conditions.