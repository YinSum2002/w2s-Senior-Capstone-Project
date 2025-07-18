# W2S Instrumentation Module

## Overview
The scope of this repo is a partial overview of the Wither Watcher System (W2S). W2S was the senior capstone project of Computer Engineering Undergrads Justin Chan and Griffin Danehy, as well as Electrical Engineers Kam Haghighi and Santino Mei.

W2S Consisted of two main componenets. The GardenHub, which was designed by Santino, and the Instrumentation Module, designed by Justin. Griffin designed the software framework for these two components to communicate, and Kam designed the mechanical hardware to host both the GardenHub and Instrumentation Module.

## Tech Stack
- Hardware: [Raspberry Pi Pico → ESP32]
- Language: MicroPython, C++
- Tools: [KiCad, ArduinoIDE]

## Roles
Justin and Griffin were the primary contributors to this codebase.
- Justin was the Firmware/PCB Engineer, and dealt primarily in designing and programming the Instrumentation Module.
- Griffin was the Software/Wireless Communications Engineer, and dealt primarily in establishing realiable connectivity between the Intrumentation Modules and GardenHub.

## Repo Notes
> ⚠️ Heads up: This repo contains a lot of experimental and test files from the development cycle, and reflects the collaborative nature of a student project. 
- The primary files for the final version of the Instrumentation Module are `duty_cycling.c` and `demoday.c`.
- Code for the GardenHub is not included in this Repo.

## Lessons Learned
Quick list of what you’d do differently, or what you took away.

## Status
- The system achieved its specs of collecting and storing data in the Instrumentation Module and sending the data via Bluetooth Low Energy to the GardenHub.
- The system did NOT achieve it's specs of having precise plant data, nor did it hit its power spec of being able to run for months without a battery change.
- The system is no longer active.
