import ephem
from datetime import datetime, timedelta, timezone
import pytz
import geocoder
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import random

# --- Configuration and Data ---

# Get current date and time
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
print(f"Current Date and Time: {formatted_datetime}")

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
observer.date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

# Local timezone
local_tz = datetime.now().astimezone().tzinfo
input_time = datetime.now(local_tz)

# Zodiac signs and enhanced attributes
zodiac_signs = [
    ("Aries", 0, "Fire", "Cardinal", "+", "hot", "dry", "Eris – The Inciter", "Triangle (3)", "Tetrahedron"),
    ("Taurus", 30, "Earth", "Fixed", "-", "cold", "dry", "Mammon – The Accumulator", "Square (4)", "Cube"),
    ("Gemini", 60, "Air", "Mutable", "+", "hot", "wet", "Mercurius – The Messenger", "Pentagram (5)", "Octahedron"),
    ("Cancer", 90, "Water", "Cardinal", "-", "cold", "wet", "Leviathan – The Keeper", "Circle within Square", "Icosahedron"),
    ("Leo", 120, "Fire", "Fixed", "+", "hot", "dry", "Lucifer – The Luminary", "Hexagram (6)", "Tetrahedron (refined)"),
    ("Virgo", 150, "Earth", "Mutable", "-", "cold", "dry", "Aka Manah – The Purifier", "Heptagon (7)", "Cube (refined)"),
    ("Libra", 180, "Air", "Cardinal", "+", "hot", "wet", "Ashtaroth – The Balancer", "Octagon (8)", "Octahedron (refined)"),
    ("Scorpio", 210, "Water", "Fixed", "-", "cold", "wet", "Abaddon – The Transformer", "Nonagon (9)", "Icosahedron (deep)"),
    ("Sagittarius", 240, "Fire", "Mutable", "+", "hot", "dry", "Belial – The Seeker", "Triangle & Circle fusion", "Tetrahedron"),
    ("Capricorn", 270, "Earth", "Cardinal", "-", "cold", "dry", "Samael – The Builder", "Cube & Mountain Pyramid", "Cube (primal)"),
    ("Aquarius", 300, "Air", "Fixed", "+", "hot", "wet", "Prometheus – The Awakener", "Star Polygon (11)", "Octahedron"),
    ("Pisces", 330, "Water", "Mutable", "-", "cold", "wet", "Choronzon – The Dreamer", "Vesica Piscis & Circle", "Icosahedron (highest octave)")
]

# Planets with added frequency and energy dynamics
planets = {
    "Sun": {"obj": ephem.Sun(), "frequency": "~126.22 Hz", "potential": "Moderate", "kinetic": "High"},
    "Moon": {"obj": ephem.Moon(), "frequency": "~210.42 Hz", "potential": "High", "kinetic": "Moderate"},
    "Mercury": {"obj": ephem.Mercury(), "frequency": "~141.27 Hz", "potential": "Moderate", "kinetic": "High"},
    "Venus": {"obj": ephem.Venus(), "frequency": "~221.23 Hz", "potential": "Very High", "kinetic": "Low"},
    "Mars": {"obj": ephem.Mars(), "frequency": "~306 Hz", "potential": "High", "kinetic": "Very High"},
    "Jupiter": {"obj": ephem.Jupiter(), "frequency": "~183.58 Hz", "potential": "Moderate", "kinetic": "High"},
    "Saturn": {"obj": ephem.Saturn(), "frequency": "~147.85 Hz", "potential": "Very High", "kinetic": "Low to Moderate"},
    "Uranus": {"obj": ephem.Uranus(), "frequency": "~207.36 Hz", "potential": "High", "kinetic": "High"},
    "Neptune": {"obj": ephem.Neptune(), "frequency": "~211.44 Hz", "potential": "High", "kinetic": "Low to Moderate"},
    "Pluto": {"obj": ephem.Pluto(), "frequency": "~306 Hz (resonance)", "potential": "Very High", "kinetic": "High"} # Using Mars freq for Pluto resonance as in your text
}

# Element colors
element_colors = {"Fire": "orange", "Earth": "green", "Air": "yellow", "Water": "blue"}
connection_colors = {"Fire": "orange", "Earth": "green", "Air": "purple", "Water": "blue"}
element_groups = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

