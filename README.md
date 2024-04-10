<h1 align="center"> AutoSplit64 </h1><br>
<p align="center">
  <a href="https://gitpoint.co/">
    <img alt="SM64" title="SM64" src="https://imgur.com/B3eyq3A.png" width="168">
  </a>
</p>

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Release](#release)
- [Features](#features)
- [Quick Setup](#quick-setup)
  - [Interface](#interface)
  - [LiveSplit Server](#livesplit-server)
  - [Game Capture](#game-capture)
  - [Routes](#routes)
- [Troubleshooting](#troubleshooting)
- [Running/Building from Source](#runningbuilding-from-source)
- [Credit](#credit)
- [Contact](#contact)
- [Donate](#donate)
- [Author](#author)

## Introduction

Inspired by Gerardo Cervantes's [Star Classifier](https://github.com/gerardocervantes8/Star-Classifier-For-Mario-64), AutoSplit 64 analyzes your game capture to automate splitting.

AutoSplit64 is primarily designed for console use, and is the only officialy supported platform, however may still function for Emulator.
For details on proper emulator configuration see Giboss's [Setup Guide](https://goo.gl/PKGDn6).
Virtual Console is not supported.

## Release

[Version 0.2.6](https://github.com/Kainev/AutoSplit64/releases)

## Features

- Automatically start/reset timer on console reset
- Split on fadeout/fadein at specified star count
- Split on DDD enter
- Split on final star grab
- Split on X-Cam
- Death Detection
- Create custom routes with graphical interface
- Automatically convert LiveSplit .lss files to AutoSplit 64 routes
- SRL Mode - Prevents AutoSplit64 from detecting console resets to pass control to SRL

## Quick Setup

Download the latest release. Extract contents and run `AutoSplit64.exe`.

LiveSplit timer should start at 1.36 seconds.

### Interface

All windows and options are accessed via the right-click menu:

<p>
  <a href="https://gitpoint.co/">
    <img alt="SM64" title="SM64" src="https://imgur.com/0VEPCco.png" width="320">
  </a>
</p>

### LiveSplit Server

AutoSplit64 communicates with LiveSplit via the LiveSplit Server component. This is included in LiveSplit releases after 1.8.29.

If you are using LiveSplit 1.8.28 ot older, please download the latest version [here](https://github.com/LiveSplit/LiveSplit.Server).

Add the LiveSplit Server Component in your LiveSplit Layout.

### Game Capture

To be able to run correctly, we must let AutoSplit 64 know where to capture.

Make sure you have your capture software open (i.e., AmaRecTV), then open the Capture Editor (`Right-Click -> Edit Coordinates`):

<p>
  <a href="https://gitpoint.co/">
    <img alt="SM64" title="SM64" src="https://imgur.com/jzbFj05.png" width="1200">
  </a>
</p>

Select the desired process from the `Process` drop-down and position the `Game Region` selector as shown. Ensure you are as accurate as possible for best results.

When finished, press `Apply` to save changes.

**NOTE**<br/>
If you are using a correctly configured version of AmaRecTV as shown (with windows size at 100% `Right-Click AmaRecTV -> 100%`), the default settings should already be set appropriately.

### Routes

We must let AutoSplit 64 know when we want splits to occur. This can be done by using the Route Editor (`Right-Click -> Edit Route`) to generate route files.

A regular split will trigger when the specified number of stars have been collected, and a set amount of fadeouts or fadeins have occurred after the star count was reached, or the last split occurred.

Every time a star is collected, or a split, undo or skip is triggered, the fadeout and fadein count are reset to 0.
The Route Editor has been designed to look and function similar to the split editor found in LiveSplit to make it as familiar as possible.

**The easiest method of creating routes is to import your splits you use for LiveSplit. To do this, in the Route Editor, nagivate to `File -> Convert LSS`. Open the `.lss` file you use with LiveSplit. AutoSplit 64 will attempt to fill in as many details as possible to simplify the route creation process, however it is important you check each split to make sure it is correct.**

## Troubleshooting

If you encounter any issues, please run through all steps below.

- Check capture coordinates are correct (`Right Click -> Edit Coordinates`)
- When using TCP connection, ensure LiveSplit server is running (`Right Click LiveSplit -> Control -> Start Server')
- Check the correct route is loaded, and that the route file is accurate (i.e. correct star counts, fadeout/fadein counts)
- Make sure SRL Mode (Right Click -> SRL Mode) is disabled if you want AutoSplit64 to detect console resets
- Generate reset templates (`Right Click -> Generate Reset Templates`)
- Enlarge your game capture window if it is very small
- Make sure the captures colour settings (i.e. saturation) are default or close to default
- If using an unpowered splitter, compare the whiteness of your star select screens to other players. If it is extremely dull you may need to increase your capture brightness
- Ensure your capture is set to a 4:3 aspect ratio (or close to)

## Running/Building from Source

- **Python:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`3.6.8`<br/>
- **Dependencies:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;See `requirements.txt`<br/>
- **Build Command:** &nbsp;`pyinstaller -windowed --icon="resources\gui\icons\icon.ico" AutoSplit64.py`

## Credit

A big thanks to Gerardo Cervantes for open-sourcing his project!

**Davi Be** - Added named pipe connection mode. Manually starting the LiveSplit Server every time is no longer necessary!

## Contact

Feel free to join the [discord](https://discord.gg/Q4TrSqB)!<br/>
Bug reports may also be left on the issues page of this repository.

## Donate

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=28PJSWKT77WLL&currency_code=USD&source=url)

## Author

Synozure
