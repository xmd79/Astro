import matplotlib.pyplot as plt
import numpy as np
import ephem
import datetime
import pytz
import math
from astroquery.jplhorizons import Horizons
from astropy.time import Time
from matplotlib.patches import Circle, Wedge, PathPatch
from matplotlib.path import Path
import warnings

# Suppress any potential warnings (kept as a precaution)
warnings.filterwarnings("ignore", category=UserWarning, message="Glyph .* missing from font")

# Define planetary symbols for visualization
planet_symbols = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '♅',
    'Neptune': '♆',
    'Pluto': '♇'
}

# Define element symbols and their names (using plain text to avoid glyph issues)
element_symbols = {
    'Fire': 'Fire',
    'Earth': 'Earth',
    'Air': 'Air',
    'Water': 'Water'
}

# Define element colors (adjusted for better astrological alignment)
element_colors = {
    'Fire': 'red',        # Traditional fiery color
    'Earth': 'green',     # Traditional earthy color
    'Air': 'skyblue',     # Light blue to represent sky/wind
    'Water': 'blue'       # Traditional water color
}

# Define intermediate stages between elements (Hot, Dry, Cold, Wet)
intermediate_stages = [
    ("Hot", 45),   # Between Fire (0°) and Air (90°)
    ("Wet", 135),  # Between Air (90°) and Water (180°)
    ("Cold", 225), # Between Water (180°) and Earth (270°)
    ("Dry", 315)   # Between Earth (270°) and Fire (0°/360°)
]

# Define zodiac signs with elements, modalities, and polarities
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

# Define Vedic houses (12 houses, each 30 degrees, aligned with zodiac signs for simplicity)
vedic_houses = [
    (1, "Self, Identity", 0),
    (2, "Wealth, Values", 30),
    (3, "Communication, Siblings", 60),
    (4, "Home, Mother", 90),
    (5, "Creativity, Children", 120),
    (6, "Health, Service", 150),
    (7, "Partnerships, Marriage", 180),
    (8, "Transformation, Occult", 210),
    (9, "Philosophy, Higher Learning", 240),
    (10, "Career, Public Life", 270),
    (11, "Gains, Friendships", 300),
    (12, "Spirituality, Losses", 330)
]

# Define 12-pointed star cycles (Yearly Cycles, Triads of Mind, Tetrads of Physicality)
yearly_cycles = [
    ("Vernal Equinox", 0), ("Spring", 30), ("Planting", 60), ("Summer Solstice", 90),
    ("Summer", 120), ("Growth", 150), ("Autumn Equinox", 180), ("Autumn", 210),
    ("Harvest", 240), ("Winter Solstice", 270), ("Winter", 300), ("Fallow", 330)
]

triads_of_mind = [
    ("Knowledge", 0), ("Conscious", 30), ("Beliefs", 60), ("Attention", 90),
    ("Understanding", 120), ("Superconscious", 150), ("Ego", 180), ("Perception", 210),
    ("Wisdom", 240), ("Subconscious", 270), ("Thoughts", 300), ("Memory", 330)
]

# Corrected cardinal directions: North (0°), East (90°), South (180°), West (270°)
tetrads_of_physicality = [
    ("North", 0), ("Fire", 30), ("Length", 60), ("East", 90),
    ("Air", 120), ("Width", 150), ("South", 180), ("Water", 210),
    ("Height", 240), ("West", 270), ("Earth", 300), ("Time", 330)
]

# Moon phases (simplified for integration)
moon_phases = [
    ("New", 0), ("Waxing Crescent", 45), ("First Quarter", 90), ("Waxing Gibbous", 135),
    ("Full", 180), ("Waning Gibbous", 225), ("Third Quarter", 270), ("Waning Crescent", 315)
]

# Function to calculate the zodiac sign of a planet based on its ecliptic longitude
def get_zodiac_sign(longitude):
    longitude = longitude % 360
    for sign, start, element, modality, polarity in zodiac_signs:
        if longitude >= start and longitude < (start + 30):
            return sign, element, modality, polarity
    return "Pisces", "Water", "Mutable", "-"

