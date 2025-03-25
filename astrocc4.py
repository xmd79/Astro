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

# Zodiac sign data with elemental associations and qualities
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

zodiac_elements = {sign[0]: (sign[2], "hot" if sign[2] in ["Fire", "Air"] else "cold", 
                            "dry" if sign[2] in ["Fire", "Earth"] else "wet") for sign in zodiac_signs}

# Nakshatras and planetary dignities
nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", 
              "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", 
              "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
              "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

dignities = {
    "Sun": {"exalted": "Aries", "debilitated": "Libra", "ruler": ["Leo"], "detriment": ["Aquarius"], "fall": "Libra"},
    "Moon": {"exalted": "Taurus", "debilitated": "Scorpio", "ruler": ["Cancer"], "detriment": ["Capricorn"], "fall": "Scorpio"},
    "Mercury": {"exalted": "Virgo", "debilitated": "Pisces", "ruler": ["Gemini", "Virgo"], "detriment": ["Sagittarius", "Pisces"], "fall": "Pisces"},
    "Venus": {"exalted": "Pisces", "debilitated": "Virgo", "ruler": ["Taurus", "Libra"], "detriment": ["Scorpio", "Aries"], "fall": "Virgo"},
    "Mars": {"exalted": "Capricorn", "debilitated": "Cancer", "ruler": ["Aries", "Scorpio"], "detriment": ["Libra", "Taurus"], "fall": "Cancer"},
    "Jupiter": {"exalted": "Cancer", "debilitated": "Capricorn", "ruler": ["Sagittarius", "Pisces"], "detriment": ["Gemini", "Virgo"], "fall": "Capricorn"},
    "Saturn": {"exalted": "Libra", "debilitated": "Aries", "ruler": ["Capricorn", "Aquarius"], "detriment": ["Cancer", "Leo"], "fall": "Aries"}
}

# Element colors
element_colors = {"Fire": "red", "Earth": "green", "Air": "yellow", "Water": "blue"}

# Ayanamsa for sidereal calculations (Lahiri approximation)
ayanamsa = 24.0

# Get current geolocation and time
def get_local_datetime():
    try:
        response = requests.get("http://ip-api.com/json", timeout=5)
        data = response.json()
        if data["status"] == "success":
            lat, lon = data["lat"], data["lon"]
            city = data["city"]
            print(f"Estimated location via IP-API: {city} (Lat: {lat}, Lon: {lon})")
        else:
            raise Exception("IP-API failed")
    except Exception:
        print("IP-API failed. Falling back to geocoder.")
        g = geocoder.ip('me')
        if g.ok:
            lat, lon = g.lat, g.lng
            print(f"Estimated location via geocoder: Lat: {lat}, Lon: {lon}")
        else:
            print("Geocoder failed. Using default (Timișoara, Romania).")
            lat, lon = 45.7537, 21.2257

    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=lat, lng=lon) or "UTC"
    timezone = pytz.timezone(timezone_str)
    local_time = timezone.localize(datetime.datetime.now())
    utc_time = local_time.astimezone(pytz.UTC)
    return local_time, utc_time, lat, lon

# Set up observer
def setup_observer(lat, lon, dt):
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = dt
    observer.elevation = 0
    observer.pressure = 0
    return observer

# Convert radians to degrees
def rad_to_deg(radians):
    return math.degrees(radians) % 360

# Get zodiac sign from longitude
def get_zodiac_sign(longitude):
    deg = longitude % 360
    for sign, start, _, _, _ in zodiac_signs:
        if start <= deg < start + 30:
            return sign
    return "Pisces"  # Fallback for 330-360

