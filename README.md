
# PyTeapotPlus for BNO055 + ESP32 C3 Supermini

---
The complete open-source code for testing BNO055 9-Axis absolute orientation IMU Sensor. This Arduino demo is specially made for YouTube channel **牛志伟机器人实验室** @[NiusRobotLab](https://www.youtube.com/@NiusRobotLab)

## In this Repo

- :white_check_mark: **PyTeapotPlus** - Improved pythonic visualization and data receiver for IMU sensors based on [PyTeapot](https://github.com/thecountoftuscany/PyTeapot-Quaternion-Euler-cube-rotation)
- :white_check_mark: **BNO055 support** - Arduino coding for BNO055 calibration and Wireless/Serial communication with PyTeapotPlus

- :white_check_mark: **EEPROM support** - Calibration data saved to AT24C256, other AT24CXX chips can be easily implemented

- :white_check_mark: **ESP32 MCU support** - Generic ESP32, ESP32-S3, ESP32-C3/C6 etc. with WiFi support

## Dependences

- OS
  -  Windows 10
  -  Anaconda
<br/>

- Arduino Libraries
  -  Adafruit BNO055 [[Github](https://github.com/adafruit/Adafruit_BNO055)]
  -  AT24C [[Github](https://github.com/stefangs/arduino-library-at24cxxx)]
<br/>

- Python Libraries
  - pygame
  - pyopengl
  - pyopengl-accelerate
  - PyWavefront
  - pyglet


## Usage

1. Install Python dependencies in Anaconda environment

```
> cd PyTeapotPlus
> pip install -r requirements.txt
```

2. Modify **`config.h`** according to your needs.
<br/>

3. Download **`bno055_udp_miniC3`** to MCU.
<br/>

4. Modify **`pyteapotplus.py`** settings to match the configurations in **`config.h`**.

 &emsp;&emsp;Or

&emsp;&emsp;Modify **`pyteapot_3dm.py`** settings to match the configurations in **`config.h`**.

5. Ensure the MCU and the sensor working properly, then execute the python scripts, reset MCU. You should see the printing of readings and relevant information from a serial monitor. Calibrate the sensor until the readings are stable without errors.

## Questions

> What does 'PyTeapotPlus/3DViewer.py' made for?

You can view 3D models, zoom in/out, rotate using mouse by setting correct directory to your model.
<br/>

> I cannot see anything using '3DViewer.py' or 'pyteapot_3dm.py'.

Yes, that happens frequently due to various numerical ranges of 3D models. If you would like to change the parameters of OpenGL, such as the viewpoint, scales and depth, please try out.
<br/>

> How can I modify the code to implement other AT24CXX chips

In **`tools.h`**, substitute `#include <at24c256.h>` by `#include <at24cxx.h>`, `xx` is the chip you want to use.
<br/>

> Have you tested the source code before pushing it here?

I only tested some of the settings, cannot guarantee 'bugs-free' though. If you find any issues, feel free to let me know.

> Can my Arduino/STM32/Raspberry Pi boards run this demo? 

This demo is designed for ESP32 boards. UDP mode will not work for dev boards without WiFi features. As some Arduino boards have onboard EEPROM (e.g., Arduino UNO R3/R4 WiFi), simply replace the 'AT24C' lib by built-in 'EEPROM.h', then modify several lines of EEPROM codes should work. The code may work with some STM32 boards. The code is not compatible with Raspberry Pi.

## (Optional) Test a Non-Adafruit/Sparkfun BNO055 Module  

:point_down: Please refer to the video @NiusRobotLab

[![BNO055 Test](https://img.youtube.com/vi/xjYgq-Zbp5E/0.jpg)](https://www.youtube.com/watch?v=xjYgq-Zbp5E)




