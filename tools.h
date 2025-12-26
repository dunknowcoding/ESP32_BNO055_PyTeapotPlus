/**************************************************************************
 * Libs and Globals
  
 * This repo is specially designed for YouTube channel @NiusRobotLab

 * GNU General Public License v3.0
 **************************************************************************/

#ifndef TOOLS_H
#define TOOLS_H

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <at24c256.h>

#include "config.h"

Adafruit_BNO055 bno = Adafruit_BNO055(55, BNO055_I2C_ADDR);

const char* ssid = AID;
const char* password = PWD; 
unsigned int localPort = APPORT;
IPAddress broadcastIP;
WiFiUDP Udp;

extern imu::Vector<3> quat2Deg(imu::Quaternion&);

#endif