# Calculate planetary positions
def get_planetary_positions(observer):
    planets = {
        "Sun": ephem.Sun(), "Moon": ephem.Moon(), "Mercury": ephem.Mercury(), "Venus": ephem.Venus(),
        "Mars": ephem.Mars(), "Jupiter": ephem.Jupiter(), "Saturn": ephem.Saturn(), "Uranus": ephem.Uranus(),
        "Neptune": ephem.Neptune(), "Pluto": ephem.Pluto(),
        "Black Moon Lilith": None, "Dark Moon Lilith": None, "Asteroid Lilith": None, "Rahu": None, "Ketu": None
    }

    asc = observer.radec_of(0, 0)[0]
    mc = observer.radec_of(math.pi/2, 0)[0]
    asc_long = ephem.Ecliptic(asc, 0, epoch=observer.date).lon
    mc_long = ephem.Ecliptic(mc, 0, epoch=observer.date).lon

    lst = observer.sidereal_time()
    asc_trop = (rad_to_deg(lst) + rad_to_deg(observer.lon) * 15 / math.pi) % 360
    asc_sidereal = (asc_trop - ayanamsa) % 360
    asc_sign_idx = int(asc_sidereal // 30)
    asc_sign, _, asc_element, asc_modality, asc_polarity = zodiac_signs[asc_sign_idx]
    asc_house_start = asc_sign_idx * 30

    positions = {}
    for name, body in planets.items():
        if name == "Black Moon Lilith":
            days_since_ref = observer.date - ephem.Date("2000/01/01")
            trop_long = (83 + days_since_ref * 0.111404 + 180) % 360
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
            trop_long = (positions["Rahu"]["tropical_long"] + 180) % 360 if "Rahu" in positions else 0
        else:
            body.compute(observer)
            trop_long = rad_to_deg(body.hlon)

        sidereal_long = (trop_long - ayanamsa) % 360
        house_num = (int((sidereal_long - asc_house_start) % 360 // 30) + 1) % 12 or 12
        sign = get_zodiac_sign(sidereal_long)
        element, quality1, quality2 = zodiac_elements[sign]
        modality = next(s[3] for s in zodiac_signs if s[0] == sign)
        polarity = next(s[4] for s in zodiac_signs if s[0] == sign)
        nakshatra = nakshatras[int(sidereal_long / 13.3333) % 27]

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
                "az": rad_to_deg(body.az),
                "alt": rad_to_deg(body.alt),
                "ra": rad_to_deg(body.ra),
                "dec": rad_to_deg(body.dec),
                "lat": rad_to_deg(body.hlat),
                "distance": body.earth_distance,
                "magnitude": body.mag if name in ["Sun", "Moon"] else None,
                "phase": body.phase if name == "Moon" else None
            })
            if name in dignities:
                dignity = "Neutral"
                if sign == dignities[name]["exalted"]:
                    dignity = "Exalted"
                elif sign == dignities[name]["debilitated"]:
                    dignity = "Debilitated"
                elif sign in dignities[name]["ruler"]:
                    dignity = "Ruler"
                elif sign in dignities[name]["detriment"]:
                    dignity = "Detriment"
                elif sign == dignities[name]["fall"]:
                    dignity = "Fall"
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
        "sign": get_zodiac_sign(rad_to_deg(mc_long)),
        "element": zodiac_elements[get_zodiac_sign(rad_to_deg(mc_long))][0],
        "modality": next(s[3] for s in zodiac_signs if s[0] == get_zodiac_sign(rad_to_deg(mc_long))),
        "polarity": next(s[4] for s in zodiac_signs if s[0] == get_zodiac_sign(rad_to_deg(mc_long))),
        "nakshatra": nakshatras[int(((rad_to_deg(mc_long) - ayanamsa) % 360) / 13.3333) % 27],
        "color": element_colors[zodiac_elements[get_zodiac_sign(rad_to_deg(mc_long))][0]]
    }
    return positions, planets

# Calculate aspects with strength
def calculate_aspects(positions):
    aspects = {
        0: ("Conjunction", 10, 0.0),
        45: ("Semi-square", 2, -0.1),
        60: ("Sextile", 6, 0.15),
        90: ("Square", 8, -0.15),
        120: ("Trine", 8, 0.2),
        135: ("Sesquiquadrate", 2, -0.1),
        180: ("Opposition", 10, -0.2),
        72: ("Quintile", 2, 0.1)
    }
    aspect_table = []
    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            long1, long2 = positions[p1]["sidereal_long"], positions[p2]["sidereal_long"]
            diff = min((long1 - long2) % 360, (long2 - long1) % 360)
            for angle, (aspect_name, orb, base_weight) in aspects.items():
                if abs(diff - angle) <= orb:
                    orb_factor = 1 - (abs(diff - angle) / orb)
                    strength = base_weight * orb_factor
                    aspect_table.append((p1, p2, aspect_name, diff, strength))
    return aspect_table

