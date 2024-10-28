import uvlight
import moisture
import TSL2591
import pH

def main():
    uv_value = uvlight.get_uv_data()
    print(f"UV Value: {uv_value}")
    
    moisture_value = moisture.read_moisture()
    print(f"Moisture Value: {moisture_value}")
    
    pH_value = pH.read_pH()
    print(f"pH Value: {pH_value}")
    
if __name__ == "__main__":
    main()
