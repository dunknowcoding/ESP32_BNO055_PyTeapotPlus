/**************************************************************************
 * This arduino sketch shows how to implement BNO055 IMU sensor with 

    -  a AT24C256 EEPROM
    -  ESP32 C3 MINI

 * Based on the 'Adafruit BNO055' exmaple 'restore_offsets'
  
 * This repo is specially designed for YouTube channel @NiusRobotLab

 * GNU General Public License v3.0
 **************************************************************************/

#include "tools.h"
/********************************************
/*
    Arduino setup function (automatically called at startup)
    
    */
/********************************************/
void setup() {
  int eeAddress = 0;
  int32_t bnoID;
  bool foundCalib = false;
 
  adafruit_bno055_offsets_t calibrationData;
  sensor_t sensor;
  sensors_event_t event;
  adafruit_bno055_offsets_t newCalib;
  AT24C256 eprom(AT24C_ADDRESS_0);

  Serial.begin(115200);
  Wire.setPins(SDA, SCL);
  Wire.begin();
  delay(5000);
  Serial.println("BNO055 Sensor Test\n");
  /* Initialise the sensor */
  if (!bno.begin()) {
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }
  Serial.println("BNO055 detected, start in 5 seconds ...");
  delay(5000);
  /* Calibration */
  if (reCalib) {
    Serial.println("\nRecalibration set by user, proceed to calibrate ...\n");
  }
  else {
    eprom.get(eeAddress, bnoID);
    bno.getSensor(&sensor);
    if (bnoID != sensor.sensor_id) {
      Serial.println("\nNo Calibration Data for this sensor exists in EEPROM");
      Serial.println("Will start new calibration in 3s");
      delay(3000);
    } 
    else {
      Serial.println("\nFound Calibration for this sensor in EEPROM.");
      eeAddress += sizeof(long);
      eprom.get(eeAddress, calibrationData);
      displaySensorOffsets(calibrationData);
      Serial.println("\n\nRestoring Calibration data to the BNO055...");
      bno.setSensorOffsets(calibrationData);
      Serial.println("\n\nCalibration data loaded into BNO055");
      foundCalib = true;
    }
  }
  /* Display calibration status*/
  delay(1000);
  displaySensorDetails(); // Display some basic information on this sensor
  displaySensorStatus(); //Optional: Display current status
  bno.setExtCrystalUse(true); //Crystal must be configured AFTER loading calibration data into BNO055.
  bno.getEvent(&event);
  if (foundCalib) {  //always recal the mag as It goes out of calibration very often
    if (!skipMagCalib) {
      Serial.println("Move sensor slightly to calibrate magnetometers");
      while (!bno.isFullyCalibrated()) {
        bno.getEvent(&event);
        displayCalStatus();
        Serial.println("");
        delay(BNO055_CALIB_SAMPLERATE_DELAY_MS);
      }
    }
  }
  else {
    Serial.println("Please Calibrate Sensor: ");
    while (!bno.isFullyCalibrated()) {
      bno.getEvent(&event);
      Serial.print("Yaw: ");
      Serial.print(event.orientation.x, 4);
      Serial.print("\tPitch: ");
      Serial.print(event.orientation.y, 4);
      Serial.print("\tRoll: ");
      Serial.print(event.orientation.z, 4);
      displayCalStatus(); // Optional: Display calibration status
      Serial.println(""); // New line for the next sample
      delay(BNO055_CALIB_SAMPLERATE_DELAY_MS); //Wait the specified delay before requesting new data
      }
  }
  /* Save new calibration data to eeprom*/
  Serial.println("\nFully calibrated!");
  Serial.println("--------------------------------");
  Serial.println("Calibration Results: ");
  bno.getSensorOffsets(newCalib);
  displaySensorOffsets(newCalib);
  Serial.println("\n\nStoring calibration data to EEPROM...");
  eeAddress = 0;
  bno.getSensor(&sensor);
  bnoID = sensor.sensor_id;
  eprom.put(eeAddress, bnoID);
  eeAddress += sizeof(long);
  eprom.put(eeAddress, newCalib);
  Serial.println("Data stored to EEPROM.");
  Serial.println("\n--------------------------------\n");
  delay(500);
  if (!useSerial) {
    /* Initialise WiFi UDP */
    Serial.println("\n\n Now setting up ESP32 Access Point ... ");
    WiFi.persistent(false);
    WiFi.disconnect();
    WiFi.mode(WIFI_AP);
    WiFi.softAPConfig(local_ip, gateway, subnet);
    bool success = WiFi.softAP(ssid, password);
    if (success) {
      Serial.print("Access Point \"");
      Serial.print(ssid);
      Serial.println("\" started successfully.");
      Serial.print("AP IP Address: ");
      Serial.println(WiFi.softAPIP()); // The default IP is often 192.168.4.1
      broadcastIP = WiFi.softAPIP();
      broadcastIP[3] = 255; // Set the last octet to 255 for broadcast on the local subnet
    }
  }
}

void loop() {
  sensors_event_t event; // Get a new sensor event
  String broadcastString; // Sensor data to broadcast
  uint8_t sys = displayCalStatus(); // Calibration status
  float yaw, pitch, roll;
  imu::Quaternion quat;
  imu::Vector<3> euler;
  
  Serial.println("");
  if (useQuat) {
    /* Quaternion mode */
    quat = bno.getQuat();
    if (quat2euler) {
      /* Quaternion to Euler Angle mode */
      euler = quat2Deg(quat);
      yaw = (float)euler.x();
      pitch = -(float)euler.y();
      roll = (float)euler.z();
    }
  }
  else {
    /* Default Euler Angle mode */ 
    bno.getEvent(&event);
    yaw = 360 - (float)event.orientation.x;
    pitch = (float)event.orientation.y;
    roll = -(float)event.orientation.z;
  }
  if (sys) {
    if (!useQuat || (useQuat && quat2euler)) {
      broadcastString = "y" + String(yaw, 4) + "y "
                      + "p" + String(pitch, 4) + "p "
                      + "r" + String(roll, 4) + "r ";
      if (!useSerial) {
        Serial.printf(" Broadcasting XYZ angles to %s\n", broadcastIP.toString().c_str());
        Udp.beginPacket(broadcastIP, localPort);
        Udp.write((uint8_t*)(broadcastString.c_str()), broadcastString.length());
        Udp.endPacket();
      }
      else {
        Serial.printf("%s\n", broadcastString.c_str());
      }
    }
    else {
      broadcastString = "w" + String(quat.w(), 4) + "w "
                      + "a" + String(quat.x(), 4) + "a "
                      + "b" + String(quat.y(), 4) + "b "
                      + "c" + String(quat.z(), 4) + "c ";
      if (!useSerial) {
        Serial.printf("\nBroadcasting WXYZ quaternion to %s\n", broadcastIP.toString().c_str());
        Udp.beginPacket(broadcastIP, localPort);
        Udp.write((uint8_t*)(broadcastString.c_str()), broadcastString.length());
        Udp.endPacket();
      }
      else {
        Serial.printf("%s\n", broadcastString.c_str());
      }
    }
  }
  delay(BNO055_MEASURE_SAMPLERATE_DELAY_MS); // Wait the specified delay before requesting new data
}