# Build geometric patterns
def build_geometric_patterns(positions, aspects):
    patterns = {
        "Dualities": [], "Triads": [], "Squares": [], "Pentagrams": [], "Hexagons": [], "Symmetries": [], "Polarities": []
    }
    opposites = {s[0]: zodiac_signs[(i + 6) % 12][0] for i, s in enumerate(zodiac_signs)}

    for a1, a2, aspect, diff, _ in aspects:
        if aspect == "Opposition":
            patterns["Dualities"].append((a1, a2))
        elif aspect == "Trine":
            for b1, b2, asp, _, _ in aspects:
                if asp == "Trine" and {a1, a2} & {b1, b2} and len({a1, a2, b1, b2}) == 3:
                    patterns["Triads"].append((a1, a2, b1))
        elif aspect == "Square":
            for b1, b2, asp, _, _ in aspects:
                if asp == "Square" and {a1, a2} & {b1, b2} and len({a1, a2, b1, b2}) == 4:
                    patterns["Squares"].append((a1, a2, b1, b2))
        elif aspect == "Quintile":
            patterns["Pentagrams"].append((a1, a2))
        elif aspect == "Sextile":
            patterns["Hexagons"].append((a1, a2))

    for name1, data1 in positions.items():
        for name2, data2 in positions.items():
            if name1 >= name2:
                continue
            diff = min((data1["sidereal_long"] - data2["sidereal_long"]) % 360, 
                       (data2["sidereal_long"] - data1["sidereal_long"]) % 360)
            if 175 <= diff <= 185:
                patterns["Symmetries"].append((name1, name2))
            if opposites[data1["sign"]] == data2["sign"]:
                patterns["Polarities"].append((name1, name2))

    return patterns

# Calculate planetary cycles
def calculate_planetary_cycles(observer, planets, positions):
    cycles = {}
    original_date = observer.date
    observer.date = original_date - 1.0

    prev_positions = {}
    for planet, body in planets.items():
        if planet in ["Black Moon Lilith", "Dark Moon Lilith", "Asteroid Lilith", "Rahu", "Ketu"]:
            days_since_ref = observer.date - ephem.Date("2000/01/01" if planet in ["Black Moon Lilith", "Rahu"] else 
                                                       "1898/01/01" if planet == "Dark Moon Lilith" else 
                                                       "1927/02/11")
            prev_long = {
                "Black Moon Lilith": (83 + days_since_ref * 0.111404 + 180) % 360,
                "Dark Moon Lilith": (days_since_ref * 3.025) % 360,
                "Asteroid Lilith": (days_since_ref * 0.23) % 360,
                "Rahu": (15 - days_since_ref * 0.053) % 360,
                "Ketu": (prev_positions["Rahu"] + 180) % 360 if "Rahu" in prev_positions else 0
            }[planet]
        else:
            body.compute(observer)
            prev_long = rad_to_deg(body.hlon)
        prev_positions[planet] = prev_long

    observer.date = original_date
    max_velocity = 0
    for planet in planets:
        curr_long = positions[planet]["tropical_long"]
        prev_long = prev_positions[planet]
        delta_long = (curr_long - prev_long + 180) % 360 - 180
        velocity = delta_long
        cycle_length = 360 / abs(velocity) if abs(velocity) > 0.0001 else float('inf')
        cycles[planet] = {
            "velocity": velocity,
            "cycle_length": cycle_length,
            "retrograde": " (Retrograde)" if velocity < 0 else ""
        }
        max_velocity = max(max_velocity, abs(velocity))

    sun_long = positions["Sun"]["sidereal_long"]
    for planet in cycles:
        vel = cycles[planet]["velocity"]
        long = positions[planet]["sidereal_long"]
        freq = (vel / max_velocity) * math.cos(math.radians(long - sun_long))
        cycles[planet]["frequency"] = max(min(freq, 1.0), -1.0)

    return cycles

# Sacred geometry formations
def sacred_geometry(positions):
    geo_forms = {"Tetrahedron": [60], "Cube": [90], "Octahedron": [120], "Dodecahedron": [108], "Icosahedron": [180]}
    active_forms = set()
    for planet, data in positions.items():
        for form, angles in geo_forms.items():
            for angle in angles:
                if any(abs(min((data["sidereal_long"] - p["sidereal_long"]) % 360, 
                              (p["sidereal_long"] - data["sidereal_long"]) % 360) - angle) < 1 
                       for p_name, p in positions.items() if p_name != planet):
                    active_forms.add(f"{form} active with {planet}")
    return list(active_forms)

