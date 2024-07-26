import math
import ephem
import requests
from datetime import datetime
import pytz

# Constants
circle_radius = 1
phi = (1 + math.sqrt(5)) / 2  # Golden Ratio

def angle_to_degrees(angle):
    """Convert ephem.Angle object to degrees."""
    return angle * 180.0 / math.pi

def get_zodiac_sign(ra):
    """Determine the zodiac sign based on Right Ascension."""
    zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    signs_degrees = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    
    ra_deg = angle_to_degrees(ra) % 360  # Convert RA to degrees and normalize
    for i, degree in enumerate(signs_degrees):
        if ra_deg >= degree and ra_deg < degree + 30:
            return zodiac_signs[i]
    return 'Unknown'

def get_coordinates(city_name):
    """Get latitude and longitude for a given city."""
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            raise ValueError("City not found")
    else:
        raise ValueError("Error in geocoding request")

def angular_distance(angle1, angle2):
    """Calculate the angular distance between two angles in radians."""
    diff = abs(angle1 - angle2)
    return min(diff, 2 * math.pi - diff)

def calculate_cardinal_points():
    """Calculate the cardinal points (equinoxes and solstices) for the current year."""
    now = datetime.utcnow()
    year = now.year
    vernal_equinox = ephem.Date(f'{year}/03/20 00:00:00')
    summer_solstice = ephem.Date(f'{year}/06/21 00:00:00')
    autumnal_equinox = ephem.Date(f'{year}/09/22 00:00:00')
    winter_solstice = ephem.Date(f'{year}/12/21 00:00:00')
    
    return {
        'Vernal Equinox': vernal_equinox,
        'Summer Solstice': summer_solstice,
        'Autumnal Equinox': autumnal_equinox,
        'Winter Solstice': winter_solstice
    }

def get_distance_to_helios(planet, helios, observer):
    """Calculate distance in degrees from planet to cardinal helios."""
    planet.compute(observer)
    planet_deg = angle_to_degrees(planet.ra) % 360
    distances = {}
    for name, helios_date in helios.items():
        helios_body = ephem.Sun()
        helios_body.compute(helios_date)
        helios_deg = angle_to_degrees(helios_body.ra) % 360
        distance = angular_distance(math.radians(planet_deg), math.radians(helios_deg))
        distances[name] = math.degrees(distance)
    return distances

def planet_additional_data(planet, observer):
    """Calculate additional data for planets."""
    planet.compute(observer)
    distance_to_earth = planet.earth_distance * ephem.meters_per_au / 1000  # in kilometers
    
    # For lunar cycle-like data, let's use arbitrary example calculations
    cycle_percentage = (planet.phase / 100.0) * 100  # Mock data for example
    energy = math.sin(cycle_percentage * math.pi / 100)
    intensity = energy * 100  # Scale energy to a 0-100 range for intensity
    vibration = 1 + abs(math.cos(cycle_percentage * math.pi / 100))  # Arbitrary calculation
    frequency = 432 + (cycle_percentage / 100) * 8  # Arbitrary range from 432 Hz to 440 Hz
    resonance = vibration * frequency  # Arbitrary combination for resonance
    
    return {
        'Distance to Earth (km)': distance_to_earth,
        'Cycle Percentage': cycle_percentage,
        'Energy': energy,
        'Intensity': intensity,
        'Vibration': vibration,
        'Current Frequency (Hz)': frequency,
        'Resonance': resonance
    }

def lilith_black_moon(observer):
    """Calculate the position of Lilith (Black Moon)."""
    moon = ephem.Moon(observer)
    apogee = moon.hlon + math.pi  # Approximate position of Lilith
    
    # Create a FixedBody for Lilith
    lilith = ephem.FixedBody()
    lilith._epoch = observer.date
    lilith._ra = apogee
    lilith._dec = 0  # Not relevant for Lilith
    lilith.compute(observer)
    
    return lilith

def get_astrological_data(city_name):
    """Get astrological data for a given city."""
    # Get coordinates for the city
    lat, lon = get_coordinates(city_name)
    
    # Setup observer
    observer = ephem.Observer()
    observer.lat, observer.lon = str(lat), str(lon)
    
    # Convert UTC now to local time
    local_tz = pytz.timezone("Europe/Bucharest")  # Timisoara timezone
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_now = utc_now.astimezone(local_tz)
    observer.date = ephem.Date(local_now)
    
    # Calculate helios positions
    helios = calculate_cardinal_points()
    
    # Planets
    planets = {
        'Sun': ephem.Sun(observer),
        'Moon': ephem.Moon(observer),
        'Mercury': ephem.Mercury(observer),
        'Venus': ephem.Venus(observer),
        'Mars': ephem.Mars(observer),
        'Jupiter': ephem.Jupiter(observer),
        'Saturn': ephem.Saturn(observer),
        'Uranus': ephem.Uranus(observer),
        'Neptune': ephem.Neptune(observer),
        'Pluto': ephem.Pluto(observer)
    }
    
    # Adding Lilith (Black Moon)
    lilith = lilith_black_moon(observer)
    planets['Lilith'] = lilith
    
    # Fetch planetary positions
    astro_data = {}
    for planet_name, planet in planets.items():
        astro_data[planet_name] = {
            'RA': planet.ra,  # Right Ascension
            'Dec': planet.dec,  # Declination
            'Zodiac Sign': get_zodiac_sign(planet.ra),  # Zodiac sign
        }
        # Add additional data
        if planet_name != 'Lilith':
            astro_data[planet_name].update(planet_additional_data(planet, observer))
            # Add distance to helios
            astro_data[planet_name]['Distance to Helios'] = get_distance_to_helios(planet, helios, observer)
    
    # Print local time and planetary positions
    print(f"Local Time: {local_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Location: {city_name} (Lat: {lat}, Lon: {lon})\n")
    print("Planetary Positions:")
    for planet, data in astro_data.items():
        print(f"{planet}:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print()
    
    # Special Correspondences for Elements
    element_correspondences = {
        'Fire': ['Sun', 'Mars', 'Jupiter'],
        'Earth': ['Venus', 'Saturn', 'Pluto'],
        'Air': ['Mercury', 'Uranus', 'Neptune'],
        'Ether': ['Moon', 'Lilith']
    }
    
    # Print element correspondences
    print("Element Correspondences:")
    for element, associated_planets in element_correspondences.items():
        print(f"{element}: {', '.join(associated_planets)}")
    
    # Trace planetary circles
    print("\nTracing planetary circles relative to elements:")
    for element, associated_planets in element_correspondences.items():
        print(f"\n{element} Element Planets:")
        for planet_name in associated_planets:
            if planet_name in astro_data:
                planet_data = astro_data[planet_name]
                print(f"{planet_name}:")
                print(f"  Zodiac Sign: {planet_data['Zodiac Sign']}")
                print(f"  Right Ascension (RA): {planet_data['RA']}")
                print(f"  Declination (Dec): {planet_data['Dec']}")
                print(f"  Distance to Helios: {planet_data.get('Distance to Helios', 'N/A')}")
                print(f"  Current Frequency (Hz): {planet_data.get('Current Frequency (Hz)', 'N/A')}")
                print(f"  Resonance: {planet_data.get('Resonance', 'N/A')}")
                print()

# Example usage
get_astrological_data('Timisoara')
