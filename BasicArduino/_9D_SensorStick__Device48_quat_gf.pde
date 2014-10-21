

/*
  NUS - Agilent Project Team
 -- Gao Fan
 
 
 */
#include "HMC58X3.h"
#include "ADXL345.h"
#include <Wire.h>
#include "ITG3200.h"

ITG3200 gyro;
HMC58X3 magn;
ADXL345 acc;

int ledPin =  13;    // LED connected to digital pin 13

#define SAMPLING_PERIOD_MS  40 // sampling at 25 hz 

float dx, dy, dz;
int ix, iy, iz;

long gx, gy, gz;
long cx, cy, cz;

unsigned long lastUpdate=0, nextUpdate=0;
String idstr;

#define ID           (46)
#define BAUD         (57600)

#if ID == 48 
int gXoffset = -69;
int gYoffset = 29;
int gZoffset = 9;

#define MOFFX 23
#define MOFFY 5
#define MOFFZ -39

// enter the scales here
#define MSCALEX 0.9282f
#define MSCALEY 1.0f
#define MSCALEZ 0.9869f

#elif ID == 47
int gXoffset = 25;
int gYoffset = 12;
int gZoffset = 1;

#define MOFFX 23
#define MOFFY 5
#define MOFFZ -39

// enter the scales here
#define MSCALEX 0.9282f
#define MSCALEY 1.0f
#define MSCALEZ 0.9869f

#elif ID == 46
int gXoffset = -27;
int gYoffset = 8;
int gZoffset = -1;

#define MOFFX 53
#define MOFFY 13
#define MOFFZ -256

// enter the scales here
#define MSCALEX 1.0f
#define MSCALEY 0.9805f
#define MSCALEZ 0.9988f

#endif

int ISRn = 0;
void setup()
{
  pinMode(ledPin, OUTPUT); 
  digitalWrite(ledPin, HIGH);

  // initialize the serial communications:
  Serial.begin( BAUD );

  // initialize the wire (I2C)
  Wire.begin();

  acc = ADXL345();
  acc.init(ADXL345_ADDR_ALT_LOW);

  gyro = ITG3200();
  gyro.init(ITG3200_ADDR_AD0_LOW);   
  gyro.setOffsets(gXoffset, gYoffset, gZoffset);

  magn = HMC58X3();

  magn.init(false);
  delay(10);
  magn.calibrate(1, 10);
  magn.setMode(0);

  // apply calibration
  magn.setOffsets(MOFFX, MOFFY, MOFFZ);
  magn.setScale(MSCALEX, MSCALEY, MSCALEZ);

  magn.setDOR(B110);

  digitalWrite(ledPin, LOW);  

  // create ID string since its fixed
  //sendInitString();

  idstr = String(ID);
  idstr = String(idstr + '\t');

  // init time variable
  lastUpdate = millis();
}

void sendInitString()
{

  // send the initialization string for 5 seconds
  for(int i=0; i<25; i++)
  {
    // construct string
    String output = String(-ID, DEC);
    output = output + "\t11,12,13,21,22,23,31,32,33,51,61";
    Serial.println(output);
    delay(200); 
  }
}


void loop()
{
  readSensors();
  sendData();

  // determine the time for next sample
  nextUpdate = lastUpdate + SAMPLING_PERIOD_MS;

  // wait till the time is up
  while(millis() < nextUpdate);
  lastUpdate = millis();

}

void readSensors()
{
  // get values from sensors
  acc.readAccel(&ix, &iy, &iz);
  gyro.readGyro(&dx, &dy, &dz);
  //
  //  Serial.print(ix);
  //  Serial.print(',');
  //  Serial.print(iy);
  //  Serial.print(',');
  //  Serial.print(iz);
  //  Serial.print(',');
  //  Serial.print(dx);
  //  Serial.print(',');
  //  Serial.print(dy);
  //  Serial.print(',');
  //  Serial.print(dz);


  // convert to long
  gx = dx*10000;
  gy = dy*10000;
  gz = dz*10000;

  magn.getValues(&dx, &dy, &dz); 
  // convert to long
  cx = dx*10000;
  cy = dy*10000;
  cz = dz*10000;
}


void sendData()
{
  // output values
  String accelx = String(ix, DEC);
  String accely = String(iy, DEC);
  String accelz = String(iz, DEC);

  String gyrox = String(gx, DEC);
  String gyroy = String(gy, DEC);
  String gyroz = String(gz, DEC);

  String cmpx = String(cx, DEC);
  String cmpy = String(cy, DEC);
  String cmpz = String(cz, DEC);

  String timestamp = String(millis(), DEC);


  //String output = accelx + '\n';

  // form the final string
  String output = "1~";
  output = output + accelx + '~'; //1
  output = output + accely + '~'; //2
  output = output + accelz + '~'; //3
  output = output + gyrox + '~';  //4
  output = output + gyroy + '~';  //5
  output = output + gyroz + '~';  //6
  output = output + cmpx + '~';   //7
  output = output + cmpy + '~';   //8
  output = output + cmpz + '~';   //9
  output = output + "~" + timestamp + '\n'; 

  // convert it to char array
  int len = output.length();
  byte outputArr[len+1];
  output.getBytes(outputArr, len+1);

  // print out the complete string in one go
  Serial.write(outputArr, len+1);
}