# Spectral analysis
def spectral_analysis(positions, dt, cycles, aspects):
    times = np.linspace(0, 24, 25)
    energies = {}
    for planet, data in positions.items():
        if planet in ["Ascendant", "Midheaven", "Black Moon Lilith", "Dark Moon Lilith", "Asteroid Lilith", "Rahu", "Ketu"]:
            continue
        freq = cycles[planet]["frequency"]
        amplitude = data["distance"]
        phase = data["sidereal_long"] / 360 * 2 * math.pi
        wave = [amplitude * math.sin(2 * math.pi * freq * t + phase) for t in times]
        energies[planet] = wave

    total_energy = np.sum(list(energies.values()), axis=0)
    fft = np.fft.fft(total_energy)
    freqs = np.fft.fftfreq(len(times), d=24/len(times))
    predominant_freqs = sorted(zip(abs(fft), freqs), reverse=True)[:5]

    planet_contributions = {p: sum(abs(np.fft.fft(wave))) for p, wave in energies.items()}
    top_planets = sorted(planet_contributions.items(), key=lambda x: x[1], reverse=True)[:3]

    polarity = "Positive" if np.mean(total_energy) > 0 else "Negative"
    trend = "Up" if total_energy[-1] > total_energy[0] else "Down"
    trend_desc = ("Dip Reversal (down-to-up)" if trend == "Up" else "Continuing Down") if polarity == "Negative" else \
                 ("Peak Reversal (up-to-down)" if trend == "Down" else "Continuing Up")
    dip_planet = min(cycles.items(), key=lambda x: x[1]["frequency"])[0]
    peak_planet = max(cycles.items(), key=lambda x: x[1]["frequency"])[0]

    daily_pulse = max(min(sum(c["frequency"] for c in cycles.values()) / len(cycles) + len(aspects) * 0.05, 1.0), -1.0)
    pulse_desc = "High" if daily_pulse > 0.5 else "Low" if daily_pulse < -0.5 else "Moderate"

    return {
        "spectrum": total_energy.tolist(),
        "predominant_frequencies": [(amp, freq) for amp, freq in predominant_freqs],
        "top_planets": top_planets,
        "polarity": polarity,
        "trend": trend,
        "energy_forecast": f"Energy is {polarity}, {trend_desc} on {dt}, from {dip_planet} (dip) to {peak_planet} (peak), "
                          f"influenced by {', '.join(f'{p} (Amp={a:.2f})' for p, a in top_planets)}. Daily Pulse: {pulse_desc} ({daily_pulse:.2f})"
    }

# Enhanced Fear and Greed Index
def calculate_fear_greed_index(positions, cycles, aspects):
    lilith_aspects = [(p1, p2, asp, diff, strength) for p1, p2, asp, diff, strength in aspects 
                      if p1 == "Black Moon Lilith" or p2 == "Black Moon Lilith"]
    lilith_velocity = cycles["Black Moon Lilith"]["velocity"]
    lilith_sign = positions["Black Moon Lilith"]["sign"]
    lilith_long = positions["Black Moon Lilith"]["sidereal_long"]

    aspect_score = sum(strength for _, _, _, _, strength in lilith_aspects)
    element_modifiers = {"Fire": 0.1, "Air": 0.05, "Earth": 0.0, "Water": -0.1}
    zodiac_score = element_modifiers[zodiac_elements[lilith_sign][0]]
    velocity_factor = (lilith_velocity - 0.111404) / 0.111404 * 0.3
    retrograde_factor = -0.2 if lilith_velocity < 0 else 0.0
    degree_score = math.sin(math.radians(lilith_long)) * 0.2

    fear_greed_index = aspect_score + zodiac_score + velocity_factor + retrograde_factor + degree_score
    fear_greed_index = max(min(fear_greed_index, 1.0), -1.0)

    ranges = [
        (-1.0, -0.5, "Extreme Fear", "Deep uncertainty and withdrawal dominate."),
        (-0.5, -0.1, "Fear", "Caution and hesitation prevail."),
        (-0.1, 0.1, "Neutral", "Balanced energies, neither fear nor greed dominates."),
        (0.1, 0.5, "Greed", "Optimism and risk-taking emerge."),
        (0.5, 1.0, "Extreme Greed", "Exuberance and overconfidence peak.")
    ]
    description, range_desc = next((desc, r_desc) for min_v, max_v, desc, r_desc in ranges if min_v <= fear_greed_index <= max_v)

    transitions = {
        "Upward": {"Extreme Fear to Fear": (-0.5, 180), "Fear to Neutral": (-0.1, 90), "Neutral to Greed": (0.1, 60), "Greed to Extreme Greed": (0.5, 120)},
        "Downward": {"Extreme Greed to Greed": (0.5, 135), "Greed to Neutral": (0.1, 90), "Neutral to Fear": (-0.1, 45), "Fear to Extreme Fear": (-0.5, 180)}
    }
    transition_desc = "\n".join(
        f"{direction} Transitions:\n" + "\n".join(f"  {label} at {thresh:.1f} (typical degree: {deg}°)" 
        for label, (thresh, deg) in trans.items()) for direction, trans in transitions.items())

    return fear_greed_index, description, lilith_aspects, range_desc, transition_desc