# I Ching hexagrams (simplified for integration)
iching_hexagrams = [
    (1, "Ch'ien", "The Creative", "Strength, initiative", [1, 1, 1, 1, 1, 1]),
    (2, "K'un", "The Receptive", "Devotion, adaptability", [0, 0, 0, 0, 0, 0]),
    (3, "Chun", "Difficulty at the Beginning", "Perseverance through obstacles", [1, 0, 0, 0, 1, 0]),
    (4, "Meng", "Youthful Folly", "Learning, openness", [0, 1, 0, 0, 0, 1]),
    (5, "Hsu", "Waiting", "Patience, preparation", [1, 1, 1, 0, 1, 0]),
    (6, "Sung", "Conflict", "Resolution, clarity", [0, 1, 0, 1, 1, 1]),
    (7, "Shih", "The Army", "Discipline, organization", [0, 0, 0, 0, 1, 0]),
    (8, "Pi", "Holding Together (Union)", "Support, unity", [0, 1, 0, 0, 0, 0]),
    (9, "Hsiao Ch'u", "The Taming Power of the Small", "Restraint, gentle influence", [1, 1, 0, 1, 1, 1]),
    (10, "Lu", "Treading (Conduct)", "Careful steps, proper behavior", [1, 1, 1, 0, 1, 1]),
    (11, "T'ai", "Peace", "Harmony, prosperity", [1, 1, 1, 0, 0, 0]),
    (12, "P'i", "Standstill (Stagnation)", "Blockage, difficulty", [0, 0, 0, 1, 1, 1]),
    (13, "T'ung Jen", "Fellowship with Men", "Community, shared goals", [1, 0, 1, 1, 1, 1]),
    (14, "Ta Yu", "Possession in Great Measure", "Abundance, greatness", [1, 1, 1, 1, 0, 1]),
    (15, "Ch'ien", "Modesty", "Humility, respect", [0, 0, 0, 1, 0, 0]),
    (16, "Yu", "Enthusiasm", "Inspiration, joy", [0, 0, 1, 0, 0, 0]),
    (17, "Sui", "Following", "Adaptability, going with the flow", [0, 1, 1, 0, 0, 0]),
    (18, "Ku", "Work on What has been Spoiled (Decay)", "Repair, renewal", [0, 0, 0, 1, 1, 0]),
    (19, "Lin", "Approach", "Growth, proximity", [1, 1, 0, 0, 0, 0]),
    (20, "Kuan", "Contemplation (View)", "Observation, insight", [0, 0, 0, 0, 1, 1]),
    (21, "Shih Ho", "Biting Through", "Resolution, overcoming obstacles", [1, 0, 1, 1, 0, 1]),
    (22, "Pi", "Grace", "Beauty, adornment", [1, 0, 0, 1, 0, 0]),
    (23, "Po", "Splitting Apart", "Deterioration, decline", [0, 0, 0, 0, 0, 1]),
    (24, "Fu", "Return (The Turning Point)", "Rebirth, renewal", [1, 0, 0, 0, 0, 0]),
    (25, "Wu Wang", "Innocence (The Unexpected)", "Purity, naturalness", [1, 0, 0, 1, 1, 1]),
    (26, "Ta Ch'u", "The Taming Power of the Great", "Accumulation, great potential", [1, 1, 1, 0, 0, 1]),
    (27, "I", "The Corners of the Mouth (Nourishment)", "Sustenance, care", [1, 0, 0, 0, 0, 1]),
    (28, "Ta Kuo", "Preponderance of the Great", "Critical mass, transition", [0, 1, 1, 1, 1, 0]),
    (29, "K'an", "The Abysmal (Water)", "Danger, perseverance", [0, 1, 0, 0, 1, 0]),
    (30, "Li", "The Clinging, Fire", "Brightness, clarity", [1, 0, 1, 1, 0, 1]),
    (31, "Hsien", "Influence (Wooing)", "Attraction, connection", [0, 0, 1, 1, 1, 0]),
    (32, "Heng", "Duration", "Perseverance, continuity", [0, 1, 1, 0, 1, 1]),
    (33, "Tun", "Retreat", "Withdrawal, prudence", [0, 0, 1, 1, 1, 1]),
    (34, "Ta Chuang", "The Power of the Great", "Strength, assertion", [1, 1, 1, 1, 0, 0]),
    (35, "Chin", "Progress", "Advancement, illumination", [0, 0, 0, 1, 0, 1]),
    (36, "Ming I", "Darkening of the Light", "Suppression, perseverance in adversity", [1, 0, 1, 0, 0, 0]),
    (37, "Chia Jen", "The Family (The Clan)", "Harmony, order within the home", [1, 0, 1, 0, 1, 1]),
    (38, "K'uei", "Opposition", "Estrangement, divergence", [1, 1, 0, 1, 0, 1]),
    (39, "Chien", "Obstruction (Limping)", "Difficulty, patience", [0, 1, 0, 1, 0, 0]),
    (40, "Hsieh", "Deliverance", "Release, resolution", [0, 0, 1, 0, 1, 0]),
    (41, "Sun", "Decrease", "Reduction, sincerity", [1, 1, 0, 0, 0, 1]),
    (42, "I", "Increase", "Growth, benefit", [1, 0, 0, 0, 1, 1]),
    (43, "Kuai", "Break-through (Resoluteness)", "Decision, breakthrough", [1, 1, 1, 1, 1, 0]),
    (44, "Kou", "Coming to Meet", "Encounter, unexpected connection", [0, 1, 1, 1, 1, 1]),
    (45, "Ts'ui", "Gathering Together (Massing)", "Assembly, union", [0, 0, 1, 1, 0, 0]),
    (46, "Sheng", "Pushing Upward", "Advancement, progress", [0, 1, 1, 0, 0, 0]),
    (47, "K'un", "Oppression (Exhaustion)", "Adversity, perseverance", [0, 1, 0, 1, 1, 0]),
    (48, "Ching", "The Well", "Nourishment, reliability", [0, 0, 1, 0, 1, 0]),
    (49, "Ko", "Revolution (Molting)", "Change, transformation", [1, 0, 1, 1, 1, 0]),
    (50, "Ting", "The Cauldron", "Stability, nourishment", [0, 1, 1, 1, 0, 1]),
    (51, "Chen", "The Arousing (Thunder)", "Shock, awakening", [1, 0, 0, 1, 0, 0]),
    (52, "Ken", "Keeping Still (Mountain)", "Stillness, meditation", [0, 0, 1, 0, 0, 1]),
    (53, "Chien", "Development (Gradual Progress)", "Slow and steady advancement", [0, 0, 1, 0, 1, 1]),
    (54, "Kuei Mei", "The Marrying Maiden", "Relationships, progression", [1, 1, 0, 1, 0, 0]),
    (55, "Feng", "Abundance (Fullness)", "Prosperity, culmination", [1, 0, 1, 1, 0, 0]),
    (56, "Lu", "The Wanderer", "Travel, detachment", [0, 0, 1, 0, 1, 1]),
    (57, "Sun", "The Gentle (The Penetrating Wind)", "Subtlety, influence", [0, 1, 1, 0, 1, 0]),
    (58, "Tui", "The Joyous (Lake)", "Pleasure, communication", [1, 1, 0, 1, 1, 0]),
    (59, "Huan", "Dispersion (Dissolution)", "Dissipation, release", [0, 1, 0, 0, 0, 1]),
    (60, "Chieh", "Limitation", "Restriction, discipline", [0, 0, 1, 0, 1, 1]),
    (61, "Chung Fu", "Inner Truth", "Sincerity, trust", [1, 1, 0, 0, 1, 1]),
    (62, "Hsiao Kuo", "Preponderance of the Small", "Attention to detail, humility", [0, 0, 1, 1, 0, 0]),
    (63, "Chi Chi", "After Completion", "Success, caution", [1, 0, 1, 0, 1, 0]),
    (64, "Wei Chi", "Before Completion", "Transition, caution", [0, 1, 0, 1, 0, 1])
]


