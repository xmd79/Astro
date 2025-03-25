import ephem
import geocoder
import datetime
import math
import requests
import numpy as np
from dateutil import tz
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import pytz
from timezonefinder import TimezoneFinder

# Elemental associations and qualities for zodiac signs (from images)
zodiac_elements = {
    "Aries": ("Fire", "hot", "dry"), "Leo": ("Fire", "hot", "dry"), "Sagittarius": ("Fire", "hot", "dry"),
    "Taurus": ("Earth", "cold", "dry"), "Virgo": ("Earth", "cold", "dry"), "Capricorn": ("Earth", "cold", "dry"),
    "Gemini": ("Air", "hot", "wet"), "Libra": ("Air", "hot", "wet"), "Aquarius": ("Air", "hot", "wet"),
    "Cancer": ("Water", "cold", "wet"), "Scorpio": ("Water", "cold", "wet"), "Pisces": ("Water", "cold", "wet")
}

# Zodiac signs with additional attributes
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

# Nakshatras and dignities
nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
              "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
              "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
              "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

dignities = {
    "Sun": {"exalted": "Aries", "debilitated": "Libra"},
    "Moon": {"exalted": "Taurus", "debilitated": "Scorpio"},
    "Mercury": {"exalted": "Virgo", "debilitated": "Pisces"},
    "Venus": {"exalted": "Pisces", "debilitated": "Virgo"},
    "Mars": {"exalted": "Capricorn", "debilitated": "Cancer"},
    "Jupiter": {"exalted": "Cancer", "debilitated": "Capricorn"},
    "Saturn": {"exalted": "Libra", "debilitated": "Aries"}
}

# Element colors (consistent with images)
element_colors = {
    "Fire": "red",
    "Earth": "green",
    "Air": "yellow",
    "Water": "blue"
}

# Ayanamsa for sidereal calculations
ayanamsa = 24.0

# Function to get current geolocation and time dynamically
def get_local_datetime():
    try:
        # Try IP-API first
        response = requests.get("http://ip-api.com/json")
        data = response.json()
        if data["status"] == "success":
            lat = data["lat"]
            lon = data["lon"]
            city = data["city"]
            print(f"Estimated location via IP-API: {city} (Lat: {lat}, Lon: {lon})")
        else:
            raise Exception("IP-API geolocation failed")
    except Exception as e:
        print(f"IP-API failed: {e}. Falling back to geocoder.")
        g = geocoder.ip('me')
        if g.ok:
            lat, lon = g.lat, g.lng
            print(f"Estimated location via geocoder: Lat: {lat}, Lon: {lon}")
        else:
            print("Geocoder failed. Using default (Timișoara, Romania).")
            lat, lon = 45.7537, 21.2257

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=lat, lng=lon)
    timezone = pytz.timezone(timezone_str) if timezone_str else pytz.UTC
    naive_local_time = datetime.datetime.now()  # Get current time
    local_time = timezone.localize(naive_local_time)
    utc_time = local_time.astimezone(pytz.UTC)
    return local_time, utc_time, lat, lon

# Function to set up observer
def setup_observer(lat, lon, dt):
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = dt
    observer.elevation = 0
    observer.pressure = 0
    return observer

# Function to convert radians to degrees
def rad_to_deg(radians):
    return math.degrees(radians)

# Function to get zodiac sign from longitude
def get_zodiac_sign(longitude):
    deg = rad_to_deg(longitude) % 360
    if 0 <= deg < 30: return "Aries"
    elif 30 <= deg < 60: return "Taurus"
    elif 60 <= deg < 90: return "Gemini"
    elif 90 <= deg < 120: return "Cancer"
    elif 120 <= deg < 150: return "Leo"
    elif 150 <= deg < 180: return "Virgo"
    elif 180 <= deg < 210: return "Libra"
    elif 210 <= deg < 240: return "Scorpio"
    elif 240 <= deg < 270: return "Sagittarius"
    elif 270 <= deg < 300: return "Capricorn"
    elif 300 <= deg < 330: return "Aquarius"
    elif 330 <= deg < 360: return "Pisces"

