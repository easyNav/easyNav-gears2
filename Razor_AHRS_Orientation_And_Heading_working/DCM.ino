/* This file is part of the Razor AHRS Firmware */

// DCM algorithm

/**************************************************/
void Normalize(void)
{
  float error=0;
  float temporary[3][3];
  float renorm=0;
  
  error= -Vector_Dot_Product(&DCM_Matrix[0][0],&DCM_Matrix[1][0])*.5; //eq.19

  Vector_Scale(&temporary[0][0], &DCM_Matrix[1][0], error); //eq.19
  Vector_Scale(&temporary[1][0], &DCM_Matrix[0][0], error); //eq.19
  
  Vector_Add(&temporary[0][0], &temporary[0][0], &DCM_Matrix[0][0]);//eq.19
  Vector_Add(&temporary[1][0], &temporary[1][0], &DCM_Matrix[1][0]);//eq.19
  
  Vector_Cross_Product(&temporary[2][0],&temporary[0][0],&temporary[1][0]); // c= a x b //eq.20
  
  renorm= .5 *(3 - Vector_Dot_Product(&temporary[0][0],&temporary[0][0])); //eq.21
  Vector_Scale(&DCM_Matrix[0][0], &temporary[0][0], renorm);
  
  renorm= .5 *(3 - Vector_Dot_Product(&temporary[1][0],&temporary[1][0])); //eq.21
  Vector_Scale(&DCM_Matrix[1][0], &temporary[1][0], renorm);
  
  renorm= .5 *(3 - Vector_Dot_Product(&temporary[2][0],&temporary[2][0])); //eq.21
  Vector_Scale(&DCM_Matrix[2][0], &temporary[2][0], renorm);
}

/**************************************************/
void Drift_correction(void)
{
  float mag_heading_x;
  float mag_heading_y;
  float errorCourse;
  //Compensation the Roll, Pitch and Yaw drift. 
  static float Scaled_Omega_P[3];
  static float Scaled_Omega_I[3];
  float Accel_magnitude;
  float Accel_weight;
  
  //*****Roll and Pitch***************

  // Calculate the magnitude of the accelerometer vector
  Accel_magnitude = sqrt(Accel_Vector[0]*Accel_Vector[0] + Accel_Vector[1]*Accel_Vector[1] + Accel_Vector[2]*Accel_Vector[2]);
  Accel_magnitude = Accel_magnitude / GRAVITY; // Scale to gravity.
  // Dynamic weighting of accelerometer info (reliability filter)
  // Weight for accelerometer info (<0.5G = 0.0, 1G = 1.0 , >1.5G = 0.0)
  Accel_weight = constrain(1 - 2*abs(1 - Accel_magnitude),0,1);  //  

  Vector_Cross_Product(&errorRollPitch[0],&Accel_Vector[0],&DCM_Matrix[2][0]); //adjust the ground of reference
  Vector_Scale(&Omega_P[0],&errorRollPitch[0],Kp_ROLLPITCH*Accel_weight);
  
  Vector_Scale(&Scaled_Omega_I[0],&errorRollPitch[0],Ki_ROLLPITCH*Accel_weight);
  Vector_Add(Omega_I,Omega_I,Scaled_Omega_I);     
  
  //*****YAW***************
  // We make the gyro YAW drift correction based on compass magnetic heading
 
  mag_heading_x = cos(MAG_Heading);
  mag_heading_y = sin(MAG_Heading);
  errorCourse=(DCM_Matrix[0][0]*mag_heading_y) - (DCM_Matrix[1][0]*mag_heading_x);  //Calculating YAW error
  Vector_Scale(errorYaw,&DCM_Matrix[2][0],errorCourse); //Applys the yaw correction to the XYZ rotation of the aircraft, depeding the position.
  
  Vector_Scale(&Scaled_Omega_P[0],&errorYaw[0],Kp_YAW);//.01proportional of YAW.
  Vector_Add(Omega_P,Omega_P,Scaled_Omega_P);//Adding  Proportional.
  
  Vector_Scale(&Scaled_Omega_I[0],&errorYaw[0],Ki_YAW);//.00001Integrator
  Vector_Add(Omega_I,Omega_I,Scaled_Omega_I);//adding integrator to the Omega_I
}

