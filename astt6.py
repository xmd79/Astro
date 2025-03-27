import ephem
from datetime import datetime, timedelta
import pytz
import geocoder
import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge, Polygon

# Get current date and time
current_datetime = datetime.now()

# Format the date and time
formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

# Print the results
print(f"Current Date and Time: {formatted_datetime}")

# Access specific components
year = current_datetime.year
month = current_datetime.month
day = current_datetime.day
hour = current_datetime.hour
minute = current_datetime.minute
second = current_datetime.second

print(f"Year: {year}")
print(f"Month: {month}")
print(f"Day: {day}")
print(f"Hour: {hour}")
print(f"Minute: {minute}")
print(f"Second: {second}")

# Get approximate location from IP
g = geocoder.ip('me')
if g.ok:
    latitude, longitude = g.latlng
    print(f"Estimated Location - Latitude: {latitude}, Longitude: {longitude}")
else:
    print("Could not determine location. Using default coordinates.")
    latitude, longitude = 0, 0

# Set up observer
observer = ephem.Observer()
observer.lat = str(latitude)
observer.lon = str(longitude)
observer.elev = 0

# Get current local datetime and convert to UTC
local_tz = datetime.now().astimezone().tzinfo
local_now = datetime.now(local_tz)
utc_now = local_now.astimezone(pytz.UTC)
observer.date = utc_now  # Set the observer's date to current UTC time

# Define the sun
sun = ephem.Sun()

# Get sunrise and sunset for today
observer.date = observer.date  # Current UTC time
sunrise_utc = observer.next_rising(sun, start=observer.date).datetime()  # Next sunrise
sunset_utc = observer.next_setting(sun, start=observer.date).datetime()  # Next sunset

# Convert to local time using system timezone
sunrise_local = pytz.utc.localize(sunrise_utc).astimezone(local_tz)
sunset_local = pytz.utc.localize(sunset_utc).astimezone(local_tz)

# Calculate daylight duration and stage length
daylight_duration = (sunset_local - sunrise_local).total_seconds()
stage_duration = daylight_duration / 4

# Define stage boundaries
morning_end = sunrise_local + timedelta(seconds=stage_duration)
noon_end = sunrise_local + timedelta(seconds=2 * stage_duration)
afternoon_end = sunrise_local + timedelta(seconds=3 * stage_duration)

# Get current time in local timezone
now = datetime.now(local_tz)

# Print stage boundaries for reference
print(f"\nSunrise: {sunrise_local.strftime('%H:%M:%S')}")
print(f"End of Morning: {morning_end.strftime('%H:%M:%S')}")
print(f"End of Noon: {noon_end.strftime('%H:%M:%S')}")
print(f"End of Afternoon: {afternoon_end.strftime('%H:%M:%S')}")
print(f"Sunset: {sunset_local.strftime('%H:%M:%S')}")

# Determine current stage
if sunrise_local <= now < morning_end:
    print("It's morning!")
elif morning_end <= now < noon_end:
    print("It's noon!")
elif noon_end <= now < afternoon_end:
    print("It's afternoon!")
elif afternoon_end <= now <= sunset_local:
    print("It's evening!")
else:
    print("It's nighttime!")

# Define zodiac sign boundaries (in degrees) and their attributes, including qualities
zodiac_signs = [
    ("Aries", 0, "Fire", "Cardinal", "+", "hot", "dry"),
    ("Taurus", 30, "Earth", "Fixed", "-", "cold", "dry"),
    ("Gemini", 60, "Air", "Mutable", "+", "hot", "wet"),
    ("Cancer", 90, "Water", "Cardinal", "-", "cold", "wet"),
    ("Leo", 120, "Fire", "Fixed", "+", "hot", "dry"),
    ("Virgo", 150, "Earth", "Mutable", "-", "cold", "dry"),
    ("Libra", 180, "Air", "Cardinal", "+", "hot", "wet"),
    ("Scorpio", 210, "Water", "Fixed", "-", "cold", "wet"),
    ("Sagittarius", 240, "Fire", "Mutable", "+", "hot", "dry"),
    ("Capricorn", 270, "Earth", "Cardinal", "-", "cold", "dry"),
    ("Aquarius", 300, "Air", "Fixed", "+", "hot", "wet"),
    ("Pisces", 330, "Water", "Mutable", "-", "cold", "wet")
]

# Define planets to track
planets = {
    "Sun": ephem.Sun(),
    "Moon": ephem.Moon(),
    "Mercury": ephem.Mercury(),
    "Venus": ephem.Venus(),
    "Mars": ephem.Mars(),
    "Jupiter": ephem.Jupiter(),
    "Saturn": ephem.Saturn(),
    "Uranus": ephem.Uranus(),
    "Neptune": ephem.Neptune(),
    "Pluto": ephem.Pluto()
}