# Function to determine the Vedic house of a planet
def get_vedic_house(longitude):
    longitude = longitude % 360
    for house_num, house_name, start in vedic_houses:
        if longitude >= start and longitude < (start + 30):
            return house_num, house_name
    return 12, "Spirituality, Losses"

# Function to get Vedic houses based on the Ascendant (Lagna) - Fixed the NameError
def get_vedic_houses(current_time, observer_coords):
    observer = ephem.Observer()  # Corrected variable name from MUNobserver to observer
    observer.lat = str(observer_coords['latitude'])
    observer.lon = str(observer_coords['longitude'])
    observer.date = current_time
    observer.pressure = 0  # Ignore atmospheric pressure for simplicity
    observer.horizon = '0'  # Set horizon to 0 degrees
    
    # Calculate the Ascendant (Lagna)
    ascendant = observer.radec_of(0, '0')[0]  # Right Ascension of the Ascendant
    ecliptic = ephem.Ecliptic(ascendant, 0)  # Convert to ecliptic coordinates
    ascendant_longitude = math.degrees(ecliptic.lon) % 360
    
    # Map houses starting from the Ascendant
    houses = {}
    for i in range(1, 13):
        house_start = (ascendant_longitude + (i - 1) * 30) % 360
        sign, _, _, _ = get_zodiac_sign(house_start)
        houses[i] = sign
    return houses

# Function to draw a square given the center and size
def draw_square(ax, center, size, angle=0, **kwargs):
    half_size = size / 2
    square = np.array([
        [-half_size, -half_size],
        [ half_size, -half_size],
        [ half_size,  half_size],
        [-half_size,  half_size],
        [-half_size, -half_size]
    ])
    
    rotation_matrix = np.array([
        [np.cos(np.radians(angle)), -np.sin(np.radians(angle))],
        [np.sin(np.radians(angle)),  np.cos(np.radians(angle))]
    ])
    square = square @ rotation_matrix.T
    square += center
    ax.plot(square[:, 0], square[:, 1], **kwargs)

# Function to draw a 12-pointed star
def draw_12_pointed_star(ax, radius, center=(0, 0), color='black'):
    vertices = []
    for i in range(12):
        angle = math.radians(90 - (i * 30))  # Adjust for astrological orientation
        outer_x = center[0] + radius * math.cos(angle)
        outer_y = center[1] + radius * math.sin(angle)
        inner_angle = math.radians(90 - (i * 30 + 15))
        inner_x = center[0] + (radius * 0.5) * math.cos(inner_angle)
        inner_y = center[1] + (radius * 0.5) * math.sin(inner_angle)
        vertices.extend([(outer_x, outer_y), (inner_x, inner_y)])
    vertices.append(vertices[0])
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 1)
    path = Path(vertices, codes)
    patch = PathPatch(path, facecolor='none', edgecolor=color, lw=1)
    ax.add_patch(patch)

# Function to calculate aspects between planets with wave properties
def calculate_aspects(positions, planet_wave_properties):
    aspects = []
    aspect_types = {
        "Conjunction": (0, 8), "Semi-sextile": (30, 2), "Sextile": (60, 6),
        "Square": (90, 8), "Trine": (120, 8), "Quincunx": (150, 4), "Opposition": (180, 8)
    }

    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            # Use ecliptic longitude for aspects
            lon1 = positions[p1].get('ecliptic_lon', 0)
            lon2 = positions[p2].get('ecliptic_lon', 0)
            if lon1 is None or lon2 is None:
                continue
            angle = min((lon1 - lon2) % 360, (lon2 - lon1) % 360)
            
            # Calculate wave interference
            freq1, amp1 = planet_wave_properties.get(p1, (0.5, 0.5))
            freq2, amp2 = planet_wave_properties.get(p2, (0.5, 0.5))
            phase_shift = abs(angle) * math.pi / 180
            coherence = abs(math.cos(phase_shift))
            energy = (amp1 * amp2) * coherence
            
            for aspect, (target_angle, orb) in aspect_types.items():
                if abs(angle - target_angle) <= orb:
                    aspects.append((p1, p2, aspect, round(angle, 2), energy, coherence))
    
    return aspects