void Matrix_update(void)
{
  Gyro_Vector[0]=GYRO_SCALED_RAD(gyro[0]); //gyro x roll
  Gyro_Vector[1]=GYRO_SCALED_RAD(gyro[1]); //gyro y pitch
  Gyro_Vector[2]=GYRO_SCALED_RAD(gyro[2]); //gyro z yaw
  
  Accel_Vector[0]=accel[0];
  Accel_Vector[1]=accel[1];
  Accel_Vector[2]=accel[2];
    
  Vector_Add(&Omega[0], &Gyro_Vector[0], &Omega_I[0]);  //adding proportional term
  Vector_Add(&Omega_Vector[0], &Omega[0], &Omega_P[0]); //adding Integrator term
  
#if DEBUG__NO_DRIFT_CORRECTION == true // Do not use drift correction
  Update_Matrix[0][0]=0;
  Update_Matrix[0][1]=-G_Dt*Gyro_Vector[2];//-z
  Update_Matrix[0][2]=G_Dt*Gyro_Vector[1];//y
  Update_Matrix[1][0]=G_Dt*Gyro_Vector[2];//z
  Update_Matrix[1][1]=0;
  Update_Matrix[1][2]=-G_Dt*Gyro_Vector[0];
  Update_Matrix[2][0]=-G_Dt*Gyro_Vector[1];
  Update_Matrix[2][1]=G_Dt*Gyro_Vector[0];
  Update_Matrix[2][2]=0;
#else // Use drift correction
  Update_Matrix[0][0]=0;
  Update_Matrix[0][1]=-G_Dt*Omega_Vector[2];//-z
  Update_Matrix[0][2]=G_Dt*Omega_Vector[1];//y
  Update_Matrix[1][0]=G_Dt*Omega_Vector[2];//z
  Update_Matrix[1][1]=0;
  Update_Matrix[1][2]=-G_Dt*Omega_Vector[0];//-x
  Update_Matrix[2][0]=-G_Dt*Omega_Vector[1];//-y
  Update_Matrix[2][1]=G_Dt*Omega_Vector[0];//x
  Update_Matrix[2][2]=0;
#endif

  Matrix_Multiply(DCM_Matrix,Update_Matrix,Temporary_Matrix); //a*b=c

  for(int x=0; x<3; x++) //Matrix Addition (update)
  {
    for(int y=0; y<3; y++)
    {
      DCM_Matrix[x][y]+=Temporary_Matrix[x][y];
    } 
  }
}

void Euler_angles(void)
{
  pitch = -asin(DCM_Matrix[2][0]);
  roll = atan2(DCM_Matrix[2][1],DCM_Matrix[2][2]);
  yaw = atan2(DCM_Matrix[1][0],DCM_Matrix[0][0]);

  if (firstIteration  < 600) 
  {
    offsetOrientation = yaw;
    
  }

  if(firstIteration < 601) {
     firstIteration++;
  }

}

void get_quaternion_vec() 
{
    float c1 = cos(yaw/2);
  float c2 = cos(pitch/2);
  float c3 = cos(roll/2);

  float s1 = sin(yaw/2);
  float s2 = sin(pitch/2);
  float s3 = sin(roll/2);

  w_quaternion = (c1 *c2*c3) - (s1 *s2 *s3);
  x_quaternion = (s1 *s2 *c3) +(c1 *c2 *s3);
  y_quaternion = (s1 *c2 *c3) + (c1 *s2 *s3);
  z_quaternion = (c1 *s2 *c3) - (s1 *c2 *s3);
}

void getGravity(void) 
{
  gravityOnX = 2 * (x_quaternion*z_quaternion - w_quaternion*y_quaternion);
  gravityOnY = 2 * (w_quaternion*x_quaternion + y_quaternion*z_quaternion);
  gravityOnZ = w_quaternion*w_quaternion - x_quaternion*x_quaternion - y_quaternion*y_quaternion + z_quaternion*z_quaternion;
}

void getLinearAcceleration(void)
{
  accelRealX = forwardAccel - (gravityOnX);
  //accelRealY = accel[1] - (gravityOnY*256);
  //accelRealZ = accel[2] - (gravityOnZ*256);
}

// void getEarthCoordAcceleration(void)
// {
//   float conjW = 0.0;
//   float conjX = accelRealX;
//   float conjY = accelRealY;
//   float conjZ = accelRealZ;

//   float newConjW =  w_quaternion * conjW - x_quaternion*conjX - y_quaternion*conjY -z_quaternion*conjZ;
//   float newConjX =  w_quaternion*conjX + x_quaternion*conjW + y_quaternion*conjZ - z_quaternion*conjY;
//   float newConjY =  w_quaternion*conjY - x_quaternion*conjZ +y_quaternion*conjW + z_quaternion*conjX;
//   float newConjZ =  w_quaternion*conjZ + x_quaternion*conjY - y_quaternion*conjW +z_quaternion*conjW;

//   float newConjW2 = w_quaternion * newConjW - (-x_quaternion)*newConjX - (-y_quaternion)*newConjY -(-z_quaternion)*newConjZ;
//   float newConjX2 =  w_quaternion*newConjX + (-x_quaternion)*newConjW + (-y_quaternion)*newConjZ - (-z_quaternion)*newConjY;
//   float newConjY2 =  w_quaternion*newConjY - (-x_quaternion)*newConjZ +(-y_quaternion)*newConjW + (-z_quaternion)*newConjX;
//   float newConjZ2 =  w_quaternion*newConjZ + (-x_quaternion)*newConjY - (-y_quaternion)*newConjW +(-z_quaternion)*newConjW;

//   accelEarthX=newConjX2;
//   accelEarthY=newConjY2;
//   accelEarthZ=newConjZ2;

// }


