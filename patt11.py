import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Polygon, Arc, Wedge
from matplotlib.colors import LinearSegmentedColormap
import ephem
from datetime import datetime, timedelta, timezone
import pytz
import geocoder
import math

# --- Sacred Geometry Setup ---
phi = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.618
outer_circle_radius = phi  # Phi golden circle
square_side = np.sqrt(phi)  # Square
smaller_circle_radius = square_side / 2  # Smaller circle
smaller_square_side = np.sqrt(phi / 2)  # Smaller square
golden_rectangle_width = square_side
golden_rectangle_height = square_side * phi
outer_golden_square_side = phi**2  # Outer golden square (φ² ≈ 2.618)
outer_unit_circle_radius = 2.8  # Outer circle to contain everything
second_square_side = outer_unit_circle_radius * np.sqrt(2) / phi  # Second square for symmetry (phi-scaled)

# --- Astronomical Setup ---
current_datetime = datetime.now().astimezone()
local_tz = current_datetime.tzinfo
formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')

# Get location
g = geocoder.ip('me')
if g.ok:
    latitude, longitude = g.latlng
else:
    latitude, longitude = 0, 0
    print("Could not determine location. Using default coordinates.")

# Set up observer
observer = ephem.Observer()
observer.lat = str(latitude)
observer.lon = str(longitude)
observer.elev = 0
observer.date = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)

# Define celestial bodies
planets = {
    "Sun": ephem.Sun(), "Moon": ephem.Moon(), "Mercury": ephem.Mercury(),
    "Venus": ephem.Venus(), "Mars": ephem.Mars(), "Jupiter": ephem.Jupiter(),
    "Saturn": ephem.Saturn(), "Uranus": ephem.Uranus(), "Neptune": ephem.Neptune(),
    "Pluto": ephem.Pluto()
}

# Zodiac signs
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

# Element colors
element_colors = {"Fire": "orange", "Earth": "green", "Air": "yellow", "Water": "blue"}
connection_colors = {"Fire": "orange", "Earth": "green", "Air": "purple", "Water": "blue"}
element_groups = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

# Planet markers for visualization
planet_markers = {
    "Sun": ('o', 'yellow', 10), "Moon": ('o', 'silver', 10), "Mercury": ('^', 'gray', 8),
    "Venus": ('s', 'pink', 8), "Mars": ('d', 'red', 8), "Jupiter": ('*', 'orange', 10),
    "Saturn": ('h', 'brown', 8), "Uranus": ('p', 'cyan', 8), "Neptune": ('D', 'blue', 8),
    "Pluto": ('v', 'purple', 8)
}

# --- Helper Functions ---
def get_zodiac_sign(longitude):
    longitude = longitude % 360
    for sign, start, element, modality, polarity, q1, q2 in zodiac_signs:
        if start <= longitude < start + 30:
            return sign, element, modality, polarity, q1, q2
    return "Pisces", "Water", "Mutable", "-", "cold", "wet"

def get_moon_phase(observer):
    moon = ephem.Moon()
    sun = ephem.Sun()
    moon.compute(observer)
    sun.compute(observer)
    elongation = float(moon.elong) * 180 / math.pi
    elongation = elongation % 360
    if elongation < 0:
        elongation += 360
    if 0 <= elongation < 5 or 355 <= elongation < 360:
        return "New Moon", elongation
    elif 5 <= elongation < 85:
        return "Waxing Crescent", elongation
    elif 85 <= elongation < 95:
        return "First Quarter", elongation
    elif 95 <= elongation < 175:
        return "Waxing Gibbous", elongation
    elif 175 <= elongation < 185:
        return "Full Moon", elongation
    elif 185 <= elongation < 265:
        return "Waning Gibbous", elongation
    elif 265 <= elongation < 275:
        return "Third Quarter", elongation
    else:
        return "Waning Crescent", elongation

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