# Function to calculate moon phase
def get_moon_phase(current_time):
    observer = ephem.Observer()
    observer.lat = '45.75415'
    observer.lon = '21.21621'
    observer.date = current_time
    moon = ephem.Moon()
    moon.compute(observer)
    sun = ephem.Sun()
    sun.compute(observer)
    elongation = float(ephem.separation(moon, sun))
    phase_angle = (elongation * 180 / math.pi) % 360
    for phase, angle in moon_phases:
        if phase_angle >= angle - 22.5 and phase_angle < angle + 22.5:
            return phase
    return "New"

# Function to plot the extended astrological map
def plot_elements_with_labels(planet_positions, sun_position, vedic_houses, moon_data, aspects, planet_wave_properties):
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.set_aspect('equal', 'box')
    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    
    radius_golden = 1.1
    square_size = radius_golden * np.sqrt(2)

    # Draw squares at 0° and 45° (adjusted for astrological orientation)
    draw_square(ax, (0, 0), square_size, angle=90, color='blue', label='Square at 0° (adjusted)')
    draw_square(ax, (0, 0), square_size, angle=135, color='red', label='Square at 45° (adjusted)')
    
    # Draw golden circle
    circle_golden = plt.Circle((0, 0), radius_golden, color='gold', fill=False, linestyle='-', linewidth=2, label='Golden Circle')
    ax.add_patch(circle_golden)

    # Draw zodiac wheel (adjusted for astrological orientation)
    for sign, start, element, modality, polarity in zodiac_signs:
        adjusted_start = 90 - start  # Rotate 90° clockwise
        adjusted_end = 90 - (start + 30)
        if adjusted_end < adjusted_start:
            adjusted_end += 360
        wedge = Wedge((0, 0), 1.5, adjusted_start, adjusted_end, facecolor=element_colors[element], alpha=0.3)
        ax.add_patch(wedge)
        angle = math.radians(90 - (start + 15))  # Center of the segment
        x = 1.6 * math.cos(angle)
        y = 1.6 * math.sin(angle)
        ax.text(x, y, sign, ha='center', va='center', fontsize=10, rotation=-(90 - (start + 15)))

    # Draw Vedic house boundaries and labels
    for house_num, house_name, start in vedic_houses:
        angle = math.radians(90 - start)
        x_house = 1.3 * np.cos(angle)
        y_house = 1.3 * np.sin(angle)
        ax.text(x_house * 1.15, y_house * 1.15, f'H{house_num}', fontsize=12, ha='center', va='center')

    # Draw 12-pointed star for Yearly Cycles (Orange)
    draw_12_pointed_star(ax, 1.8, color='orange')
    for cycle, start in yearly_cycles:
        angle = math.radians(90 - (start + 15))
        x = 1.9 * math.cos(angle)
        y = 1.9 * math.sin(angle)
        ax.text(x, y, cycle, ha='center', va='center', fontsize=8, color='orange')

    # Draw 12-pointed star for Triads of Mind (Purple)
    draw_12_pointed_star(ax, 2.1, color='purple')
    for triad, start in triads_of_mind:
        angle = math.radians(90 - (start + 15))
        x = 2.2 * math.cos(angle)
        y = 2.2 * math.sin(angle)
        ax.text(x, y, triad, ha='center', va='center', fontsize=8, color='purple')

    # Draw 12-pointed star for Tetrads of Physicality (Brown)
    draw_12_pointed_star(ax, 2.4, color='saddlebrown')
    for tetrad, start in tetrads_of_physicality:
        angle = math.radians(90 - (start + 15))
        x = 2.5 * math.cos(angle)
        y = 2.5 * math.sin(angle)
        ax.text(x, y, tetrad, ha='center', va='center', fontsize=8, color='saddlebrown')

    # Draw Moon phases
    moon_phase = moon_data['moon_phase']
    for phase, start in moon_phases:
        angle = math.radians(90 - start)
        x = 2.7 * math.cos(angle)
        y = 2.7 * math.sin(angle)
        color = 'red' if phase == moon_phase else 'black'
        ax.text(x, y, phase, ha='center', va='center', fontsize=8, color=color)

    # Draw intermediate stages (Hot, Dry, Cold, Wet)
    for stage, start in intermediate_stages:
        angle = math.radians(90 - start)
        x = 2.9 * math.cos(angle)
        y = 2.9 * math.sin(angle)
        ax.text(x, y, stage, ha='center', va='center', fontsize=8, color='black')

    # Draw Yin-Yang symbol for sacred geometry
    yin_yang = Circle((0, 0), 0.3, facecolor='black')
    ax.add_patch(yin_yang)
    yin_yang_half = Wedge((0, 0), 0.3, 0, 180, facecolor='white')
    ax.add_patch(yin_yang_half)
    small_circle1 = Circle((0, 0.15), 0.05, facecolor='white')
    small_circle2 = Circle((0, -0.15), 0.05, facecolor='black')
    ax.add_patch(small_circle1)
    ax.add_patch(small_circle2)

    # Plot planetary positions with symbols (adjust angles)
    for name, pos in planet_positions.items():
        ra_rad = np.radians(pos['RA'])
        dec_rad = np.radians(pos['DEC'])
        freq, amp = planet_wave_properties.get(name, (0.5, 0.5))
        radius = radius_golden + (amp * 0.1)
        # Adjust RA to match astrological orientation
        adjusted_ra_rad = math.radians(90 - math.degrees(ra_rad))
        x = radius * np.cos(dec_rad) * np.cos(adjusted_ra_rad)
        y = radius * np.cos(dec_rad) * np.sin(adjusted_ra_rad)
        ax.plot(x, y, 'o', label=f"{planet_symbols[name]} {name} (Freq: {freq})", markersize=10)

    # Plot the Sun (adjust angles)
    sun_ra_rad = np.radians(sun_position['RA'])
    sun_dec_rad = np.radians(sun_position['DEC'])
    adjusted_sun_ra_rad = math.radians(90 - math.degrees(sun_ra_rad))
    sun_x = radius_golden * np.cos(sun_dec_rad) * np.cos(adjusted_sun_ra_rad)
    sun_y = radius_golden * np.cos(sun_dec_rad) * np.sin(adjusted_sun_ra_rad)
    ax.plot(sun_x, sun_y, 'o', color='yellow', label=f"{planet_symbols['Sun']} Sun", markersize=10)

    # Draw aspects as lines with energy intensity (adjust angles)
    for p1, p2, aspect, angle, energy, coherence in aspects:
        pos1 = planet_positions.get(p1, sun_position if p1 == 'Sun' else None)
        pos2 = planet_positions.get(p2, sun_position if p2 == 'Sun' else None)
        if not pos1 or not pos2:
            continue
        ra1_rad = np.radians(pos1['RA'])
        dec1_rad = np.radians(pos1['DEC'])
        ra2_rad = np.radians(pos2['RA'])
        dec2_rad = np.radians(pos2['DEC'])
        adjusted_ra1_rad = math.radians(90 - math.degrees(ra1_rad))
        adjusted_ra2_rad = math.radians(90 - math.degrees(ra2_rad))
        x1 = radius_golden * np.cos(dec1_rad) * np.cos(adjusted_ra1_rad)
        y1 = radius_golden * np.cos(dec1_rad) * np.sin(adjusted_ra1_rad)
        x2 = radius_golden * np.cos(dec2_rad) * np.cos(adjusted_ra2_rad)
        y2 = radius_golden * np.cos(dec2_rad) * np.sin(adjusted_ra2_rad)
        ax.plot([x1, x2], [y1, y2], linestyle='--', alpha=energy, label=f"{p1}-{p2}: {aspect}")

    # Add element symbols around (adjust positions)
    element_positions = {
        'Fire': (2.8 * math.cos(math.radians(90 - 0)), 2.8 * math.sin(math.radians(90 - 0))),
        'Earth': (2.8 * math.cos(math.radians(90 - 180)), 2.8 * math.sin(math.radians(90 - 180))),
        'Air': (2.8 * math.cos(math.radians(90 - 90)), 2.8 * math.sin(math.radians(90 - 90))),
        'Water': (2.8 * math.cos(math.radians(90 - 270)), 2.8 * math.sin(math.radians(90 - 270)))
    }
    
    for element, (x_pos, y_pos) in element_positions.items():
        ax.text(x_pos, y_pos, f"{element_symbols[element]}", fontsize=15, ha='center', va='center')

    ax.set_title('AstroMap with Classical Elements, Planetary Positions, Vedic Houses, and Sacred Geometry', fontsize=16)
    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