# Plot astrological wheel
def plot_astrological_wheel(positions, zodiac_signs, local_time):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.axis('off')

    for sign, start, element, modality, polarity in zodiac_signs:
        wedge = Wedge((0, 0), 1, start, start + 30, facecolor=element_colors[element], alpha=0.5)
        ax.add_patch(wedge)
        angle = math.radians(start + 15)
        ax.text(1.1 * math.cos(angle), 1.1 * math.sin(angle), sign, ha='center', va='center', fontsize=10, rotation=-(start + 15))
        ax.text(0.7 * math.cos(angle), 0.7 * math.sin(angle), f"{element}\n{modality}\n{polarity}", ha='center', va='center', fontsize=8)

    for planet, data in positions.items():
        angle = math.radians(360 - data["sidereal_long"] + 90)
        x, y = 0.9 * math.cos(angle), 0.9 * math.sin(angle)
        ax.plot(x, y, 'o', color=data["color"], label=planet)
        ax.text(x * 1.05, y * 1.05, planet, fontsize=8)

    ax.text(0, 0, "THE 12 SIGNS", ha='center', va='center', fontsize=14, color='purple')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"Sidereal Astrological Wheel for {local_time}")
    plt.show()

# Generate cosmic reflection
def generate_cosmic_reflection(local_time, asc_sign, mc_sign, aspects, patterns, positions, cycles, analysis, fear_greed_index, description, lilith_aspects, sacred_geo):
    asc_element, asc_q1, asc_q2 = zodiac_elements[asc_sign]
    mc_element, mc_q1, mc_q2 = zodiac_elements[mc_sign]
    reflection = (f"On {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}, with Ascendant in {asc_sign} ({asc_element}, {asc_q1} and {asc_q2}) "
                  f"and Midheaven in {mc_sign} ({mc_element}, {mc_q1} and {mc_q2}), the heavens weave a cosmic tapestry:\n"
                  f"The sky’s {len(aspects)} aspects form intricate patterns, including {', '.join(k for k, v in patterns.items() if v)}—"
                  f"their {sum(1 for v in patterns.values() if v)} forms reflect the {len(positions)} celestial bodies’ symmetries and polarities.\n"
                  f"Spectral Analysis: {analysis['energy_forecast']}\n"
                  f"Black Moon Lilith Fear and Greed Index: {fear_greed_index:.2f} ({description})\n"
                  f"This celestial dance unveils a timeless harmony on this day.")
    return reflection