# --- Functions ---

# Moon phase calculation
def get_moon_phase(observer):
    moon = ephem.Moon()
    moon.compute(observer)
    sun = ephem.Sun()
    sun.compute(observer)
    phase_angle = (moon.elong * 180 / math.pi) % 360
    if 0 <= phase_angle < 5 or 355 <= phase_angle < 360:
        phase_name = "New Moon"
    elif 5 <= phase_angle < 67.5:
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

# Zodiac sign determination with enhanced attributes
def get_zodiac_sign(longitude):
    longitude = math.degrees(longitude) % 360
    for sign, start, element, modality, polarity, q1, q2, demon, geometry, solid in zodiac_signs:
        if start <= longitude < start + 30:
            return sign, element, modality, polarity, q1, q2, demon, geometry, solid
    # Fallback for the last sign (Pisces)
    return zodiac_signs[-1][0], zodiac_signs[-1][2], zodiac_signs[-1][3], zodiac_signs[-1][4], zodiac_signs[-1][5], zodiac_signs[-1][6], zodiac_signs[-1][7], zodiac_signs[-1][8], zodiac_signs[-1][9]

# Aspects calculation
def calculate_aspects(positions):
    aspects = []
    aspect_types = {
        "Conjunction": (0, 8),
        "Sextile": (60, 6),
        "Square": (90, 6),
        "Trine": (120, 8),
        "Opposition": (180, 8)
    }
    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            lon1, lon2 = positions[p1], positions[p2]
            angle = min((lon1 - lon2) % 360, (lon2 - lon1) % 360)
            for aspect, (target, orb) in aspect_types.items():
                if abs(angle - target) <= orb:
                    aspects.append((p1, p2, aspect, round(angle, 2)))
    return aspects

