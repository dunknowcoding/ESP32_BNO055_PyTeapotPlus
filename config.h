/**************************************************************************
 * Modify this configuration header for 'bno055_udp_miniC3.ino'
  
 * This repo is specially designed for YouTube channel @NiusRobotLab

 * GNU General Public License v3.0
 **************************************************************************/

#ifndef CONFIG_H
#define CONFIG_H

/* Sensor setting*/
#define SDA 4                                      // I2C bus data pin
#define SCL 3                                      // I2C bus clock pin
#define BNO055_CALIB_SAMPLERATE_DELAY_MS (100)     // Calibration ODR: 10Hz
#define BNO055_MEASURE_SAMPLERATE_DELAY_MS (200)   // Continuous ODR: 5Hz
#define BNO055_I2C_ADDR 0x28                       // ADR-GND: 0x28,ADR-VCC: 0x29, ADR: 0x29, HID-I2C:0x40

/* User setting*/
 bool reCalib = false;                             // (Optional) true to force recalibrating bno055 on boot
 bool skipMagCalib = false;                        // (Optional) true to skip the magnetometer recalibration process, not recommended
 bool useSerial = true;                            // true to enable serial port communication, must be consistent with PyTeapot setting
 bool useQuat = true;                             // true to enable serial port communication, must be consistent with PyTeapot setting
 bool quat2euler = false;                          // true to transfrom quaternion to Euler angles, effective only when useQuat is true

/* UDP setting*/
#define AID "bno055"                               // Access Point credentials: WiFi name
#define PWD ""                                     // Password must be at least 8 characters long, or NULL for an open WiFi
#define APPORT 5555                                // Local port to broadcast

IPAddress local_ip(192,168,1,1);                   // Set IP address for AP
IPAddress gateway(192,168,1,0);                    // Set Gateway for AP
IPAddress subnet(255,255,255,0);                   // Set Subnet for AP

#endif