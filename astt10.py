import ephem
from datetime import datetime, timedelta
import pytz
import geocoder
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

# Get current date and time
current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
print(f"Current Date and Time: {formatted_datetime}")
year, month, day = current_datetime.year, current_datetime.month, current_datetime.day
hour, minute, second = current_datetime.hour, current_datetime.minute, current_datetime.second
print(f"Year: {year}\nMonth: {month}\nDay: {day}\nHour: {hour}\nMinute: {minute}\nSecond: {second}")

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
observer.date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)  # Start of current UTC day

# Local timezone
local_tz = datetime.now().astimezone().tzinfo
input_time = datetime.now(local_tz)

# Zodiac signs and attributes
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

# Planets
planets = {
    "Sun": ephem.Sun(), "Moon": ephem.Moon(), "Mercury": ephem.Mercury(), 
    "Venus": ephem.Venus(), "Mars": ephem.Mars(), "Jupiter": ephem.Jupiter(), 
    "Saturn": ephem.Saturn(), "Uranus": ephem.Uranus(), "Neptune": ephem.Neptune(), 
    "Pluto": ephem.Pluto()
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

# Zodiac sign determination
def get_zodiac_sign(longitude):
    longitude = math.degrees(longitude) % 360
    for sign, start, element, modality, polarity, q1, q2 in zodiac_signs:
        if start <= longitude < start + 30:
            return sign, element, modality, polarity, q1, q2
    return "Pisces", "Water", "Mutable", "-", "cold", "wet"

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

# Elemental connections
def draw_elemental_connections(ax, radius=1.0):
    for element, signs in element_groups.items():
        color = connection_colors[element]
        angles = [math.radians(start + 15) for s, start, *_ in zodiac_signs if s in signs]
        for i in range(len(angles)):
            for j in range(i + 1, len(angles)):
                x1, y1 = radius * math.cos(angles[i]), radius * math.sin(angles[i])
                x2, y2 = radius * math.cos(angles[j]), radius * math.sin(angles[j])
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.5, alpha=0.7)

# Astrological wheel plot
def plot_astrological_wheel(positions, moon_phase, local_time_str):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')
    for sign, start, element, modality, polarity, q1, q2 in zodiac_signs:
        wedge = Wedge((0, 0), 1, start, start + 30, facecolor=element_colors[element], alpha=0.3)
        ax.add_patch(wedge)
        angle = math.radians(start + 15)
        ax.text(1.1 * math.cos(angle), 1.1 * math.sin(angle), sign, ha='center', va='center', fontsize=10, rotation=-(start + 15))
        ax.text(0.7 * math.cos(angle), 0.7 * math.sin(angle), f"{element}\n{modality}\n{polarity}\n{q1}, {q2}", ha='center', va='center', fontsize=8)
    draw_elemental_connections(ax)
    for planet, lon in positions.items():
        angle = math.radians(360 - lon + 90)
        x, y = 0.9 * math.cos(angle), 0.9 * math.sin(angle)
        ax.plot(x, y, 'o', label=planet)
        ax.text(x * 1.05, y * 1.05, planet, fontsize=8)
    ax.text(0, 0, f"THE 12 SIGNS\nMoon Phase: {moon_phase}", ha='center', va='center', fontsize=14, color='purple')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"Astrological Wheel for {local_time_str}")
    plt.show()

# Arabic Parts (Lots) Calculator
def calculate_lot(personal_point, significator, trigger, positions, asc_deg):
    pp = asc_deg if personal_point == "ASC" else positions.get(personal_point, 0)
    sig = positions.get(significator, 0)
    trig = positions.get(trigger, 0)
    lot_deg = (pp + sig - trig) % 360
    sign, *_ = get_zodiac_sign(math.radians(lot_deg))
    return lot_deg, sign

def evaluate_lot_energy(lot_deg, positions, aspects):
    """ Determine the general status of the Arabic Lot based on its aspects with all planets. """
    score = 0
    up_threshold = 15  # Angle within which we consider "UP"
    
    for aspect in aspects:
        p1, p2, aspect_type, angle = aspect
        angle_to_lot = abs(lot_deg - (positions[p2] if p2 in positions else 0)) % 360
        
        # Evaluate influences
        if abs(angle_to_lot) <= up_threshold:  # Positive influence
            score += 1
        elif aspect_type == "Opposition":  # Negative influence
            score -= 1
    
    if score > 0:
        return f"{lot_deg:.2f}° is UP due to positive aspects"
    elif score < 0:
        return f"{lot_deg:.2f}° is DOWN due to negative aspects"
    else:
        return f"{lot_deg:.2f}° is NEUTRAL"

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
            return math.degrees(ephem.Ecliptic(moon).lon) % 360
        observer.date += 1
    return 0