def calculate_harmonic_ratios(positions):
    harmonic_aspects = []
    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            lon1, lon2 = positions[p1], positions[p2]
            angle = min((lon1 - lon2) % 360, (lon2 - lon1) % 360)
            if abs(angle - 144) <= 8:
                harmonic_aspects.append((p1, p2, "Perfect Fifth (3:2)", round(angle, 2)))
            if abs(angle - 120) <= 8:
                harmonic_aspects.append((p1, p2, "Trine (4:3)", round(angle, 2)))
    return harmonic_aspects

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

def calculate_lot(personal_point, significator, trigger, positions, asc_deg):
    pp = asc_deg if personal_point == "ASC" else positions.get(personal_point, 0)
    sig = positions.get(significator, 0)
    trig = positions.get(trigger, 0)
    lot_deg = (pp + sig - trig) % 360
    sign, *_ = get_zodiac_sign(lot_deg)
    return lot_deg, sign

def calculate_cycle_percentage(positions):
    percentages = {}
    for planet, lon in positions.items():
        sign_start = int(lon / 30) * 30
        degree_in_sign = lon - sign_start
        percentage = (degree_in_sign / 30) * 100
        percentages[planet] = percentage
    return percentages

def draw_elemental_connections(ax, radius):
    for element, signs in element_groups.items():
        color = connection_colors[element]
        angles = [math.radians(start + 15) for s, start, *_ in zodiac_signs if s in signs]
        for i in range(len(angles)):
            for j in range(i + 1, len(angles)):
                x1, y1 = radius * math.cos(angles[i]), radius * math.sin(angles[i])
                x2, y2 = radius * math.cos(angles[j]), radius * math.sin(angles[j])
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.5, alpha=0.7)

# --- Time Stage Calculations ---
sun = ephem.Sun()
observer.date = current_datetime.astimezone(timezone.utc)
sunrise_utc = observer.next_rising(sun).datetime()
sunset_utc = observer.next_setting(sun).datetime()
sunrise_local = pytz.utc.localize(sunrise_utc).astimezone(local_tz)
sunset_local = pytz.utc.localize(sunset_utc).astimezone(local_tz)
daylight_duration = (sunset_local - sunrise_local).total_seconds()
stage_duration = daylight_duration / 4
morning_end = sunrise_local + timedelta(seconds=stage_duration)
noon_end = sunrise_local + timedelta(seconds=2 * stage_duration)
afternoon_end = sunrise_local + timedelta(seconds=3 * stage_duration)
now = current_datetime
if sunrise_local <= now < morning_end:
    current_stage = "Morning"
    stage_color = 'gold'
elif morning_end <= now < noon_end:
    current_stage = "Noon"
    stage_color = 'orange'
elif noon_end <= now < afternoon_end:
    current_stage = "Afternoon"
    stage_color = 'coral'
elif afternoon_end <= now <= sunset_local:
    current_stage = "Evening"
    stage_color = 'violet'
else:
    current_stage = "Nighttime"
    stage_color = 'navy'

# --- Planetary Positions ---
positions = {}
observer.date = current_datetime.astimezone(timezone.utc)
for name, planet in planets.items():
    planet.compute(observer)
    lon = ephem.Ecliptic(planet).lon
    positions[name] = math.degrees(lon) % 360

# Ascendant
asc = observer.radec_of(0, 0)[0]
asc_deg = (math.degrees(asc) - observer.sidereal_time() * 180 / math.pi + 360) % 360

# Moon phase
moon_phase, phase_angle = get_moon_phase(observer)

# Syzygy and Arabic Parts
syzygy_deg = get_syzygy(observer, observer.date)
fortune_deg, fortune_sign = calculate_lot("ASC", "Moon", "Sun", positions, asc_deg)
spirit_deg, spirit_sign = calculate_lot("ASC", "Sun", "Moon", positions, asc_deg)
eros_deg, eros_sign = calculate_lot("ASC", "Venus", "Mars", positions, asc_deg)