# Function to get moon phase momentum (modified to include phase name)
def get_moon_phase_momentum(current_time):
    tz = pytz.timezone('Europe/Bucharest')  # Updated to the correct timezone for Timișoara
    current_time = tz.normalize(current_time.astimezone(tz))
    current_date = current_time.date()

    observer = ephem.Observer()
    observer.lat = '45.75415'
    observer.lon = '21.21621'
    observer.date = current_time

    moon = ephem.Moon()
    moon.compute(observer)
    sun = ephem.Sun()
    sun.compute(observer)

    moon_phase = moon.phase
    previous_new_moon = ephem.previous_new_moon(current_date)
    previous_new_moon_datetime = ephem.Date(previous_new_moon).datetime()
    previous_new_moon_datetime = previous_new_moon_datetime.replace(tzinfo=pytz.timezone('Europe/Bucharest'))
    moon_age = (current_time - previous_new_moon_datetime).days

    moon_sign = ephem.constellation(moon)[1]
    moon_ra = math.degrees(moon.ra)
    moon_dec = math.degrees(moon.dec)
    moon_distance_km = moon.earth_distance * ephem.meters_per_au / 1000
    moon_angular_diameter = math.degrees(moon.size / moon_distance_km)
    moon_speed_km_hr = moon_distance_km / (1 / 24)
    moon_energy = (moon_phase / 100) ** 2

    # Get moon phase name
    moon_phase_name = get_moon_phase(current_time)

    moon_data = {
        'moon_phase': moon_phase_name,
        'moon_phase_percent': moon_phase,
        'moon_age': moon_age,
        'moon_sign': moon_sign,
        'moon_ra': moon_ra,
        'moon_dec': moon_dec,
        'moon_distance_km': moon_distance_km,
        'moon_angular_diameter': moon_angular_diameter,
        'moon_speed_km_hr': moon_speed_km_hr,
        'moon_energy': moon_energy,
        'ecliptic_lon': math.degrees(ephem.Ecliptic(moon).lon) % 360
    }

    return moon_data

