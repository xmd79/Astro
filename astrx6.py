import math
import ephem
import requests
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim

# Constants
phi = (1 + math.sqrt(5)) / 2  # Golden Ratio
phi_squared = phi ** 2  # Phi^2
phi_inv = 1 / phi  # 1/Phi

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
    geolocator = Nominatim(user_agent="astro_application")  # Use a descriptive user_agent
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError("City not found")

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

def get_aspect(angle1, angle2):
    """Determine the aspect between two planetary positions."""
    distance = angular_distance(angle1, angle2)
    aspects = {
        'Conjunction': math.radians(8),
        'Opposition': math.pi - math.radians(8),
        'Trine': math.radians(60),
        'Square': math.radians(90),
        'Sextile': math.radians(120)
    }
    for aspect, threshold in aspects.items():
        if abs(distance - threshold) < math.radians(8):
            return aspect
    return 'No significant aspect'

def angular_positions_of_planets(planets):
    """Determine angular positions of planets in radians."""
    angles = {}
    for name, planet in planets.items():
        ra_in_radians = planet.ra  # Already in radians
        angles[name] = ra_in_radians
    return angles

def phi_symmetry_calculations(planet_name, planet):
    """Calculate ratios and phi symmetry for the given planet."""
    planet_radius = planet.earth_distance * ephem.meters_per_au / 1000  # Convert distance to km
    
    # Golden Circle
    golden_circle = phi * planet_radius
    golden_triangle = phi_squared * planet_radius
    golden_square = phi_inv * planet_radius
    golden_star = phi_squared * golden_circle  # Extend this concept further if needed.

    return {
        'Planet': planet_name,
        'Radius (km)': planet_radius,
        'Golden Circle': golden_circle,
        'Golden Triangle': golden_triangle,
        'Golden Square': golden_square,
        'Golden Star': golden_star,
    }

def get_astrological_data(city_name):
    """Get astrological data for a given city."""
    try:
        lat, lon = get_coordinates(city_name)
    except ValueError as e:
        print(e)
        return

    # Setup observer
    observer = ephem.Observer()
    observer.lat, observer.lon = str(lat), str(lon)
    observer.date = datetime.utcnow()

    # Convert UTC now to local time
    local_now = datetime.now(pytz.timezone("Europe/Bucharest"))
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

    # Fetch planetary positions and calculate additional properties
    astro_data = {}
    for planet_name, planet in planets.items():
        astro_data[planet_name] = {
            'RA': planet.ra,  # Right Ascension
            'Dec': planet.dec,  # Declination
            'Zodiac Sign': get_zodiac_sign(planet.ra),  # Zodiac sign
            'Constellation': ephem.constellation(planet)  # Zodiac constellation
        }

    # Calculate angular positions
    angles = angular_positions_of_planets(planets)

    # Print local time and planetary positions
    print(f"Local Time: {local_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Location: {city_name} (Lat: {lat}, Lon: {lon})\n")
    
    print("--- Planetary Positions and Data ---")
    for planet, data in astro_data.items():
        print(f"{planet}:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print()

    # Calculate aspects and display triangular relationships
    print("Symmetrical Triangle Relationships:")
    saturn_angle = angles['Saturn']
    mercury_angle = angles['Mercury']
    venus_angle = angles['Venus']
    
    # Equilateral Triangle 1: Saturn, Mercury, Venus
    print(f"Angles for Triangle 1 (Saturn, Mercury, Venus):")
    print(f"  Saturn: {angle_to_degrees(saturn_angle)}°")
    print(f"  Mercury: {angle_to_degrees(mercury_angle)}°")
    print(f"  Venus: {angle_to_degrees(venus_angle)}°")
    
    # Aspects within Triangle 1
    print("Aspects within Triangle 1:")
    for p1, p2 in [('Saturn', 'Mercury'), ('Mercury', 'Venus'), ('Venus', 'Saturn')]:
        aspect = get_aspect(angles[p1], angles[p2])
        print(f"  Aspect between {p1} and {p2}: {aspect}")

    moon_angle = angles['Moon']
    mars_angle = angles['Mars']
    jupiter_angle = angles['Jupiter']

    # Equilateral Triangle 2: Moon, Mars, Jupiter
    print(f"\nAngles for Triangle 2 (Moon, Mars, Jupiter):")
    print(f"  Moon: {angle_to_degrees(moon_angle)}°")
    print(f"  Mars: {angle_to_degrees(mars_angle)}°")
    print(f"  Jupiter: {angle_to_degrees(jupiter_angle)}°")
    
    # Aspects within Triangle 2
    print("Aspects within Triangle 2:")
    for p1, p2 in [('Moon', 'Mars'), ('Mars', 'Jupiter'), ('Jupiter', 'Moon')]:
        aspect = get_aspect(angles[p1], angles[p2])
        print(f"  Aspect between {p1} and {p2}: {aspect}")

# Example usage
if __name__ == "__main__":
    city = "Timisoara, Timis, Romania"
    get_astrological_data(city)