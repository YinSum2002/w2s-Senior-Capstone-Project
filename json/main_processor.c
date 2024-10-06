#include <stdio.h>
#include <time.h>

#include "sensors.h"

int main() {
  // Create a time_t variable to store the current time
  time_t raw_time;
  struct tm *time_info;
  char time_str[30];  // Buffer to store the formatted time string

  // Get the current time
  time(&raw_time);

  // Convert the time to local time (you can use gmtime() for UTC time)
  time_info = localtime(&raw_time);

  // Format the time as "YYYY-MM-DD HH:MM:SS"
  strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", time_info);

  // Open a file to write the JSON data
  FILE *file = fopen("sensor_data.json", "w");
  if (file == NULL) {
    printf("Error opening file!\n");
    return 1;
  }

  // Simulating sensor data
  float temperature = get_temperature();
  float humidity = get_humidity();

  // Write the formatted data into the file
  fprintf(file,
          "{\n  \"time\": \"%s\",\n  \"temperature\": %.2f,\n  \"humidity\": "
          "%.2f\n}\n",
          time_str, temperature, humidity);

  // Close the file
  fclose(file);

  printf("Data successfully written to file.\n");

  return 0;
}