# Define colors for elements (for zodiac wedges)
element_colors = {
    "Fire": "orange",
    "Earth": "green",
    "Air": "yellow",
    "Water": "blue"
}

# Define colors for elemental connection lines (Air triangle in purple)
connection_colors = {
    "Fire": "orange",
    "Earth": "green",
    "Air": "purple",
    "Water": "blue"
}

# Group zodiac signs by element for drawing connections
element_groups = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

# Function to calculate the Moon's phase
def get_moon_phase(observer):
    """
    Calculates the Moon's phase based on the observer's date and time.

    Args:
        observer (ephem.Observer): The observer object with location and time.

    Returns:
        tuple: (phase_name, phase_angle) where phase_name is a string and phase_angle is in degrees.
    """
    moon = ephem.Moon()
    moon.compute(observer)
    sun = ephem.Sun()
    sun.compute(observer)

    # Calculate the phase angle (angle between the Moon and Sun as seen from Earth)
    phase_angle = (moon.elong * 180 / math.pi) % 360  # Elongation in degrees

    # Determine the Moon's phase based on the phase angle
    if 0 <= phase_angle < 22.5 or 337.5 <= phase_angle < 360:
        phase_name = "New Moon"
    elif 22.5 <= phase_angle < 67.5:
        phase_name = "Waxing Crescent"
    elif 67.5 <= phase_angle < 112.5:
        phase_name = "First Quarter"
    elif 112.5 <= phase_angle < 157.5:
        phase_name = "Waxing Gibbous"
    elif 157.5 <= phase_angle < 202.5:
        phase_name = "Full Moon"
    elif 202.5 <= phase_angle < 247.5:
        phase_name = "Waning Gibbous"
    elif 247.5 <= phase_angle < 292.5:
        phase_name = "Third Quarter"
    else:
        phase_name = "Waning Crescent"

    return phase_name, phase_angle

# Function to calculate the zodiac sign of a planet based on its ecliptic longitude
def get_zodiac_sign(longitude):
    """
    Determines the zodiac sign based on the ecliptic longitude of a celestial body.

    Args:
        longitude (float): Ecliptic longitude in radians.

    Returns:
        tuple: (sign_name, element, modality, polarity, quality1, quality2)
    """
    longitude = math.degrees(longitude) % 360  # Normalize to 0-360 degrees
    for sign, start, element, modality, polarity, quality1, quality2 in zodiac_signs:
        if longitude >= start and longitude < (start + 30):
            return sign, element, modality, polarity, quality1, quality2
    return "Pisces", "Water", "Mutable", "-", "cold", "wet"  # Default for 330-360 degrees

# Function to calculate aspects between planets
def calculate_aspects(positions):
    """
    Calculates astrological aspects between planets based on their angular separation.

    Args:
        positions (dict): Dictionary of planet names and their ecliptic longitudes in degrees.

    Returns:
        list: List of tuples (planet1, planet2, aspect_type, angle).
    """
    aspects = []
    aspect_types = {
        "Conjunction": (0, 8),       # Within 8 degrees
        "Semi-sextile": (30, 2),     # Within 2 degrees
        "Sextile": (60, 6),           # Within 6 degrees
        "Square": (90, 8),            # Within 8 degrees
        "Trine": (120, 8),            # Within 8 degrees
        "Quincunx": (150, 4),         # Within 4 degrees
        "Opposition": (180, 8)        # Within 8 degrees
    }

    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            lon1, lon2 = positions[p1], positions[p2]
            angle = min((lon1 - lon2) % 360, (lon2 - lon1) % 360)  # Shortest angular distance

            for aspect, (target_angle, orb) in aspect_types.items():
                if abs(angle - target_angle) <= orb:
                    aspects.append((p1, p2, aspect, round(angle, 2)))

    return aspects

# Function to draw elemental connections between zodiac signs
def draw_elemental_connections(ax, radius=1.0):
    """
    Draws lines between zodiac signs of the same element, forming a star-like pattern.

    Args:
        ax: Matplotlib axis to draw on.
        radius (float): Radius at which to draw the connections (should match the zodiac wheel radius).
    """
    # For each element, connect the signs
    for element, signs in element_groups.items():
        color = connection_colors[element]  # Use connection_colors for the lines
        # Get the center angles of each sign in the group
        angles = []
        for sign in signs:
            for zodiac_sign, start, _, _, _, _, _ in zodiac_signs:
                if zodiac_sign == sign:
                    angle = math.radians(start + 15)  # Middle of the sign
                    angles.append(angle)
                    break

        # Draw lines between each pair of signs in the group
        for i in range(len(angles)):
            for j in range(i + 1, len(angles)):
                x1 = radius * math.cos(angles[i])
                y1 = radius * math.sin(angles[i])
                x2 = radius * math.cos(angles[j])
                y2 = radius * math.sin(angles[j])
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.5, alpha=0.7)