# Main calculation function
def calculate_planetary_positions():
    try:
        local_time, utc_time, lat, lon = get_local_datetime()
        observer = setup_observer(lat, lon, utc_time)
        positions, planets = get_planetary_positions(observer)

        moon_phase = positions["Moon"]["phase"]
        phase_name = ("New Moon" if 0 <= moon_phase < 1 else "Waxing Crescent" if 1 <= moon_phase < 49 else 
                      "First Quarter" if 49 <= moon_phase < 51 else "Waxing Gibbous" if 51 <= moon_phase < 99 else 
                      "Full Moon" if 99 <= moon_phase <= 100 else "Waning Gibbous" if 100 < moon_phase <= 149 else 
                      "Last Quarter" if 149 < moon_phase <= 151 else "Waning Crescent")

        print(f"Planetary Positions for {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"UTC Time: {utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Location: Latitude {lat:.4f}°, Longitude {lon:.4f}°")
        print("--------------------------------------------------")
        print(f"Moon Phase: {phase_name}, ~{moon_phase:.1f}% illuminated")
        print(f"Moon Zodiac: {positions['Moon']['sign']} (Sidereal: ~{positions['Moon']['sidereal_long']:.1f}°, House {positions['Moon']['house']})")
        print("\nPlanetary Positions (Vedic Sidereal):")
        for planet, data in positions.items():
            element, q1, q2 = zodiac_elements[data['sign']]
            extras = (f", Phase={data['phase']:.1f}%" if planet == "Moon" else "") + \
                     (f", Magnitude={data['magnitude']:.2f}" if data.get('magnitude') else "") + \
                     (f", Dignity={data.get('dignity', 'N/A')}" if 'dignity' in data else "")
            print(f"{planet}:\n  Sidereal Longitude: {data['sidereal_long']:.2f}°\n  Tropical Longitude: {data['tropical_long']:.2f}°\n"
                  f"  Zodiac Sign: {data['sign']} ({element}, {q1} and {q2}, {data['modality']}, {data['polarity']}, {data['nakshatra']})\n"
                  f"  House: {data['house']}" + (f"\n  Distance: {data['distance']:.2f} AU{extras}" if 'distance' in data else "") + "\n")

        aspects = calculate_aspects(positions)
        print("Aspects:\n--------")
        for p1, p2, aspect, diff, strength in aspects:
            print(f"{p1} - {p2}: {aspect} ({diff:.2f}°) [Strength: {strength:.2f}]")

        patterns = build_geometric_patterns(positions, aspects)
        print("\nGeometric Patterns:\n------------------")
        for pattern, instances in patterns.items():
            if instances:
                print(f"{pattern}:\n" + "\n".join(f"  {inst}" for inst in instances))

        cycles = calculate_planetary_cycles(observer, planets, positions)
        print("\nPlanetary Cycles (Sorted by Frequency, -1 to +1):")
        for planet, data in sorted(cycles.items(), key=lambda x: x[1]["frequency"]):
            print(f"{planet}: Velocity={data['velocity']:.2f}°/day{data['retrograde']}, Cycle={data['cycle_length']:.2f} days, Frequency={data['frequency']:.2f}")

        sacred_geo = sacred_geometry(positions)
        print("\nSacred Geometry Formations (Sidereal):")
        for form in sacred_geo:
            print(form)

        analysis = spectral_analysis(positions, local_time, cycles, aspects)
        print("\nSpectral Analysis:")
        print(f"Spectrum (25 points): {analysis['spectrum']}")
        print("Top 5 Predominant Frequencies (Amplitude, Freq):")
        for amp, freq in analysis["predominant_frequencies"]:
            print(f"Amplitude={amp:.2f}, Frequency={freq:.4f} cycles/hour")
        print(f"Top Influential Planets: {', '.join(f'{p} (Amp={a:.2f})' for p, a in analysis['top_planets'])}")
        print(f"Polarity: {analysis['polarity']}\nTrend: {analysis['trend']}")
        print(f"Energy Forecast: {analysis['energy_forecast']}")

        fear_greed_index, description, lilith_aspects, range_desc, transition_desc = calculate_fear_greed_index(positions, cycles, aspects)
        print("\nBlack Moon Lilith Fear and Greed Index:")
        print(f"Index: {fear_greed_index:.2f} ({description})\nRange Description: {range_desc}")
        print("Lilith Aspects Contributing to Index:")
        for p1, p2, aspect, diff, strength in lilith_aspects:
            print(f"{p1} - {p2}: {aspect} ({diff:.2f}°) [Strength: {strength:.2f}]")
        print(transition_desc)

        reflection = generate_cosmic_reflection(local_time, positions["Ascendant"]["sign"], positions["Midheaven"]["sign"], 
                                               aspects, patterns, positions, cycles, analysis, fear_greed_index, description, lilith_aspects, sacred_geo)
        print("\nCosmic Reflection:\n-----------------\n" + reflection)

        print("\nGenerating Sidereal Astrological Wheel Plot...")
        plot_astrological_wheel(positions, zodiac_signs, local_time)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    calculate_planetary_positions()