# Function to get planet positions with ecliptic coordinates
def get_planet_positions():
    now = Time.now()
    planets = [
        {'name': 'Mercury', 'id': '1', 'freq': 0.9, 'amp': 0.6},
        {'name': 'Venus', 'id': '2', 'freq': 0.6, 'amp': 0.9},
        {'name': 'Mars', 'id': '4', 'freq': 0.8, 'amp': 1.2},
        {'name': 'Jupiter', 'id': '5', 'freq': 0.4, 'amp': 1.5},
        {'name': 'Saturn', 'id': '6', 'freq': 0.3, 'amp': 1.0},
        {'name': 'Uranus', 'id': '7', 'freq': 0.2, 'amp': 0.7},
        {'name': 'Neptune', 'id': '8', 'freq': 0.1, 'amp': 0.5},
        {'name': 'Pluto', 'id': '9', 'freq': 0.15, 'amp': 0.8}
    ]

    planet_positions = {}
    planet_wave_properties = {}
    
    observer = ephem.Observer()
    observer.lat = '45.75415'
    observer.lon = '21.21621'
    observer.date = datetime.datetime.now(pytz.timezone('Europe/Bucharest'))  # Updated timezone

    for planet in planets:
        obj = Horizons(id=planet['id'], location='500', epochs=now.jd)
        eph = obj.ephemerides()[0]
        planet_positions[planet['name']] = {'RA': eph['RA'], 'DEC': eph['DEC']}
        
        # Get ecliptic longitude using ephem
        ephem_planet = getattr(ephem, planet['name'])()
        ephem_planet.compute(observer)
        ecliptic_lon = math.degrees(ephem.Ecliptic(ephem_planet).lon) % 360
        planet_positions[planet['name']]['ecliptic_lon'] = ecliptic_lon
        planet_wave_properties[planet['name']] = (planet['freq'], planet['amp'])
    
    # Add Moon
    moon_data = get_moon_phase_momentum(datetime.datetime.now(pytz.timezone('Europe/Bucharest')))
    planet_positions['Moon'] = {
        'RA': moon_data['moon_ra'],
        'DEC': moon_data['moon_dec'],
        'ecliptic_lon': moon_data['ecliptic_lon']
    }
    planet_wave_properties['Moon'] = (0.7, 0.8)

    # Add Sun
    sun_position = get_sun_position()
    sun = ephem.Sun()
    sun.compute(observer)
    ecliptic_lon = math.degrees(ephem.Ecliptic(sun).lon) % 360
    sun_position['ecliptic_lon'] = ecliptic_lon
    planet_positions['Sun'] = sun_position
    planet_wave_properties['Sun'] = (0.5, 1.0)

    return planet_positions, planet_wave_properties

