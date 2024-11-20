import uvlight
import pH
import TSL2591
import soil_moisture
import temp_humid


def make_array(sensor_function):
    sensor_array = []
    for _ in range(1):
        sensor_array.append(sensor_function)
    return sensor_array

def main():
    sensor_values = []
    
    sensor_values.append(make_array(uvlight.read_uv()))
# 
    sensor_values.append(make_array(pH.read_ph()))
    sensor_values.append(make_array(TSL2591.light()))
    sensor_values.append(make_array(soil_moisture.read_soil_moisture()))
#     
    sensor_values.append(make_array(temp_humid.read_am2320()))

    print(sensor_values)
    return sensor_values
    

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()