# Cycle percentages
cycle_percentages = calculate_cycle_percentage(positions)

# Aspects and harmonic ratios
aspects = calculate_aspects(positions)
harmonic_aspects = calculate_harmonic_ratios(positions)

# --- Plotting Sigil ---
fig, ax = plt.subplots(figsize=(14, 14))
ax.set_aspect('equal')
ax.set_xlim(-4, 4)
ax.set_ylim(-4, 4)
ax.set_facecolor('#f0f0f5')
fig.patch.set_facecolor('#e6e6fa')
ax.grid(False)

# Gradient colormap
cmap = LinearSegmentedColormap.from_list("custom", ['#4682b4', '#ff4500', '#ffd700'])

# 1. Zodiac Wedges
for sign, start, element, _, _, _, _ in zodiac_signs:
    wedge = Wedge((0, 0), outer_unit_circle_radius + 0.2, start, start + 30, facecolor=element_colors[element], alpha=0.3)
    ax.add_patch(wedge)
    angle = math.radians(start + 15)
    ax.text((outer_unit_circle_radius + 0.4) * math.cos(angle), (outer_unit_circle_radius + 0.4) * math.sin(angle), sign, ha='center', va='center', fontsize=8, rotation=-(start + 15))

# 2. Outer Unit Circle
outer_circle = Circle((0, 0), outer_unit_circle_radius, fill=False, color='black', linestyle='-', linewidth=1.5, label='Celestial Boundary')
ax.add_patch(outer_circle)

# 3. Daylight Arc
daylight_arc = Arc((0, 0), outer_unit_circle_radius*2, outer_unit_circle_radius*2, theta1=90, theta2=270, color='gold', linewidth=3, alpha=0.6, label='Daylight Path')
ax.add_patch(daylight_arc)

# 4. Cardinal Points
cardinal_points = {
    'N': (0, outer_unit_circle_radius),
    'S': (0, -outer_unit_circle_radius),
    'E': (outer_unit_circle_radius, 0),
    'W': (-outer_unit_circle_radius, 0),
}
for label, (x, y) in cardinal_points.items():
    ax.plot(x, y, 'o', color='black', markersize=5)
    ax.text(x, y + 0.3 if 'S' not in label else y - 0.4, label, fontsize=10, ha='center', color='darkblue')

# 5. Sunrise and Sunset Markers
ax.plot(outer_unit_circle_radius, 0, 'o', color='yellow', markersize=10, label='Sunrise')
ax.plot(-outer_unit_circle_radius, 0, 'o', color='red', markersize=10, label='Sunset')

# 6. Planetary Positions
for planet, lon in positions.items():
    angle = math.radians(360 - lon + 90)
    x, y = outer_unit_circle_radius * math.cos(angle), outer_unit_circle_radius * math.sin(angle)
    marker, color, size = planet_markers[planet]
    ax.plot(x, y, marker, color=color, markersize=size, label=planet)
    ax.text(x * 1.05, y * 1.05, planet, fontsize=8)

# 7. Elemental Connections
draw_elemental_connections(ax, outer_unit_circle_radius - 0.1)

# 8. Outer Golden Square (Rotated 45°)
outer_square_half_diagonal = (outer_golden_square_side * np.sqrt(2)) / 2
outer_square_vertices = [
    (outer_square_half_diagonal, 0),
    (0, outer_square_half_diagonal),
    (-outer_square_half_diagonal, 0),
    (0, -outer_square_half_diagonal)
]
outer_square = Polygon(outer_square_vertices, fill=False, color=cmap(0.2), linewidth=2, label=f'Golden Square (φ² ≈ {outer_golden_square_side:.2f})')
ax.add_patch(outer_square)

# 9. Second Outer Square (Axis-Aligned)
second_square_half_side = second_square_side / 2
second_square = Rectangle((-second_square_half_side, -second_square_half_side), second_square_side, second_square_side, fill=False, color=cmap(0.3), linewidth=2, label=f'Second Square (≈ {second_square_side:.2f})')
ax.add_patch(second_square)