# Elemental connections drawing
def draw_elemental_connections(ax, radius=1.0):
    for element, signs in element_groups.items():
        color = connection_colors[element]
        angles = [math.radians(start + 15) for s, start, *_ in zodiac_signs if s in signs]
        for i in range(len(angles)):
            for j in range(i + 1, len(angles)):
                x1, y1 = radius * math.cos(angles[i]), radius * math.sin(angles[i])
                x2, y2 = radius * math.cos(angles[j]), radius * math.sin(angles[j])
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.5, alpha=0.7)

# I Ching generation based on astrological data
def generate_iching_hexagram(phase_angle, asc_deg):
    # Use moon phase angle and ascendant degree to seed the hexagram
    # A more sophisticated mapping could be developed
    seed_value = int(phase_angle + asc_deg) % 64
    # Ensure the seed maps to a valid index (0-63) for hexagram list
    hex_index = seed_value
    return iching_hexagrams[hex_index]

# I Ching hexagram visualization (basic text lines)
def visualize_hexagram(hexagram_lines):
    line_map = {1: "---", 0: "-- --"}
    print("\nI Ching Hexagram Visualization:")
    print("-" * 40)
    # I Ching lines are traditionally read from bottom to top
    for line_value in reversed(hexagram_lines):
        print(line_map[line_value])
    print("-" * 40)

# Calculate house cusps (Equal House system for simplicity)
def calculate_house_cusps(asc_deg):
    houses = {}
    for i in range(1, 13):
        cusp = (asc_deg + (i - 1) * 30) % 360
        houses[f"House {i}"] = cusp
    return houses

# Get Syzygy for the last New or Full Moon
def get_syzygy(observer, current_date):
    moon = ephem.Moon()
    sun = ephem.Sun()
    current_dt = ephem.Date(current_date).datetime()
    observer.date = ephem.Date(current_dt - timedelta(days=15))
    for _ in range(30):
        moon.compute(observer)
        sun.compute(observer)
        elong = abs((moon.elong * 180 / math.pi) % 360)
        if elong < 5 or abs(elong - 180) < 5:
             # Calculate longitude at the time of syzygy
            syzygy_lon = math.degrees(ephem.Ecliptic(moon).lon) % 360
            observer.date = ephem.Date(current_dt) # Reset observer date
            return syzygy_lon
        observer.date += 1
    observer.date = ephem.Date(current_dt) # Reset observer date if no syzygy found in 30 days
    return 0

