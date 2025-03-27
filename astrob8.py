import ephem
from datetime import datetime, timedelta
import pytz
import geocoder
import math

# Constants for astrology
PLANETS = {
    'Sun': {'polarity': 'Yang', 'chakra': 'Solar Plexus', 'sephirot': 'Tiphareth', 'element': 'Fire'},
    'Moon': {'polarity': 'Yin', 'chakra': 'Sacral', 'sephirot': 'Malkuth', 'element': 'Water'},
    'Mercury': {'polarity': 'Neutral', 'chakra': 'Throat', 'sephirot': 'Binah', 'element': 'Air'},
    'Venus': {'polarity': 'Yin', 'chakra': 'Heart', 'sephirot': 'Hod', 'element': 'Earth'},
    'Mars': {'polarity': 'Yang', 'chakra': 'Root', 'sephirot': 'Gevurah', 'element': 'Fire'},
    'Jupiter': {'polarity': 'Yang', 'chakra': 'Crown', 'sephirot': 'Chokmah', 'element': 'Fire'},
    'Saturn': {'polarity': 'Yin', 'chakra': 'Third Eye', 'sephirot': 'Keter', 'element': 'Earth'},
}

ZODIAC_SIGNS = {
    0: 'Aries',
    1: 'Taurus',
    2: 'Gemini',
    3: 'Cancer',
    4: 'Leo',
    5: 'Virgo',
    6: 'Libra',
    7: 'Scorpio',
    8: 'Sagittarius',
    9: 'Capricorn',
    10: 'Aquarius',
    11: 'Pisces',
}

# Planetary days in the order of the days of the week
PLANETARY_DAYS = {
    0: 'Moon',         # Sunday
    1: 'Mars',         # Monday
    2: 'Mercury',      # Tuesday
    3: 'Jupiter',      # Wednesday
    4: 'Venus',        # Thursday
    5: 'Saturn',       # Friday
    6: 'Sun'           # Saturday
}

# Yugas and their durations (in years)
YUGAS = {
    'Satya Yuga': 1728000,
    'Treta Yuga': 1296000,
    'Dvapara Yuga': 864000,
    'Kali Yuga': 432000
}

# Starting year of Kali Yuga (approximate)
KALI_YUGA_START_YEAR = 3102  # BCE
CURRENT_YEAR = datetime.now().year

def calculate_current_yuga():
    """Calculate the current Yuga based on elapsed time from the start of Kali Yuga."""
    elapsed_years = CURRENT_YEAR - (-KALI_YUGA_START_YEAR)  # accounting for BCE
    cumulative_years = 0
    for yuga, duration in YUGAS.items():
        if elapsed_years < cumulative_years + duration:
            current_yuga = yuga
            percentage = (elapsed_years - cumulative_years) / duration * 100
            return current_yuga, percentage
        cumulative_years += duration
    return "Unknown Yuga", 0  # If for some reason we cannot determine