# 10. Phi Golden Circle
phi_circle = Circle((0, 0), outer_circle_radius, fill=False, color=cmap(0.4), linewidth=2, label=f'Phi Circle (r = φ ≈ {outer_circle_radius:.2f})')
ax.add_patch(phi_circle)

# 11. Golden Square
square_half_side = square_side / 2
square = Rectangle((-square_half_side, -square_half_side), square_side, square_side, fill=False, color=cmap(0.6), linewidth=2, label=f'Square (√φ ≈ {square_side:.2f})')
ax.add_patch(square)

# 12. Smaller Circle
smaller_circle = Circle((0, 0), smaller_circle_radius, fill=False, color=cmap(0.8), linewidth=2, label=f'Small Circle (r ≈ {smaller_circle_radius:.2f})')
ax.add_patch(smaller_circle)

# 13. Smaller Square (Rotated)
smaller_square_vertices = [
    (smaller_circle_radius, 0),
    (0, smaller_circle_radius),
    (-smaller_circle_radius, 0),
    (0, -smaller_circle_radius)
]
smaller_square = Polygon(smaller_square_vertices, fill=False, color=cmap(1.0), linewidth=2, label=f'Small Square (≈ {smaller_square_side:.2f})')
ax.add_patch(smaller_square)

# 14. Golden Rectangles
rectangles = [
    Rectangle((-square_half_side, square_half_side), golden_rectangle_width, golden_rectangle_height, fill=False, color='orange', alpha=0.5),
    Rectangle((-square_half_side, -square_half_side - golden_rectangle_height), golden_rectangle_width, golden_rectangle_height, fill=False, color='orange', alpha=0.5),
    Rectangle((square_half_side, -square_half_side), golden_rectangle_height, golden_rectangle_width, fill=False, color='orange', alpha=0.5),
    Rectangle((-square_half_side - golden_rectangle_height, -square_half_side), golden_rectangle_height, golden_rectangle_width, fill=False, color='orange', alpha=0.5)
]
for rect in rectangles:
    ax.add_patch(rect)
rectangles[0].set_label('Golden Rectangles')

# 15. Symmetric Time Stage Triangles
triangle_scale = phi / 2  # Phi-scaled for sacred geometry
angles = np.linspace(0, 2 * np.pi, 8, endpoint=False)
for i, angle in enumerate(angles):
    # Base at outer unit circle
    base_vertex_x = outer_unit_circle_radius * np.cos(angle)
    base_vertex_y = outer_unit_circle_radius * np.sin(angle)
    # One vertex at phi circle
    vertex1_x = outer_circle_radius * np.cos(angle)
    vertex1_y = outer_circle_radius * np.sin(angle)
    # Second vertex offset by phi angle
    vertex2_x = outer_circle_radius * np.cos(angle + np.pi/4)
    vertex2_y = outer_circle_radius * np.sin(angle + np.pi/4)
    color = stage_color if i == 0 and current_stage != "Nighttime" else 'magenta'
    alpha = 0.8 if i == 0 and current_stage != "Nighttime" else 0.3
    triangle = Polygon([(base_vertex_x, base_vertex_y), (vertex1_x, vertex1_y), (vertex2_x, vertex2_y)], fill=False, color=color, alpha=alpha, linewidth=1.5)
    ax.add_patch(triangle)
    if i == 0:
        triangle.set_label('Time Stage Triangles')

# 16. Current Stage Highlight
stage_arc_radius = outer_unit_circle_radius + 0.3
if current_stage != "Nighttime":
    stage_arc = Arc((0, 0), stage_arc_radius*2, stage_arc_radius*2, theta1=-22.5, theta2=22.5, color=stage_color, linewidth=5, alpha=0.7, label=f'Current: {current_stage}')
    ax.add_patch(stage_arc)