# Arabic Parts (Lots) Calculator
def calculate_lot(personal_point, significator, trigger, positions, asc_deg):
    pp = asc_deg if personal_point == "ASC" else positions.get(personal_point, 0)
    sig = positions.get(significator, 0)
    trig = positions.get(trigger, 0)
    lot_deg = (pp + sig - trig) % 360
    sign, *_ = get_zodiac_sign(math.radians(lot_deg))
    return lot_deg, sign

# Astrological wheel plot with aspect lines and enhanced labels
def plot_astrological_wheel(positions, moon_phase, local_time_str, aspects, house_cusps):
    fig, ax = plt.subplots(figsize=(12, 12)) # Increased figure size
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw zodiac signs
    for sign, start, element, modality, polarity, q1, q2, demon, geometry, solid in zodiac_signs:
        wedge = Wedge((0, 0), 1, start, start + 30, facecolor=element_colors[element], alpha=0.3)
        ax.add_patch(wedge)
        angle = math.radians(start + 15)
        # Position text labels further out
        ax.text(1.15 * math.cos(angle), 1.15 * math.sin(angle), sign, ha='center', va='center', fontsize=10, rotation=-(start + 15))
        # Add more details to the sign labels
        sign_details = f"{element}\n{modality}, {polarity}\n{q1}, {q2}\n{demon}\n{geometry}\n{solid}"
        ax.text(0.75 * math.cos(angle), 0.75 * math.sin(angle), sign_details, ha='center', va='center', fontsize=7)

    # Draw elemental connections
    draw_elemental_connections(ax)

    # Draw house cusps
    for house, cusp in house_cusps.items():
        angle = math.radians(360 - cusp + 90)
        x1, y1 = 0.95 * math.cos(angle), 0.95 * math.sin(angle)
        x2, y2 = 1.05 * math.cos(angle), 1.05 * math.sin(angle)
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1, alpha=0.5)
        ax.text(x2 * 1.08, y2 * 1.08, house, fontsize=8, ha='center', va='center') # Adjusted house label position

    # Draw planets
    planet_offset = 0.05 # Offset for planet labels
    for name, data in planets.items():
        planet = data["obj"]
        planet.compute(observer)
        lon = ephem.Ecliptic(planet).lon
        positions[name] = math.degrees(lon) % 360
        angle = math.radians(360 - positions[name] + 90)
        x, y = 0.9 * math.cos(angle), 0.9 * math.sin(angle)
        ax.plot(x, y, 'o', label=name)
        # Add planet details next to the symbol
        planet_details = f"{name}\nFreq: {data['frequency']}\nPot: {data['potential']}\nKin: {data['kinetic']}"
        ax.text(x * (1 + planet_offset), y * (1 + planet_offset), planet_details, fontsize=7)


    # Draw aspect lines
    aspect_styles = {
        "Conjunction": ("red", 1.5, "-"),
        "Sextile": ("green", 1, "--"),
        "Square": ("orange", 1.5, "-"),
        "Trine": ("blue", 1, "--"),
        "Opposition": ("purple", 1.5, "-")
    }
    for p1, p2, aspect, _ in aspects:
        lon1, lon2 = positions[p1], positions[p2]
        angle1 = math.radians(360 - lon1 + 90)
        angle2 = math.radians(360 - lon2 + 90)
        x1, y1 = 0.9 * math.cos(angle1), 0.9 * math.sin(angle1)
        x2, y2 = 0.9 * math.cos(angle2), 0.9 * math.sin(angle2)
        color, linewidth, linestyle = aspect_styles.get(aspect, ("gray", 1, "-"))
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, linestyle=linestyle, alpha=0.6)

    # Add central text
    ax.text(0, 0, f"Astrological Clock\n{local_time_str}\nMoon Phase: {moon_phase}", ha='center', va='center', fontsize=12, color='purple')
    # Removed legend as planet details are next to symbols
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title("Astrological Wheel with Enhanced Details")
    plt.show()