def get_sun_position():
    now = Time.now()
    obj = Horizons(id='10', location='500', epochs=now.jd)
    eph = obj.ephemerides()[0]
    return {'RA': eph['RA'], 'DEC': eph['DEC']}

# Main execution
if __name__ == "__main__":
    current_time = datetime.datetime.now(pytz.timezone('Europe/Bucharest'))  # Updated timezone
    observer_coords = {'longitude': '21.21621', 'latitude': '45.75415'}

    # Print the current local time for verification
    print(f"Current Local Time in Timișoara (Europe/Bucharest): {current_time}")

    # Get moon phase and other details
    moon_data = get_moon_phase_momentum(current_time)
    print("\nMoon Data:")
    for key, value in moon_data.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Get planetary positions
    planet_positions, planet_wave_properties = get_planet_positions()
    sun_position = planet_positions['Sun']
    print("\nPlanetary Positions:")
    for planet, pos in planet_positions.items():
        print(f"{planet} - RA: {pos['RA']}, DEC: {pos['DEC']}, Ecliptic Lon: {pos.get('ecliptic_lon', 'N/A')}")

    # Calculate aspects
    aspects = calculate_aspects(planet_positions, planet_wave_properties)
    print("\nAspects Between Planets with Energy and Coherence:")
    for p1, p2, aspect, angle, energy, coherence in aspects:
        print(f"{p1} {aspect} {p2} ({angle}°) - Energy: {energy:.2f}, Coherence: {coherence:.2f}")

    # Get Vedic houses
    vedic_houses_dict = get_vedic_houses(current_time, observer_coords)
    print("\nVedic Houses:")
    for house, sign in vedic_houses_dict.items():
        print(f"House {house}: {sign}")

    # Plot everything
    plot_elements_with_labels(planet_positions, sun_position, vedic_houses, moon_data, aspects, planet_wave_properties)