# Function to calculate planetary positions
def get_planetary_positions(observer):
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
        "Pluto": ephem.Pluto(),
        "Black Moon Lilith": None,
        "Dark Moon Lilith": None,
        "Asteroid Lilith": None,
        "Rahu": None,
        "Ketu": None
    }

    observer.compute_pressure()
    asc = observer.radec_of(0, 0)[0]
    mc = observer.radec_of(math.pi/2, 0)[0]
    asc_long = ephem.Ecliptic(asc, 0, epoch=observer.date).lon
    mc_long = ephem.Ecliptic(mc, 0, epoch=observer.date).lon

    # Sidereal Ascendant calculation
    lst = observer.sidereal_time()
    asc_trop = (math.degrees(lst) + observer.lon * 15 / math.pi) % 360
    asc_sidereal = (asc_trop - ayanamsa) % 360
    asc_sign_idx = int(asc_sidereal // 30)
    asc_sign, _, asc_element, asc_modality, asc_polarity = zodiac_signs[asc_sign_idx]
    asc_house_start = asc_sign_idx * 30

    positions = {}
    for name, body in planets.items():
        if name == "Black Moon Lilith":
            days_since_ref = observer.date - ephem.Date("2000/01/01")
            mean_apogee = (83 + days_since_ref * 0.111404) % 360
            trop_long = (mean_apogee + 180) % 360
        elif name == "Dark Moon Lilith":
            days_since_ref = observer.date - ephem.Date("1898/01/01")
            trop_long = (days_since_ref * 3.025) % 360
        elif name == "Asteroid Lilith":
            days_since_ref = observer.date - ephem.Date("1927/02/11")
            trop_long = (days_since_ref * 0.23) % 360
        elif name == "Rahu":
            days_since_ref = observer.date - ephem.Date("2000/01/01")
            trop_long = (15 - days_since_ref * 0.053) % 360
        elif name == "Ketu":
            trop_long = (trop_long + 180) % 360
        else:
            body.compute(observer)
            trop_long = math.degrees(body.hlon)

        sidereal_long = (trop_long - ayanamsa) % 360
        house_num = (int((sidereal_long - asc_house_start) % 360 // 30) + 1) % 12 or 12
        sign_idx = int(sidereal_long // 30)
        sign, _, element, modality, polarity = zodiac_signs[sign_idx]
        nakshatra_idx = int(sidereal_long / 13.3333) % 27
        nakshatra = nakshatras[nakshatra_idx]

        data = {
            "sidereal_long": sidereal_long,
            "tropical_long": trop_long,
            "house": house_num,
            "sign": sign,
            "element": element,
            "modality": modality,
            "polarity": polarity,
            "nakshatra": nakshatra,
            "color": element_colors[element]
        }
        if name not in ["Black Moon Lilith", "Dark Moon Lilith", "Asteroid Lilith", "Rahu", "Ketu"]:
            data.update({
                "az": math.degrees(body.az),
                "alt": math.degrees(body.alt),
                "ra": math.degrees(body.ra),
                "dec": math.degrees(body.dec),
                "lat": math.degrees(body.hlat),
                "distance": body.earth_distance
            })
            if name == "Sun":
                data["magnitude"] = body.mag
            elif name == "Moon":
                data["phase"] = body.phase
                data["magnitude"] = body.mag
            if name in dignities:
                dignity = "Neutral"
                if sign == dignities[name]["exalted"]:
                    dignity = "Exalted"
                elif sign == dignities[name]["debilitated"]:
                    dignity = "Debilitated"
                data["dignity"] = dignity
        positions[name] = data

    positions["Ascendant"] = {
        "sidereal_long": asc_sidereal,
        "tropical_long": rad_to_deg(asc_long),
        "house": 1,
        "sign": asc_sign,
        "element": asc_element,
        "modality": asc_modality,
        "polarity": asc_polarity,
        "nakshatra": nakshatras[int(asc_sidereal / 13.3333) % 27],
        "color": element_colors[asc_element]
    }
    positions["Midheaven"] = {
        "sidereal_long": (rad_to_deg(mc_long) - ayanamsa) % 360,
        "tropical_long": rad_to_deg(mc_long),
        "house": 10,
        "sign": get_zodiac_sign(mc_long),
        "element": zodiac_elements[get_zodiac_sign(mc_long)][0],
        "modality": [s[3] for s in zodiac_signs if s[0] == get_zodiac_sign(mc_long)][0],
        "polarity": [s[4] for s in zodiac_signs if s[0] == get_zodiac_sign(mc_long)][0],
        "nakshatra": nakshatras[int(((rad_to_deg(mc_long) - ayanamsa) % 360) / 13.3333) % 27],
        "color": element_colors[zodiac_elements[get_zodiac_sign(mc_long)][0]]
    }
    return positions, planets

# Function to calculate aspects
def calculate_aspects(positions):
    aspects = {
        0: ("Conjunction", 10),
        45: ("Semi-square", 2),
        60: ("Sextile", 6),
        90: ("Square", 8),
        120: ("Trine", 8),
        135: ("Sesquiquadrate", 2),
        180: ("Opposition", 10),
        72: ("Quintile", 2)
    }
    aspect_table = []
    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            long1, long2 = positions[p1]["sidereal_long"], positions[p2]["sidereal_long"]
            diff = min((long1 - long2) % 360, (long2 - long1) % 360)
            for angle, (aspect_name, orb) in aspects.items():
                if abs(diff - angle) <= orb:
                    aspect_table.append((p1, p2, aspect_name, diff))
    return aspect_table

# Function to build geometric patterns
def build_geometric_patterns(positions, aspects):
    patterns = {
        "Dualities": [],
        "Triads": [],
        "Squares": [],
        "Pentagrams": [],
        "Hexagons": [],
        "Symmetries": [],
        "Polarities": [],
        "Interconnections": []
    }
    involved_bodies = set()

    opposites = {
        "Aries": "Libra", "Taurus": "Scorpio", "Gemini": "Sagittarius",
        "Cancer": "Capricorn", "Leo": "Aquarius", "Virgo": "Pisces",
        "Libra": "Aries", "Scorpio": "Taurus", "Sagittarius": "Gemini",
        "Capricorn": "Cancer", "Aquarius": "Leo", "Pisces": "Virgo"
    }

    for a1, a2, aspect, diff in aspects:
        involved_bodies.add(a1)
        involved_bodies.add(a2)
        if aspect == "Opposition":
            patterns["Dualities"].append((a1, a2))
        elif aspect == "Trine":
            for b1, b2, asp, _ in aspects:
                if asp == "Trine" and {a1, a2} & {b1, b2} and len({a1, a2, b1, b2}) == 3:
                    patterns["Triads"].append((a1, a2, b1))
        elif aspect == "Square":
            for b1, b2, asp, _ in aspects:
                if asp == "Square" and {a1, a2} & {b1, b2} and len({a1, a2, b1, b2}) == 4:
                    patterns["Squares"].append((a1, a2, b1, b2))
        elif aspect == "Quintile":
            patterns["Pentagrams"].append((a1, a2))
        elif aspect == "Sextile":
            patterns["Hexagons"].append((a1, a2))

    pos_dict = dict(positions)
    for name1, lon1 in [(n, p["sidereal_long"]) for n, p in positions.items()]:
        sign1 = pos_dict[name1]["sign"]
        for name2, lon2 in [(n, p["sidereal_long"]) for n, p in positions.items()]:
            if name1 >= name2:
                continue
            sign2 = pos_dict[name2]["sign"]
            diff = abs((lon1 - lon2 + 180) % 360 - 180)
            if 175 <= diff <= 185:
                patterns["Symmetries"].append((name1, name2))
            if opposites[sign1] == sign2:
                patterns["Polarities"].append((name1, name2))
            aspect_count = sum(1 for a, b, _, _ in aspects if {a, b} == {name1, name2})
            if aspect_count > 1:
                patterns["Interconnections"].append((name1, name2))

    return patterns

# Function to calculate planetary cycles and velocity
def calculate_planetary_cycles(observer, planets, positions):
    cycles = {}
    original_date = observer.date
    delta_days = 1.0
    observer.date = original_date - delta_days

    prev_positions = {}
    for planet, body in planets.items():
        if planet == "Black Moon Lilith":
            days_since_ref = observer.date - ephem.Date("2000/01/01")
            mean_apogee = (83 + days_since_ref * 0.111404) % 360
            prev_positions[planet] = (mean_apogee + 180) % 360
        elif planet == "Dark Moon Lilith":
            days_since_ref = observer.date - ephem.Date("1898/01/01")
            prev_positions[planet] = (days_since_ref * 3.025) % 360
        elif planet == "Asteroid Lilith":
            days_since_ref = observer.date - ephem.Date("1927/02/11")
            prev_positions[planet] = (days_since_ref * 0.23) % 360
        elif planet == "Rahu":
            days_since_ref = observer.date - ephem.Date("2000/01/01")
            prev_positions[planet] = (15 - days_since_ref * 0.053) % 360
        elif planet == "Ketu":
            prev_positions[planet] = (prev_positions["Rahu"] + 180) % 360
        else:
            body.compute(observer)
            prev_positions[planet] = math.degrees(body.hlon)

    observer.date = original_date
    max_velocity = 0
    for planet, body in planets.items():
        if planet == "Black Moon Lilith":
            days_since_ref = observer.date - ephem.Date("2000/01/01")
            mean_apogee = (83 + days_since_ref * 0.111404) % 360
            curr_long = (mean_apogee + 180) % 360
        elif planet == "Dark Moon Lilith":
            days_since_ref = observer.date - ephem.Date("1898/01/01")
            curr_long = (days_since_ref * 3.025) % 360
        elif planet == "Asteroid Lilith":
            days_since_ref = observer.date - ephem.Date("1927/02/11")
            curr_long = (days_since_ref * 0.23) % 360
        elif planet == "Rahu":
            days_since_ref = observer.date - ephem.Date("2000/01/01")
            curr_long = (15 - days_since_ref * 0.053) % 360
        elif planet == "Ketu":
            curr_long = (curr_long + 180) % 360
        else:
            body.compute(observer)
            curr_long = math.degrees(body.hlon)

        prev_long = prev_positions[planet]
        delta_long = curr_long - prev_long
        if delta_long > 180:
            delta_long -= 360
        elif delta_long < -180:
            delta_long += 360

        velocity = delta_long / delta_days
        cycle_length = 360 / abs(velocity) if abs(velocity) > 0.0001 else float('inf')
        retrograde = " (Retrograde)" if velocity < 0 else ""
        cycles[planet] = {
            "velocity": velocity,
            "cycle_length": cycle_length,
            "retrograde": retrograde
        }
        max_velocity = max(max_velocity, abs(velocity))

    sun_long = positions["Sun"]["sidereal_long"]
    for planet in cycles:
        vel = cycles[planet]["velocity"]
        long = positions[planet]["sidereal_long"]
        freq = (vel / max_velocity) * math.cos(math.radians(long - sun_long))
        cycles[planet]["frequency"] = max(min(freq, 1.0), -1.0)

    observer.date = original_date
    return cycles

# Function for sacred geometry
def sacred_geometry(positions):
    geo_forms = {
        "Tetrahedron": [60],
        "Cube": [90],
        "Octahedron": [120],
        "Dodecahedron": [108],
        "Icosahedron": [180]
    }
    active_forms = []
    for planet, data in positions.items():
        for form, angles in geo_forms.items():
            for angle in angles:
                if any(abs((data["sidereal_long"] - positions[p2]["sidereal_long"]) % 360 - angle) < 1 for p2 in positions if p2 != planet):
                    active_forms.append(f"{form} active with {planet}")
    return list(set(active_forms))

# Function for spectral analysis
def spectral_analysis(positions, dt, cycles, aspects):
    times = np.linspace(0, 24, 25)
    energies = {}
    for planet, data in positions.items():
        if planet in ["Ascendant", "Midheaven", "Black Moon Lilith", "Dark Moon Lilith", "Asteroid Lilith", "Rahu", "Ketu"]:
            continue
        freq = 1 / (360 / abs(data["sidereal_long"])) if data["sidereal_long"] != 0 else 0.01
        amplitude = data["distance"]
        phase = data["sidereal_long"] / 360 * 2 * math.pi
        wave = [amplitude * math.sin(2 * math.pi * freq * t + phase) for t in times]
        energies[planet] = wave

    total_energy = np.sum(list(energies.values()), axis=0)
    fft = np.fft.fft(total_energy)
    freqs = np.fft.fftfreq(len(times), d=24/len(times))
    predominant_freqs = sorted(zip(abs(fft), freqs), reverse=True)[:5]

    planet_contributions = {}
    for planet, wave in energies.items():
        planet_fft = np.fft.fft(wave)
        planet_amp = sum(abs(planet_fft[i]) for i, _ in enumerate(predominant_freqs))
        planet_contributions[planet] = planet_amp

    top_planets = sorted(planet_contributions.items(), key=lambda x: x[1], reverse=True)[:3]

    mean_energy = np.mean(total_energy)
    polarity = "Positive" if mean_energy > 0 else "Negative"
    raw_trend = total_energy[-1] - total_energy[0]

    if polarity == "Negative":
        trend = "Up" if raw_trend > 0 else "Down"
        trend_desc = "Dip Reversal (down-to-up)" if trend == "Up" else "Continuing Down"
        dip_planet = min(cycles.items(), key=lambda x: x[1]["frequency"])[0]
        peak_planet = max(cycles.items(), key=lambda x: x[1]["frequency"])[0]
    else:
        trend = "Down" if raw_trend < 0 else "Up"
        trend_desc = "Peak Reversal (up-to-down)" if trend == "Down" else "Continuing Up"
        dip_planet = min(cycles.items(), key=lambda x: x[1]["frequency"])[0]
        peak_planet = max(cycles.items(), key=lambda x: x[1]["frequency"])[0]

    total_freq = sum(cycles[p]["frequency"] for p in cycles)
    avg_freq = total_freq / len(cycles)
    aspect_weight = len(aspects) * 0.05
    daily_pulse = max(min(avg_freq + aspect_weight if polarity == "Positive" else avg_freq - aspect_weight, 1.0), -1.0)
    pulse_desc = "High" if daily_pulse > 0.5 else "Low" if daily_pulse < -0.5 else "Moderate"

    return {
        "spectrum": total_energy.tolist(),
        "predominant_frequencies": [(abs(f), freq) for f, freq in predominant_freqs],
        "top_planets": top_planets,
        "polarity": polarity,
        "trend": trend,
        "trend_description": trend_desc,
        "dip_planet": dip_planet,
        "peak_planet": peak_planet,
        "daily_pulse": daily_pulse,
        "pulse_description": pulse_desc,
        "energy_forecast": f"Energy is {polarity}, {trend_desc} on {dt}, from {dip_planet} (dip) to {peak_planet} (peak), influenced by {', '.join(p for p, _ in top_planets)}. Daily Pulse: {pulse_desc} ({daily_pulse:.2f})"
    }

# Function for Fear and Greed Index
def calculate_fear_greed_index(positions, cycles, aspects):
    lilith_aspects = [(p1, p2, aspect, diff) for p1, p2, aspect, diff in aspects if p1 == "Black Moon Lilith" or p2 == "Black Moon Lilith"]
    lilith_velocity = cycles["Black Moon Lilith"]["velocity"]

    aspect_weights = {
        "Conjunction": -0.3,
        "Opposition": -0.2,
        "Square": -0.15,
        "Semi-square": -0.1,
        "Sesquiquadrate": -0.1,
        "Quincunx": -0.05,
        "Sextile": 0.15,
        "Trine": 0.2
    }

    fear_greed_index = 0.0
    for p1, p2, aspect, diff in lilith_aspects:
        weight = aspect_weights.get(aspect, 0.0)
        fear_greed_index += weight

    velocity_factor = lilith_velocity / 0.111404
    fear_greed_index += velocity_factor * 0.3
    fear_greed_index = max(min(fear_greed_index, 1.0), -1.0)
    description = "Extreme Fear" if fear_greed_index < -0.5 else "Fear" if fear_greed_index < 0 else "Neutral" if fear_greed_index == 0 else "Greed" if fear_greed_index <= 0.5 else "Extreme Greed"

    return fear_greed_index, description, lilith_aspects

# Function to plot the astrological wheel
def plot_astrological_wheel(positions, zodiac_signs, local_time):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    for sign, start, element, modality, polarity in zodiac_signs:
        color = element_colors[element]
        wedge = Wedge((0, 0), 1, start, start + 30, facecolor=color, alpha=0.5)
        ax.add_patch(wedge)

        angle = math.radians(start + 15)
        x = 1.1 * math.cos(angle)
        y = 1.1 * math.sin(angle)
        ax.text(x, y, sign, ha='center', va='center', fontsize=10, rotation=-(start + 15))

        x_inner = 0.7 * math.cos(angle)
        y_inner = 0.7 * math.sin(angle)
        ax.text(x_inner, y_inner, f"{element}\n{modality}\n{polarity}", ha='center', va='center', fontsize=8)

    for planet, data in positions.items():
        lon = data["sidereal_long"]
        angle = math.radians(360 - lon + 90)
        x = 0.9 * math.cos(angle)
        y = 0.9 * math.sin(angle)
        ax.plot(x, y, 'o', color=data["color"], label=planet)
        ax.text(x * 1.05, y * 1.05, planet, fontsize=8)

    ax.text(0, 0, "THE 12 SIGNS", ha='center', va='center', fontsize=14, color='purple')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"Sidereal Astrological Wheel for {local_time}")
    plt.show()

# Function to generate cosmic reflection
def generate_cosmic_reflection(local_time, asc_sign, mc_sign, aspects, patterns, positions, cycles, analysis, fear_greed_index, description, lilith_aspects, sacred_geo):
    asc_element = zodiac_elements[asc_sign][0]
    mc_element = zodiac_elements[mc_sign][0]
    asc_qualities = f"{zodiac_elements[asc_sign][1]} and {zodiac_elements[asc_sign][2]}"
    mc_qualities = f"{zodiac_elements[mc_sign][1]} and {zodiac_elements[mc_sign][2]}"

    reflection = f"On {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}, with Ascendant in {asc_sign} ({asc_element}, {asc_qualities}) "
    reflection += f"and Midheaven in {mc_sign} ({mc_element}, {mc_qualities}), the heavens weave a cosmic tapestry:\n"

    reflection += f"The sky’s {len(aspects)} aspects form intricate patterns, "
    active_patterns = [p for p, v in patterns.items() if v]
    if active_patterns:
        reflection += f"including {', '.join(active_patterns)}—their {len(active_patterns)} forms "
        reflection += f"reflect the {len(positions)} celestial bodies’ symmetries and polarities. "
        if patterns["Triads"]:
            reflection += f"Triads like {patterns['Triads'][0]} form harmonious triangles (symmetry ratio 1:1:1), "
        if patterns["Pentagrams"]:
            reflection += f"while Pentagrams such as {patterns['Pentagrams'][0]} spark creative insights (ratio 1:1). "
        if patterns["Hexagons"]:
            reflection += f"Hexagons like {patterns['Hexagons'][0]} foster cooperative energies (ratio 1:1 per pair). "
        if patterns["Polarities"]:
            reflection += f"Polarities like {patterns['Polarities'][0]} highlight dynamic tensions (ratio 1:1). "

    reflection += f"\nSpectral Analysis: {analysis['energy_forecast']}\n"
    reflection += f"Black Moon Lilith Fear and Greed Index: {fear_greed_index:.2f} ({description})\n"
    if lilith_aspects:
        reflection += "Lilith Aspects Contributing to Index:\n"
        for p1, p2, aspect, diff in lilith_aspects:
            reflection += f"  {p1} {aspect} {p2} ({diff:.2f}°)\n"

    if sacred_geo:
        reflection += "Sacred Geometry Formations:\n"
        for form in sacred_geo:
            reflection += f"  {form}\n"

    reflection += "This celestial dance unveils a timeless harmony on this day."
    return reflection

# Main function to calculate planetary positions and generate output
def calculate_planetary_positions():
    try:
        local_time, utc_time, lat, lon = get_local_datetime()
        observer = setup_observer(lat, lon, utc_time)

        positions, planets = get_planetary_positions(observer)

        # Determine Moon phase
        moon_phase = positions["Moon"]["phase"]
        if 0 <= moon_phase < 1:
            phase_name = "New Moon"
        elif 1 <= moon_phase < 49:
            phase_name = "Waxing Crescent"
        elif 49 <= moon_phase < 51:
            phase_name = "First Quarter"
        elif 51 <= moon_phase < 99:
            phase_name = "Waxing Gibbous"
        elif 99 <= moon_phase <= 100:
            phase_name = "Full Moon"
        elif 100 < moon_phase <= 149:
            phase_name = "Waning Gibbous"
        elif 149 < moon_phase <= 151:
            phase_name = "Last Quarter"
        else:
            phase_name = "Waning Crescent"

        print(f"Planetary Positions for {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"UTC Time: {utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Location: Latitude {lat:.4f}°, Longitude {lon:.4f}°")
        print("--------------------------------------------------")
        print(f"Moon Phase: {phase_name}, ~{moon_phase:.1f}% illuminated")
        print(f"Moon Zodiac: {positions['Moon']['sign']} (Sidereal: ~{positions['Moon']['sidereal_long']:.1f}°, House {positions['Moon']['house']})")

        print("\nPlanetary Positions (Vedic Sidereal):")
        for planet, data in positions.items():
            if planet == "Ascendant" or planet == "Midheaven":
                print(f"{planet}:")
                print(f"  Sidereal Longitude: {data['sidereal_long']:.2f}°")
                print(f"  Tropical Longitude: {data['tropical_long']:.2f}°")
                print(f"  Zodiac Sign: {data['sign']} ({data['element']}, {data['modality']}, {data['polarity']}, {data['nakshatra']})")
                print(f"  House: {data['house']}")
            elif planet in ["Black Moon Lilith", "Dark Moon Lilith", "Asteroid Lilith", "Rahu", "Ketu"]:
                print(f"{planet}:")
                print(f"  Sidereal Longitude: {data['sidereal_long']:.2f}°")
                print(f"  Tropical Longitude: {data['tropical_long']:.2f}°")
                print(f"  Zodiac Sign: {data['sign']} ({data['element']}, {data['modality']}, {data['polarity']}, {data['nakshatra']})")
                print(f"  House: {data['house']}")
            else:
                extras = f", Phase={data['phase']:.1f}%" if planet == "Moon" else ""
                extras += f", Magnitude={data.get('magnitude', 'N/A'):.2f}" if planet in ["Sun", "Moon"] else ""
                dignity = f", Dignity={data.get('dignity', 'N/A')}" if 'dignity' in data else ""
                element, quality1, quality2 = zodiac_elements[data['sign']]
                print(f"{planet}:")
                print(f"  Sidereal Longitude: {data['sidereal_long']:.2f}°")
                print(f"  Tropical Longitude: {data['tropical_long']:.2f}°")
                print(f"  Zodiac Sign: {data['sign']} ({element}, {quality1} and {quality2}, {data['modality']}, {data['polarity']}, {data['nakshatra']})")
                print(f"  House: {data['house']}")
                print(f"  Distance: {data['distance']:.2f} AU{extras}{dignity}")
            print()

        aspects = calculate_aspects(positions)
        print("Aspects:")
        print("--------")
        for p1, p2, aspect, diff in aspects:
            print(f"{p1} - {p2}: {aspect} ({diff:.2f}°)")
        print()

        patterns = build_geometric_patterns(positions, aspects)
        print("Geometric Patterns:")
        print("------------------")
        for pattern, instances in patterns.items():
            if instances:
                print(f"{pattern}:")
                for inst in instances:
                    print(f"  {inst}")
                print()

        cycles = calculate_planetary_cycles(observer, planets, positions)
        print("Planetary Cycles (Sorted by Frequency, -1 to +1):")
        sorted_cycles = sorted(cycles.items(), key=lambda x: x[1]["frequency"])
        for planet, data in sorted_cycles:
            print(f"{planet}: Velocity={data['velocity']:.2f}°/day{data['retrograde']}, Cycle={data['cycle_length']:.2f} days, Frequency={data['frequency']:.2f}")
        print()

        sacred_geo = sacred_geometry(positions)
        print("Sacred Geometry Formations (Sidereal):")
        for form in sacred_geo:
            print(form)
        print()

        analysis = spectral_analysis(positions, local_time, cycles, aspects)
        print("Spectral Analysis:")
        print(f"Spectrum (25 points): {analysis['spectrum']}")
        print("Top 5 Predominant Frequencies (Amplitude, Freq):")
        for amp, freq in analysis["predominant_frequencies"]:
            print(f"Amplitude={amp:.2f}, Frequency={freq:.4f} cycles/hour")
        print(f"Top Influential Planets: {', '.join(f'{p} (Amp={a:.2f})' for p, a in analysis['top_planets'])}")
        print(f"Polarity: {analysis['polarity']}")
        print(f"Trend: {analysis['trend']} ({analysis['trend_description']})")
        print(f"Energy Forecast: {analysis['energy_forecast']}")
        print()

        fear_greed_index, description, lilith_aspects = calculate_fear_greed_index(positions, cycles, aspects)
        print("Black Moon Lilith Fear and Greed Index:")
        print(f"Index: {fear_greed_index:.2f} ({description})")
        print("Lilith Aspects Contributing to Index:")
        for p1, p2, aspect, diff in lilith_aspects:
            print(f"{p1} - {p2}: {aspect} ({diff:.2f}°)")
        print()

        asc_sign = positions["Ascendant"]["sign"]
        mc_sign = positions["Midheaven"]["sign"]
        reflection = generate_cosmic_reflection(local_time, asc_sign, mc_sign, aspects, patterns, positions, cycles, analysis, fear_greed_index, description, lilith_aspects, sacred_geo)
        print("Cosmic Reflection:")
        print("-----------------")
        print(reflection)

        print("Generating Sidereal Astrological Wheel Plot...")
        plot_astrological_wheel(positions, zodiac_signs, local_time)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Using fallback: UTC time and default location (0,0).")

# Run the script
if __name__ == "__main__":
    calculate_planetary_positions()