def get_zodiac_sign(degree):
    """Determine zodiac sign from degree."""
    return ZODIAC_SIGNS[int(degree // 30)]

def get_planetary_day():
    """Get the current planetary day based on the day of the week."""
    current_day = datetime.now(pytz.utc).weekday()  # Monday is 0
    return PLANETARY_DAYS[current_day]

def get_planetary_hour(local_datetime):
    """Calculate the current planetary hour."""
    planetary_order = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
    
    current_hour = local_datetime.hour
    # Find the current planetary day
    current_planetary_day = get_planetary_day()
    
    # Determine starting hour based on the current planetary day
    start_hour = planetary_order.index(current_planetary_day)
    
    # Calculate the hour index in the planetary hour
    hour_index = (start_hour + current_hour) % 7
    
    # Calculate planetary hour's ruling planet
    ruling_planet = planetary_order[hour_index]
    
    return ruling_planet

# Get location from IP
g = geocoder.ip('me')
if g.ok:
    latitude, longitude = g.latlng
else:
    latitude, longitude = 0, 0

# Set observer
observer = ephem.Observer()
observer.lat = str(latitude)
observer.lon = str(longitude)
observer.elev = 0
observer.date = datetime.utcnow()

# Get current date and time
current_datetime = datetime.now(pytz.utc).astimezone()  # Use local timezone
observer.date = current_datetime

def get_ascendant(observer):
    """Calculate Ascendant sign from the observer."""
    ascendant = ephem.Sun(observer).ra
    return get_zodiac_sign(math.degrees(ascendant) % 360)

def get_midheaven(observer):
    """Calculate Midheaven sign from the observer."""
    midheaven = ephem.Moon(observer).ra
    return get_zodiac_sign(math.degrees(midheaven) % 360)

def get_planet_data(observer):
    planet_data = {}
    for name in PLANETS.keys():
        planet = getattr(ephem, name)()  # Access the correct planet object
        planet.compute(observer)
        
        zodiac_sign = get_zodiac_sign(math.degrees(planet.ra) % 360)
        
        planet_data[name] = {
            'zodiac': zodiac_sign,
            'ra': planet.ra,
            'dec': planet.dec,
            'distance_km': planet.earth_distance * ephem.meters_per_au / 1000,
            'polarity': PLANETS[name]['polarity'],
            'chakra': PLANETS[name]['chakra'],
            'sephirot': PLANETS[name]['sephirot'],
            'element': PLANETS[name]['element'],
        }
    return planet_data

def calculate_aspects(planet_data):
    aspects = []
    keys = list(planet_data.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            planet1 = keys[i]
            planet2 = keys[j]
            angle = abs(math.degrees(planet_data[planet1]['ra'] - planet_data[planet2]['ra'])) % 360
            
            if angle < 8:  # Conjunction
                aspects.append((planet1, planet2, 'Conjunction'))
            elif 172 < angle < 188:  # Opposition
                aspects.append((planet1, planet2, 'Opposition'))
            elif 82 < angle < 98:  # Trine
                aspects.append((planet1, planet2, 'Trine'))
            elif 172 < angle < 178:  # Square
                aspects.append((planet1, planet2, 'Square'))
            # Other aspects can be added as needed
    return aspects

# Get ascendant and midheaven
ascendant = get_ascendant(observer)
midheaven = get_midheaven(observer)

# Get planet data
planet_data = get_planet_data(observer)

# Calculate aspects
aspects = calculate_aspects(planet_data)

# Get current planetary hour and day
current_planetary_hour = get_planetary_hour(current_datetime)
current_planetary_day = get_planetary_day()

# Feedback on current date details
current_week_of_month = (current_datetime.day - 1) // 7 + 1
current_month = current_datetime.month
current_year = current_datetime.year

# Calculate current Yuga and its progress
current_yuga, progress_percentage = calculate_current_yuga()

# Output results
print(f"Current Local Date and Time: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Ascendant: {ascendant}")
print(f"Midheaven: {midheaven}")
print(f"Current Planetary Day: {current_planetary_day}")
print(f"Current Planetary Hour: {current_planetary_hour}")

print(f"\nCurrent Week of Month: {current_week_of_month}")
print(f"Current Month: {current_month}")
print(f"Current Year: {current_year}")

# Yugas and their current statuses
print("\nYugas and Their Durations:")
for yuga, duration in YUGAS.items():
    if yuga == current_yuga:
        print(f"{yuga}: {duration} years (Current, {progress_percentage:.2f}% complete)")
    else:
        print(f"{yuga}: {duration} years")

print("\nPlanet Data:")
for planet, data in planet_data.items():
    print(f"{planet}:")
    for key, value in data.items():
        print(f"  {key.title()}: {value}")

print("\nAspects:")
for aspect in aspects:
    print(f"{aspect[0]} and {aspect[1]}: {aspect[2]}")