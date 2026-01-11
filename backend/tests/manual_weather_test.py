
import asyncio
import sys
import os

# Add the project root to the python path so we can import app modules
# Assuming this script is run from the project root or we can navigate relatively
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.weather_client import WeatherClient

async def main():
    print("Testing WeatherClient...")
    client = WeatherClient()
    
    # Banff coordinates
    lat = 51.1784
    lon = -115.5708
    
    print(f"Fetching weather for Banff ({lat}, {lon})...")
    weather = await client.get_weather(lat, lon)
    
    if weather:
        print("\n✅ Weather data received:")
        summary = client.get_weather_summary(weather)
        print(f"Summary: {summary}")
        
        severity = client.get_weather_severity(weather)
        print(f"Severity: {severity}")
        
        move_mod = client.get_movement_modifier(weather)
        print(f"Movement Modifier: {move_mod}")

        vis_impact = client.get_visibility_impact(weather)
        print(f"Visibility Impact: {vis_impact}")
        
        print("\nRaw Data Snippet (Current):")
        print(weather.get('current', 'No current data'))
    else:
        print("\n❌ Failed to fetch weather data.")

if __name__ == "__main__":
    asyncio.run(main())