# Main astrological clock function
def astrological_clock():
    sun = ephem.Sun()
    sunrise_utc = observer.next_rising(sun).datetime()
    sunset_utc = observer.next_setting(sun).datetime()
    sunrise_local = pytz.utc.localize(sunrise_utc).astimezone(local_tz)
    sunset_local = pytz.utc.localize(sunset_utc).astimezone(local_tz)
    observer.date += 1  # To get next day's sunrise for nighttime boundary
    next_sunrise_utc = observer.previous_rising(sun).datetime()
    next_sunrise_local = pytz.utc.localize(next_sunrise_utc).astimezone(local_tz)
    observer.date -= 1

    # Check current time
    now = datetime.now(local_tz)

    # Determine the current stage
    print("\nTime of Day:")
    print("-" * 40)
    if sunrise_local <= now < sunrise_local + timedelta(hours=1):
        print("It's Early Morning!")
    elif sunrise_local + timedelta(hours=1) <= now < sunrise_local + timedelta(hours=3):
        print("It's Morning!")
    elif sunrise_local + timedelta(hours=3) <= now < sunrise_local + timedelta(hours=5):
        print("It's Noon!")
    elif sunrise_local + timedelta(hours=5) <= now < sunset_local - timedelta(hours=1):
        print("It's Afternoon!")
    elif sunset_local - timedelta(hours=1) <= now < sunset_local:
        print("It's Late Afternoon!")
    elif sunset_local <= now < next_sunrise_local:
        print("It's Nighttime!")
    else:
        print("Time of day not precisely matched within defined ranges.")


    # Output sunrise and sunset times for reference
    print(f"Sunrise: {sunrise_local.strftime('%H:%M:%S %Z')}")
    print(f"Sunset: {sunset_local.strftime('%H:%M:%S %Z')}")
    print(f"Next Sunrise: {next_sunrise_local.strftime('%H:%M:%S %Z')}")

    # Set observer to current UTC time for planetary positions
    observer.date = datetime.now(timezone.utc)

    # Planetary positions with enhanced details
    positions = {}
    print("\nPlanetary Positions and Attributes:")
    print("-" * 40)
    for name, data in planets.items():
        planet = data["obj"]
        planet.compute(observer)
        lon = ephem.Ecliptic(planet).lon
        positions[name] = math.degrees(lon) % 360
        sign, element, modality, polarity, q1, q2, demon, geometry, solid = get_zodiac_sign(lon)
        print(f"{name}: {positions[name]:.2f}° in {sign}")
        print(f"  - Element/Modality/Polarity: {element}, {modality}, {polarity}")
        print(f"  - Qualities: {q1}, {q2}")
        print(f"  - Frequency: {data['frequency']}")
        print(f"  - Energy: Potential ({data['potential']}), Kinetic ({data['kinetic']})")
        print(f"  - Sacred Geometry: {geometry}")
        print(f"  - Platonic Solid: {solid}")
        print("-" * 40)


    # Ascendant
    # Calculate Ascendant in tropical degrees
    observer.date = datetime.now(timezone.utc) # Ensure observer date is current UTC
    # Calculate Sidereal Time
    sidereal_time = observer.sidereal_time()
    # Calculate RA of Ascendant
    ra_asc = math.atan2(-math.cos(sidereal_time), -math.sin(sidereal_time) * math.cos(observer.lat))
    ra_asc = math.degrees(ra_asc) % 360

    # Convert RA to Ecliptic Longitude (Approximation - more accurate methods exist)
    # This conversion is complex and depends on the obliquity of the ecliptic.
    # A simpler approximation using right ascension and declination could be used,
    # or we can rely on ephem's internal calculations if a specific method is needed.
    # For this script, let's use a simplified approach that might not be perfectly accurate
    # compared to professional ephemeris software for ecliptic longitude from RA.
    # A more robust approach would involve solving the spherical triangle.

    # Let's use a simplified method for demonstration, acknowledging it's an approximation.
    # A common approximation: convert RA to degrees and add/subtract based on hemisphere and time.
    # A better approach would involve ephem's internal calculations if available for Ascendant ecliptic.
    # Ephem's observer.radec_of(0,0) gives RA/Dec of Zenith, not directly Ascendant Ecliptic.
    # Let's stick to the RA of the Ascendant for now and note the approximation.

    # For plotting and Lot calculations, we need an ecliptic degree.
    # A common simplification is to relate RA of Ascendant to Ecliptic Longitude.
    # A more accurate way involves the observer's location and current sidereal time
    # to find the intersection of the eastern horizon with the ecliptic.
    # Ephem's `star.compute(observer)` calculates the position of a celestial body
    # for the observer. We need the position of the *point* on the ecliptic.

    # Let's revert to a common method for calculating Ascendant Ecliptic Longitude
    # using Sidereal Time, Latitude, and Obliquity of the Ecliptic.
    # Obliquity of the Ecliptic (approximate)
    obliquity = math.radians(23.43928)
    sin_st = math.sin(sidereal_time)
    cos_st = math.cos(sidereal_time)
    sin_lat = math.sin(observer.lat)
    cos_lat = math.cos(observer.lat)
    sin_obl = math.sin(obliquity)
    cos_obl = math.cos(obliquity)

    # Calculate Ecliptic Longitude of Ascendant (lambda_asc)
    # Using formula: tan(lambda_asc) = -cos(ST) / (sin(ST) * cos(obliquity) + tan(latitude) * sin(obliquity))
    denominator = sin_st * cos_obl + sin_lat / cos_lat * sin_obl
    if abs(denominator) < 1e-9: # Handle division by zero near poles or specific times
         lambda_asc = math.radians(90 if -cos_st > 0 else 270) # Approximation
    else:
         lambda_asc = math.atan2(-cos_st, denominator)

    asc_deg = math.degrees(lambda_asc) % 360

    print(f"Ascendant (Ecliptic Longitude): {asc_deg:.2f}°")

    # Moon phase
    print("\nMoon Phase:")
    print("-" * 40)
    moon_phase, phase_angle = get_moon_phase(observer)
    print(f"Moon Phase: {moon_phase} (Phase Angle: {phase_angle:.2f}°)")

    # Aspects
    print("\nAspects Between Planets:")
    print("-" * 40)
    aspects = calculate_aspects(positions)
    if aspects:
        for p1, p2, aspect, angle in aspects:
            print(f"{p1} {aspect} {p2} ({angle}°)")
    else:
        print("No major aspects found.")

    # Arabic Parts
    print("\nArabic Parts (Lots):")
    print("-" * 40)
    syzygy_deg = get_syzygy(observer, observer.date)
    fortune_deg, fortune_sign = calculate_lot("ASC", "Moon", "Sun", positions, asc_deg)
    spirit_deg, spirit_sign = calculate_lot("ASC", "Sun", "Moon", positions, asc_deg)
    eros_deg, eros_sign = calculate_lot("ASC", "Venus", "Mars", positions, asc_deg)

    print(f"Lot of Fortune: {fortune_deg:.2f}° in {fortune_sign}")
    print(f"Lot of Spirit: {spirit_deg:.2f}° in {spirit_sign}")
    print(f"Lot of Eros: {eros_deg:.2f}° in {eros_sign}")
    print(f"Syzygy (Prior New/Full Moon): {syzygy_deg:.2f}°")

    # I Ching hexagram
    print("\nI Ching Divination:")
    print("-" * 40)
    hex_num, hex_name, hex_title, hex_meaning, hexagram_lines = generate_iching_hexagram(phase_angle, asc_deg)
    print(f"Hexagram {hex_num}: {hex_name} ({hex_title})")
    print(f"Meaning: {hex_meaning}")
    visualize_hexagram(hexagram_lines)

    # House cusps
    print("\nHouse Cusps (Equal House System):")
    print("-" * 40)
    house_cusps = calculate_house_cusps(asc_deg)
    for house, cusp in house_cusps.items():
        sign, *_ = get_zodiac_sign(math.radians(cusp))
        print(f"{house}: {cusp:.2f}° in {sign}")

    # Plot
    local_time_str = input_time.strftime("%B %d, %Y, %H:%M %Z")
    print("\nGenerating Astrological Wheel Plot...")
    plot_astrological_wheel(positions, moon_phase, local_time_str, aspects, house_cusps)

# --- Run the clock ---
if __name__ == "__main__":
    print(f"Astrological Clock for {input_time.strftime('%B %d, %Y, %H:%M %Z')} (Current Location)")
    print("=" * 50)
    astrological_clock()