# Annotations
plt.title("Astrological Sigil: Sacred Geometry & Celestial Harmony", fontsize=14, pad=20, color='darkblue')
ax.text(-3.8, 3.8, f"Time: {formatted_datetime}\nStage: {current_stage}\nMoon: {moon_phase}", fontsize=10, va='top', ha='left', bbox=dict(facecolor='white', alpha=0.8))
ax.text(3.8, 3.8, f"Sunrise: {sunrise_local.strftime('%H:%M:%S')}\nSunset: {sunset_local.strftime('%H:%M:%S')}\nASC: {asc_deg:.2f}°", fontsize=10, va='top', ha='right', bbox=dict(facecolor='white', alpha=0.8))
ax.text(0, -3.8, f"Lat: {latitude:.2f}, Lon: {longitude:.2f}", fontsize=10, va='bottom', ha='center', color='darkblue')

# Legend
ax.legend(loc='lower right', fontsize=8, framealpha=0.9)

# Show plot
plt.show()

# --- Data Output ---
print(f"\nAstrological Data for {formatted_datetime}")
print("=" * 50)
print(f"Location: Latitude {latitude:.2f}, Longitude {longitude:.2f}")
print(f"Sunrise: {sunrise_local.strftime('%H:%M:%S %Z')}")
print(f"Sunset: {sunset_local.strftime('%H:%M:%S %Z')}")
print(f"Current Time Stage: {current_stage}")

print("\nPlanetary Positions:")
print("-" * 40)
print(f"{'Planet':<10} {'Longitude':>10} {'Sign':<10} {'Element':<8} {'Modality':<10} {'Polarity':<8} {'Q1':<6} {'Q2':<6} {'Cycle %':>8}")
for planet, lon in positions.items():
    sign, element, modality, polarity, q1, q2 = get_zodiac_sign(lon)
    print(f"{planet:<10} {lon:>10.2f}° {sign:<10} {element:<8} {modality:<10} {polarity:<8} {q1:<6} {q2:<6} {cycle_percentages[planet]:>8.2f}%")

print("\nAscendant:")
print("-" * 40)
sign, element, modality, polarity, q1, q2 = get_zodiac_sign(asc_deg)
print(f"Ascendant: {asc_deg:.2f}° in {sign} ({element}, {modality}, {polarity}, {q1}, {q2})")

print("\nMoon Phase:")
print("-" * 40)
print(f"Moon Phase: {moon_phase} (Angle: {phase_angle:.2f}°)")

print("\nArabic Parts:")
print("-" * 40)
print(f"Lot of Fortune: {fortune_deg:.2f}° in {fortune_sign}")
print(f"Lot of Spirit: {spirit_deg:.2f}° in {spirit_sign}")
print(f"Lot of Eros: {eros_deg:.2f}° in {eros_sign}")
print(f"Syzygy: {syzygy_deg:.2f}°")

print("\nAspects:")
print("-" * 40)
for p1, p2, aspect, angle in aspects:
    print(f"{p1} {aspect} {p2} ({angle}°)")

print("\nHarmonic Ratios:")
print("-" * 40)
for p1, p2, ratio, angle in harmonic_aspects:
    print(f"{p1} {ratio} {p2} ({angle}°)")

print("\nTrigonometric Analysis:")
print("-" * 40)
for planet, lon in positions.items():
    rad = math.radians(lon)
    print(f"{planet}: sin({lon:.2f}°) = {math.sin(rad):.4f}, cos({lon:.2f}°) = {math.cos(rad):.4f}")

print("\nElemental Symmetry:")
print("-" * 40)
for element, signs in element_groups.items():
    angles = [start + 15 for s, start, *_ in zodiac_signs if s in signs]
    mean = sum(angles) / len(angles)
    variance = sum((a - mean) ** 2 for a in angles) / len(angles)
    print(f"{element}: Angles {angles}, Mean = {mean:.2f}°, Variance = {variance:.2f}°")