# Function to plot the astrological wheel with new features
def plot_astrological_wheel(positions, moon_phase, local_time_str):
    """
    Plots the astrological wheel with zodiac signs, planet positions, moon phase, 
    and elemental connections.

    Args:
        positions (dict): Dictionary of planet names and their ecliptic longitudes in degrees.
        moon_phase (str): The name of the Moon's phase.
        local_time_str (str): String representation of the local time.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw zodiac wheel (each sign is 30 degrees)
    for sign, start, element, modality, polarity, quality1, quality2 in zodiac_signs:
        color = element_colors[element]
        wedge = Wedge((0, 0), 1, start, start + 30, facecolor=color, alpha=0.3)
        ax.add_patch(wedge)

        # Add sign labels
        angle = math.radians(start + 15)  # Middle of the sign
        x = 1.1 * math.cos(angle)
        y = 1.1 * math.sin(angle)
        ax.text(x, y, sign, ha='center', va='center', fontsize=10, rotation=-(start + 15))

        # Add element, modality, polarity, and qualities labels
        x_inner = 0.7 * math.cos(angle)
        y_inner = 0.7 * math.sin(angle)
        ax.text(x_inner, y_inner, f"{element}\n{modality}\n{polarity}\n{quality1}, {quality2}",
                ha='center', va='center', fontsize=8)

    # Draw elemental connections
    draw_elemental_connections(ax, radius=1.0)

    # Plot planet positions
    for planet, lon in positions.items():
        angle = math.radians(360 - lon + 90)  # Adjust for matplotlib's coordinate system
        x = 0.9 * math.cos(angle)
        y = 0.9 * math.sin(angle)
        ax.plot(x, y, 'o', label=planet)
        ax.text(x * 1.05, y * 1.05, planet, fontsize=8)

    # Add central label with Moon phase
    ax.text(0, 0, f"THE 12 SIGNS\nMoon Phase: {moon_phase}", ha='center', va='center', fontsize=14, color='purple')

    # Add legend
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"Astrological Wheel for {local_time_str} (Current Location)")
    plt.show()

# Main function to build the astrological clock
def astrological_clock():
    """
    Computes the positions of planets, determines their zodiac signs, calculates aspects,
    determines the Moon's phase, and plots the astrological wheel.

    Returns:
        tuple: (positions, aspects) where positions is a dict of planet longitudes and
        aspects is a list of planetary aspects.
    """
    # Dictionary to store planet positions (in degrees)
    positions = {}

    # Calculate positions for each planet
    print("Planetary Positions and Attributes:")
    print("-" * 40)
    for name, planet in planets.items():
        planet.compute(observer)
        # Get ecliptic longitude (position in the zodiac)
        longitude = ephem.Ecliptic(planet).lon
        positions[name] = math.degrees(longitude) % 360
        sign, element, modality, polarity, quality1, quality2 = get_zodiac_sign(longitude)

        # Print planet's position and attributes
        print(f"{name}: {round(positions[name], 2)}° in {sign} ({element}, {modality}, {polarity}, {quality1}, {quality2})")

    # Calculate Moon phase
    print("\nMoon Phase:")
    print("-" * 40)
    moon_phase, phase_angle = get_moon_phase(observer)
    print(f"Moon Phase: {moon_phase} (Phase Angle: {round(phase_angle, 2)}°)")

    # Calculate aspects
    print("\nAspects Between Planets:")
    print("-" * 40)
    aspects = calculate_aspects(positions)
    for p1, p2, aspect, angle in aspects:
        print(f"{p1} {aspect} {p2} ({angle}°)")

    # Plot the astrological wheel with Moon phase
    print("\nGenerating Astrological Wheel Plot...")
    local_time_str = local_now.strftime("%B %d, %Y, %H:%M %Z")  # Format local time for display
    plot_astrological_wheel(positions, moon_phase, local_time_str)

    return positions, aspects

# Run the astrological clock
if __name__ == "__main__":
    local_time_str = local_now.strftime("%B %d, %Y, %H:%M %Z")
    print(f"Astrological Clock for {local_time_str} (Current Location)")
    print("=" * 50)
    positions, aspects = astrological_clock()