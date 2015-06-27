import gab.opencv.*;
import java.awt.Rectangle;
import processing.video.*;

import processing.net.*; 

import procontroll.*;
import java.io.*;

ControllIO controll;
ControllDevice device;
ControllStick leftStick;
ControllStick rightStick;
ControllButton button;

OpenCV opencv;
Rectangle[] faces;
Capture video;

Client netClient;

float xgyro = 0;
float ygyro = 0;
float zgyro = 0;
double ixgyro, iygyro, izgyro = 0;
float xacc, yacc, zacc = 0;
float baro = 0;
float temp = 0;
float seaLevelPressure = 1013;
FloatList baros = new FloatList();

void setup() {
  opencv = new OpenCV(this, 640, 480);
  video = new Capture(this, 640, 480);
  size(opencv.width, opencv.height);

  //opencv.loadCascade(OpenCV.CASCADE_FRONTALFACE);  
  //video.start();
  
  
  controll = ControllIO.getInstance(this);
  controll.printDevices();

  device = controll.getDevice("Sony PLAYSTATION(R)3 Controller");
  device.printSticks();
  device.printSliders();
  device.printButtons();
  device.setTolerance(0.1f);
  
  ControllSlider sliderXL = device.getSlider("x");
  ControllSlider sliderYL = device.getSlider("y");
  
  ControllSlider sliderXR = device.getSlider("z");
  ControllSlider sliderYR = device.getSlider("rz");
  
  
  leftStick = new ControllStick(sliderXL,sliderYL);
  rightStick = new ControllStick(sliderXR,sliderYR);

  
  button = device.getButton(5);
  
  
  netClient = new Client(this, "127.0.0.1", 10001); 
}

void draw() {
//  opencv.loadImage(video);
//  image(video, 0, 0);
//  faces = opencv.detect();
  background(0);
  noFill();
  stroke(0, 255, 0);
  
  
  fill(0, 255, 0);
//  text("TCP/IP disconnected", 50, 50);
  noFill();
  
  /*
  strokeWeight(3);
  for (int i = 0; i < faces.length; i++) {
    rect(faces[i].x, faces[i].y, faces[i].width, faces[i].height);
  }
  */
  if(button != null && button.pressed()) stroke(255,0,0);
  
  
  strokeWeight(1);
  
  // drawing whiskey sign
  float stx = leftStick.getX();
  float stxr = rightStick.getX();

  pushMatrix();
  translate(320, 240);
  rotate(stx * QUARTER_PI);
  line(-320, 0, -50,  0);
  line(-50,  0, -25, 10);
  line(-25, 10,   0,  0);
  line(0,    0,  25, 10);
  line(25,  10,  50,  0);
  line(50,   0, 320,  0);
  popMatrix();

// draw stick yaw sign
  if(stxr < 0) {
    arc(320, 240, 50, 50, HALF_PI + stxr * PI, HALF_PI);
  } else {
    arc(320, 240, 50, 50, HALF_PI, HALF_PI + stxr * PI);
  }
  
  // draw metrix
  if (netClient.available() > 0) { 
    
    //background(0); 
    String inString = netClient.readStringUntil(0x0a /* LF */);
      if (inString != null) {
        println(inString);
        String[] splited = split(inString, "*");
        xgyro = radians(float(splited[0])); // to convert degree per 0.01 sec to rad per 0.01 sec
        if (abs(xgyro) > 10) xgyro = 0;

        ygyro = radians(float(splited[1]));
        if (abs(ygyro) > 10) ygyro = 0;

        zgyro = radians(float(splited[2]));
        if (abs(ygyro) > 10) zgyro = 0;

        baro = float(splited[3]);
        temp = float(splited[4]);
        
        xacc = float(splited[5]);
        yacc = float(splited[6]);
        zacc = float(splited[7]);
        float rollA = atan2(yacc, zacc);
        float pitchA = atan2(xacc, zacc);
        text(round(degrees(rollA) * 100.0) / 100.0 + " deg x", 0, 10);
        text(round(degrees(pitchA) * 100.0) / 100.0 + " deg y", 0, 20);
        
        ixgyro += xgyro;
        iygyro += ygyro;
        iygyro = iygyro * 0.02 + xacc*0.01*0.98;
        izgyro += zgyro;
      }
  }
  line(320, 300, 320, 300 + (float)iygyro * 100);
  line(320, 300, 320 + (float)izgyro * 100, 300);
  if(ixgyro < 0) {
    arc(320, 240, 50, 50, HALF_PI + ((float)ixgyro * 60), HALF_PI);
  } else {
    arc(320, 240, 50, 50, HALF_PI, HALF_PI + ((float)ixgyro * 60));
  }
  
  seaLevelPressure = 1013;
  if(baros.size() > 30){ baros.remove(0); }
  baros.append(baro);
  float baroAvg = 0;
  for (int i=0; i<baros.size(); i++) {
    baroAvg += baros.get(i);
  }
  baroAvg = baroAvg / baros.size();
  float altAvg = 44330.0 * (1.0 - pow(baroAvg / seaLevelPressure, (1.0 / 5.255)));
  
  // acc
  line(320,350,320+xacc/10.0,350);
  line(320,350,320,350+yacc/10.0);
  line(320,400,320,400+zacc/10.0);

  fill(0, 255, 0);
  text(round(baroAvg * 100.0) / 100.0 + " hPa AVG", 50, 70);
  text(temp + " deg", 50, 90);
  text(round(altAvg*100.0)/100.0 + " m approx." , 50, 110);
  line(620, 240, 620, 240 + (baroAvg - 1013.25) * 10);
  
  noFill();
  netClient.write("\n");
}

