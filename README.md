# 🧭 pico-20948-poc - Motion sensor data for your project

[![](https://img.shields.io/badge/Download-Project_Files-blue.svg)](https://github.com/violetmi966/pico-20948-poc)

## 📌 Project Overview

This project provides code and instructions to connect an ICM-20948 sensor to a Raspberry Pi Pico. This sensor tracks movement, rotation, and magnetic orientation. The system uses MicroPython for simple control. You do not need complex electronics or voltage shifters. You provide 3.3V power to the sensor, and the system handles the rest. This tool serves as a proof of concept for hardware hobbyists and engineers who track physical movement.

## 🛠️ Required Hardware

To use this software, you need the following physical items:

*   One Raspberry Pi Pico microcontroller.
*   One ICM-20948 IMU sensor board.
*   A USB data cable for communication with your Windows computer.
*   Four jumper wires to connect the sensor pins to the Pico.

## 💾 Installation and Setup

Follow these steps to prepare your hardware and run the software.

1.  Visit this page to download the project files: [https://github.com/violetmi966/pico-20948-poc](https://github.com/violetmi966/pico-20948-poc)
2.  Install the Thonny Python editor for Windows. This tool allows you to send code to your Raspberry Pi Pico.
3.  Connect your Pico to your computer with the USB cable while holding the BOOTSEL button on the Pico board.
4.  Open Thonny and select the Raspberry Pi Pico from the bottom right corner of the window to install the MicroPython firmware.
5.  Extract the downloaded project folder to your desktop.
6.  Open the files in Thonny and save them to your Pico device.

## ⚡ Wiring Instructions

Correct wiring ensures the sensor communicates with the Pico. Locate the pins on both boards and connect them as described below.

*   VCC pin on the sensor connects to the 3.3V pin on the Pico.
*   GND pin on the sensor connects to any GND pin on the Pico.
*   SDA pin on the sensor connects to GP4 on the Pico.
*   SCL pin on the sensor connects to GP5 on the Pico.

Double-check these connections before plugging the USB cable into your computer. Loose wires or incorrect connections may prevent the sensor from appearing in the code.

## 🧪 Running the Software

Once you finish the wiring and transfer the files, the software performs a check on the sensor.

1.  Ensure your Pico remains connected to the computer.
2.  In Thonny, look for the file named main.py.
3.  Click the Green Run button at the top of the Thonny interface.
4.  Watch the console window at the bottom of the screen.
5.  The system reports the sensor status and displays X, Y, and Z axis values for the accelerometer and gyroscope.

If the console shows specific numbers, the system functions as expected. If the console shows an error, check your wiring connections to the Pico.

## 📊 Understanding Sensor Data

The system captures data from three separate sensors integrated into the ICM-20948 chip.

*   Accelerometer: Measures how fast the device speeds up or slows down. It detects if the sensor tips over or remains flat.
*   Gyroscope: Measures the speed of rotation around the three axes. This detects spinning or turning movements.
*   Magnetometer: Detects the strength and direction of magnetic fields. This acts as a compass for your project.

All these values update in real-time as you move the sensor. You can modify the code to save this data to a text file or use it to trigger events in other software.

## 🔍 Troubleshooting Tips

Most errors occur during the wire connection phase or the file upload phase. Use this list to solve common problems.

*   The console reports "Sensor not found": Check your GP4 and GP5 wires. Ensure the solder joints on your sensor pins remain firm.
*   Thonny does not see the Pico: Hold the BOOTSEL button longer while plugging in the USB cable. Ensure you use a data USB cable, not a cable meant only for charging.
*   Garbled text appears in the console: Verify that the firmware on your Pico matches the latest MicroPython version.
*   The sensor feels warm: Disconnect the power immediately. Check for shorts between your wires or metal objects touching the board.

## 📂 Project Structure

The repository contains a specific structure to keep the code clean.

*   /lib: Stores the specialized driver file for the ICM-20948 sensor. Do not rename or move files inside this folder.
*   main.py: This file runs automatically when the Pico receives power. It initializes the sensor and prints data to the screen.
*   boot.py: Contains settings for the initial startup sequence.
*   README.md: Provides the instructions you read right now.

## 🧱 Expanding Your Project

Because this system uses MicroPython, you can easily change how the code handles data.

*   Add a logic check to trigger an alarm if the sensor detects a tilt beyond a certain angle.
*   Send the sensor data to a computer over the Serial port for graphing in other software.
*   Create a data logger that writes motion statistics to a small SD card if you add an SD card module to your Pico.
*   Connect the Pico to an LED screen to display the orientation of your device in real-time.

Test your changes frequently by running the code in Thonny. Use the print() command to see values in the console to confirm your math logic remains correct.

## 📝 License Information

This code reaches the public as open-source material. You can modify, copy, and share these files for your own projects. Please credit the original source if you distribute the code to others. Ensure you keep the license file in the main directory if you decide to share your fork of this project.