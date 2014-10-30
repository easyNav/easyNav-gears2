
#define SIZE 40
int collector_index = 0;
float collector_arr[SIZE];
float time_arr[SIZE];
float g_offset = 0.0;

    // def integrate(self, arr, m_arr):
    //     sum_arr = []
    //     int_sum = 0
    //     for i in xrange(0, len(arr)):
    //         int_sum +=  abs(arr[i] * (m_arr[i]))
    //         sum_arr.append(int_sum)
    //     return sum_arr

float integrate(float data_arr[], float time_arr[], float sum_arr[], int length){
  float sum = 0;
  for(int i=0;i<length;i++){
    sum += data_arr[i]*(time_arr[i]*0.001);
    sum_arr[i] = sum;
  }
  return sum;
}

void print_float(float val){
  char buffer[10];
  String finalString = 
  String(floatToString(buffer, val , 3));

  int x = finalString.length();
  String append = "";
  if(x<7){
    for(int i=0;i<(7-x);i++)
      append += "0";
  }
  finalString = finalString + append;

  Serial.println(finalString);
}


// Output angles: yaw, pitch, roll
void output_angles()
{
  if (output_format == OUTPUT__FORMAT_BINARY)
  {
    float ypr[3];  
    ypr[0] = TO_DEG(yaw); //32 bits/4 bytes per val
    ypr[1] = TO_DEG(pitch);
    ypr[2] = TO_DEG(roll);
    Serial.write((byte*) ypr, 12);  // No new-line
  }
  else if (output_format == OUTPUT__FORMAT_TEXT)
  {


    // If not on ground, store Gx and increase index
    if(!on_ground()){


      if(collector_index >= SIZE)
        return;

      //float Gx = (DCM_Matrix[2][0] - g_offset)*9.81;
      float Gx = (Accel_magnitude - 1.08) * 9.81;
      collector_arr[collector_index] = Gx;
      time_arr[collector_index] = time_passed;
      collector_index++;

    // When on ground again
    }else{

      // Store offset
      g_offset = DCM_Matrix[2][0];

      // At least 10 datasets collected
      if(collector_index > 10){

        float vel_arr[SIZE];
        float dist_arr[SIZE];
        integrate(collector_arr, time_arr, vel_arr, collector_index);
        integrate(vel_arr, time_arr, dist_arr, collector_index);

        // for(int i=0;i<collector_index;i++){
        //   print_float(collector_arr[i]);
        // }

        Serial.print(",");
        print_float(dist_arr[collector_index - 1]*1000);


        // Set index back to 0
        collector_index = 0;
      }
    }

    // char buffer[10];
    // String finalString = "," +
    // String(floatToString(buffer, Accel_magnitude , 2)) + "," +
    // String((int)on_ground()) + "," +
    // String((int)magnetom[0]) + "," +
    // String((int)magnetom[1]) + "," +
    // String((int)magnetom[2]);




    // int extrabits = 16 - finalString.length();
    // String extraString = "";
    // for(int i=0;i<extrabits;i++){
    //   finalString += ",";
    // }

    // Serial.println(finalString);



    // Serial.print("#,");
    // Serial.print(magnetom[0]); Serial.print(",");
    // Serial.print(magnetom[1]); Serial.print(",");
    // Serial.print(magnetom[2]); Serial.print(",");
    // Serial.print(Accel_magnitude); Serial.print(",");
    // Serial.print(DCM_Matrix[2][0]); Serial.print(",");
    // Serial.print(DCM_Matrix[2][1]); Serial.print(",");
    // Serial.print(DCM_Matrix[2][2]); Serial.print(",");
    // Serial.print(time_passed); Serial.print(",");
    // Serial.print(on_ground()); Serial.print(",");
    // Serial.print("1"); Serial.print(",");
    // Serial.println();
  }
}

void output_calibration(int calibration_sensor)
{
  if (calibration_sensor == 0)  // Accelerometer
  {
    // Output MIN/MAX values
    Serial.print("accel x,y,z (min/max) = ");
    for (int i = 0; i < 3; i++) {
      if (accel[i] < accel_min[i]) accel_min[i] = accel[i];
      if (accel[i] > accel_max[i]) accel_max[i] = accel[i];
      Serial.print(accel_min[i]);
      Serial.print("/");
      Serial.print(accel_max[i]);
      if (i < 2) Serial.print("  ");
      else Serial.println();
    }
  }
  else if (calibration_sensor == 1)  // Magnetometer
  {
    // Output MIN/MAX values
    Serial.print("magn x,y,z (min/max) = ");
    for (int i = 0; i < 3; i++) {
      if (magnetom[i] < magnetom_min[i]) magnetom_min[i] = magnetom[i];
      if (magnetom[i] > magnetom_max[i]) magnetom_max[i] = magnetom[i];
      Serial.print(magnetom_min[i]);
      Serial.print("/");
      Serial.print(magnetom_max[i]);
      if (i < 2) Serial.print("  ");
      else Serial.println();
    }
  }
  else if (calibration_sensor == 2)  // Gyroscope
  {
    // Average gyro values
    for (int i = 0; i < 3; i++)
      gyro_average[i] += gyro[i];
    gyro_num_samples++;
      
    // Output current and averaged gyroscope values
    Serial.print("gyro x,y,z (current/average) = ");
    for (int i = 0; i < 3; i++) {
      Serial.print(gyro[i]);
      Serial.print("/");
      Serial.print(gyro_average[i] / (float) gyro_num_samples);
      if (i < 2) Serial.print("  ");
      else Serial.println();
    }
  }
}

void output_sensors_text(char raw_or_calibrated)
{
  Serial.print("#A-"); Serial.print(raw_or_calibrated); Serial.print('=');
  Serial.print(accel[0]); Serial.print(",");
  Serial.print(accel[1]); Serial.print(",");
  Serial.print(accel[2]); Serial.println();

  Serial.print("#M-"); Serial.print(raw_or_calibrated); Serial.print('=');
  Serial.print(magnetom[0]); Serial.print(",");
  Serial.print(magnetom[1]); Serial.print(",");
  Serial.print(magnetom[2]); Serial.println();

  Serial.print("#G-"); Serial.print(raw_or_calibrated); Serial.print('=');
  Serial.print(gyro[0]); Serial.print(",");
  Serial.print(gyro[1]); Serial.print(",");
  Serial.print(gyro[2]); Serial.println();
}

void output_sensors_binary()
{
  Serial.write((byte*) accel, 12);
  Serial.write((byte*) magnetom, 12);
  Serial.write((byte*) gyro, 12);
}

void output_sensors()
{
  if (output_mode == OUTPUT__MODE_SENSORS_RAW)
  {
    if (output_format == OUTPUT__FORMAT_BINARY)
      output_sensors_binary();
    else if (output_format == OUTPUT__FORMAT_TEXT)
      output_sensors_text('R');
  }
  else if (output_mode == OUTPUT__MODE_SENSORS_CALIB)
  {
    // Apply sensor calibration
    compensate_sensor_errors();
    
    if (output_format == OUTPUT__FORMAT_BINARY)
      output_sensors_binary();
    else if (output_format == OUTPUT__FORMAT_TEXT)
      output_sensors_text('C');
  }
  else if (output_mode == OUTPUT__MODE_SENSORS_BOTH)
  {
    if (output_format == OUTPUT__FORMAT_BINARY)
    {
      output_sensors_binary();
      compensate_sensor_errors();
      output_sensors_binary();
    }
    else if (output_format == OUTPUT__FORMAT_TEXT)
    {
      output_sensors_text('R');
      compensate_sensor_errors();
      output_sensors_text('C');
    }
  }
}