# Main astrological clock function
def astrological_clock():
    sun = ephem.Sun()
    sunrise_utc = observer.previous_rising(sun).datetime()
    sunset_utc = observer.next_setting(sun).datetime()
    sunrise_local = pytz.utc.localize(sunrise_utc).astimezone(local_tz)
    sunset_local = pytz.utc.localize(sunset_utc).astimezone(local_tz)
    observer.date += 1  # To get next day's sunrise for nighttime boundary
    next_sunrise_utc = observer.previous_rising(sun).datetime()
    next_sunrise_local = pytz.utc.localize(next_sunrise_utc).astimezone(local_tz)
    observer.date -= 1

    # Define the stages
    early_morning_end = sunrise_local + timedelta(hours=1)
    morning_end = sunrise_local + timedelta(hours=3)
    noon_start = morning_end
    noon_end = noon_start + timedelta(hours=2)
    afternoon_start = noon_end
    late_afternoon_end = sunset_local - timedelta(hours=1)
    afternoon_end = late_afternoon_end + timedelta(hours=1)

    night_start = sunset_local
    early_evening_end = night_start + timedelta(hours=1)
    evening_end = early_evening_end + timedelta(hours=2)
    night_end = next_sunrise_local
    
    now = datetime.now(local_tz)
    print(f"\nCurrent Local Time: {now.strftime('%H:%M:%S %Z')}")
    print(f"Sunrise: {sunrise_local.strftime('%H:%M:%S %Z')}")
    print(f"End of Early Morning: {early_morning_end.strftime('%H:%M:%S %Z')}")
    print(f"End of Morning: {morning_end.strftime('%H:%M:%S %Z')}")
    print(f"End of Noon: {noon_end.strftime('%H:%M:%S %Z')}")
    print(f"End of Afternoon: {afternoon_end.strftime('%H:%M:%S %Z')}")
    print(f"Late Afternoon: {late_afternoon_end.strftime('%H:%M:%S %Z')}")
    print(f"Sunset (End of Evening): {sunset_local.strftime('%H:%M:%S %Z')}")
    print(f"Next Sunrise (End of Night): {next_sunrise_local.strftime('%H:%M:%S %Z')}")

    # Determine current stage
    stages = [
        ("Early Morning", sunrise_local, early_morning_end),
        ("Morning", early_morning_end, morning_end),
        ("Noon", noon_start, noon_end),
        ("Afternoon", noon_end, late_afternoon_end),
        ("Late Afternoon", late_afternoon_end, sunset_local),
        ("Night", sunset_local, next_sunrise_local),
        ("Early Evening", night_start, early_evening_end),
        ("Evening", early_evening_end, evening_end)
    ]
    
    for stage_name, start, end in stages:
        if start <= now < end:
            dist_to_min = (now - start).total_seconds() / 60
            dist_to_max = (end - now).total_seconds() / 60
            stage_hours = (end - start).total_seconds() / 3600
            print(f"\nIt's {stage_name}!")
            print(f"Stage Start: {start.strftime('%H:%M:%S %Z')}")
            print(f"Stage End: {end.strftime('%H:%M:%S %Z')}")
            print(f"Duration: {stage_hours:.2f} hours")
            print(f"Minutes from Start: {dist_to_min:.2f}")
            print(f"Minutes to End: {dist_to_max:.2f}")
            break
    
    # Set observer to current UTC time for planetary positions
    observer.date = datetime.utcnow()
    positions = {}
    print("\nPlanetary Positions and Attributes:")
    print("-" * 40)
    for name, planet in planets.items():
        planet.compute(observer)
        lon = ephem.Ecliptic(planet).lon
        positions[name] = math.degrees(lon) % 360
        sign, element, modality, polarity, q1, q2 = get_zodiac_sign(lon)
        print(f"{name}: {positions[name]:.2f}° in {sign} ({element}, {modality}, {polarity}, {q1}, {q2})")

    # Ascendant
    asc = observer.radec_of(0, 0)[0]
    asc_deg = (math.degrees(asc) - observer.sidereal_time() * 180 / math.pi + 360) % 360
    print(f"Ascendant: {asc_deg:.2f}°")

    # Moon phase
    print("\nMoon Phase:")
    print("-" * 40)
    moon_phase, phase_angle = get_moon_phase(observer)
    print(f"Moon Phase: {moon_phase} (Phase Angle: {phase_angle:.2f}°)")

    # Aspects
    print("\nAspects Between Planets:")
    print("-" * 40)
    aspects = calculate_aspects(positions)
    for p1, p2, aspect, angle in aspects:
        print(f"{p1} {aspect} {p2} ({angle}°)")

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

    # Evaluate energy states of Arabic Parts
    fortune_energy = evaluate_lot_energy(fortune_deg, positions, aspects)
    spirit_energy = evaluate_lot_energy(spirit_deg, positions, aspects)
    eros_energy = evaluate_lot_energy(eros_deg, positions, aspects)

    print(f"\nEnergy Evaluation:")
    print(fortune_energy)
    print(spirit_energy)
    print(eros_energy)

    # Plot
    local_time_str = input_time.strftime("%B %d, %Y, %H:%M %Z")
    print("\nGenerating Astrological Wheel Plot...")
    plot_astrological_wheel(positions, moon_phase, local_time_str)

if __name__ == "__main__":
    print(f"Astrological Clock for {input_time.strftime('%B %d, %Y, %H:%M %Z')} (Current Location)")
    print("=" * 50)
    astrological_clock()