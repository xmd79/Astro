import ephem
import datetime
import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge

# Set up observer (location and time)
observer = ephem.Observer()
observer.lat = '40.7128'  # Latitude for New York
observer.lon = '-74.0060'  # Longitude for New York
observer.date = datetime.datetime(2025, 3, 19, 12, 0, 0)  # March 19, 2025, 12:00 UTC

# Define zodiac sign boundaries (in degrees) and their attributes
zodiac_signs = [
    ("Aries", 0, "Fire", "Cardinal", "+"),
    ("Taurus", 30, "Earth", "Fixed", "-"),
    ("Gemini", 60, "Air", "Mutable", "+"),
    ("Cancer", 90, "Water", "Cardinal", "-"),
    ("Leo", 120, "Fire", "Fixed", "+"),
    ("Virgo", 150, "Earth", "Mutable", "-"),
    ("Libra", 180, "Air", "Cardinal", "+"),
    ("Scorpio", 210, "Water", "Fixed", "-"),
    ("Sagittarius", 240, "Fire", "Mutable", "+"),
    ("Capricorn", 270, "Earth", "Cardinal", "-"),
    ("Aquarius", 300, "Air", "Fixed", "+"),
    ("Pisces", 330, "Water", "Mutable", "-")
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

# Define colors for elements (matching the image)
element_colors = {
    "Fire": "red",
    "Earth": "green",
    "Air": "yellow",
    "Water": "blue"
}

# Function to calculate the zodiac sign of a planet based on its ecliptic longitude
def get_zodiac_sign(longitude):
    """
    Determines the zodiac sign based on the ecliptic longitude of a celestial body.
    
    Args:
        longitude (float): Ecliptic longitude in radians.
    
    Returns:
        tuple: (sign_name, element, modality, polarity)
    """
    longitude = math.degrees(longitude) % 360  # Normalize to 0-360 degrees
    for sign, start, element, modality, polarity in zodiac_signs:
        if longitude >= start and longitude < (start + 30):
            return sign, element, modality, polarity
    return "Pisces", "Water", "Mutable", "-"  # Default for 330-360 degrees

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
        "Conjunction": (0, 8),    # Within 8 degrees
        "Semi-sextile": (30, 2),  # Within 2 degrees
        "Sextile": (60, 6),       # Within 6 degrees
        "Square": (90, 8),        # Within 8 degrees
        "Trine": (120, 8),        # Within 8 degrees
        "Quincunx": (150, 4),     # Within 4 degrees
        "Opposition": (180, 8)    # Within 8 degrees
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

# Function to plot the astrological wheel
def plot_astrological_wheel(positions):
    """
    Plots the astrological wheel with zodiac signs and planet positions.
    
    Args:
        positions (dict): Dictionary of planet names and their ecliptic longitudes in degrees.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw zodiac wheel (each sign is 30 degrees)
    for sign, start, element, modality, polarity in zodiac_signs:
        color = element_colors[element]
        wedge = Wedge((0, 0), 1, start, start + 30, facecolor=color, alpha=0.5)
        ax.add_patch(wedge)
        
        # Add sign labels
        angle = math.radians(start + 15)  # Middle of the sign
        x = 1.1 * math.cos(angle)
        y = 1.1 * math.sin(angle)
        ax.text(x, y, sign, ha='center', va='center', fontsize=10, rotation=-(start + 15))

        # Add element, modality, and polarity labels
        x_inner = 0.7 * math.cos(angle)
        y_inner = 0.7 * math.sin(angle)
        ax.text(x_inner, y_inner, f"{element}\n{modality}\n{polarity}", ha='center', va='center', fontsize=8)

    # Plot planet positions
    for planet, lon in positions.items():
        angle = math.radians(360 - lon + 90)  # Adjust for matplotlib's coordinate system
        x = 0.9 * math.cos(angle)
        y = 0.9 * math.sin(angle)
        ax.plot(x, y, 'o', label=planet)
        ax.text(x * 1.05, y * 1.05, planet, fontsize=8)

    # Add central label
    ax.text(0, 0, "THE 12 SIGNS", ha='center', va='center', fontsize=14, color='purple')

    # Add legend
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title("Astrological Wheel for March 19, 2025, 12:00 UTC (New York)")
    plt.show()

# Main function to build the astrological clock
def astrological_clock():
    """
    Computes the positions of planets, determines their zodiac signs, calculates aspects,
    and plots the astrological wheel.
    
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
        sign, element, modality, polarity = get_zodiac_sign(longitude)
        
        # Print planet's position and attributes
        print(f"{name}: {round(positions[name], 2)}° in {sign} ({element}, {modality}, {polarity})")

    # Calculate aspects
    print("\nAspects Between Planets:")
    print("-" * 40)
    aspects = calculate_aspects(positions)
    for p1, p2, aspect, angle in aspects:
        print(f"{p1} {aspect} {p2} ({angle}°)")
    
    # Plot the astrological wheel
    print("\nGenerating Astrological Wheel Plot...")
    plot_astrological_wheel(positions)
    
    return positions, aspects

# Run the astrological clock
if __name__ == "__main__":
    print("Astrological Clock for March 19, 2025, 12:00 UTC (New York)")
    print("=" * 50)
    positions, aspects = astrological_clock()