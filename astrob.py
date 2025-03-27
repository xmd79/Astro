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
    ("Aries", 0, "Fire", "Cardinal", "+"), ("Taurus", 30, "Earth", "Fixed", "-"), ("Gemini", 60, "Air", "Mutable", "+"),
    ("Cancer", 90, "Water", "Cardinal", "-"), ("Leo", 120, "Fire", "Fixed", "+"), ("Virgo", 150, "Earth", "Mutable", "-"),
    ("Libra", 180, "Air", "Cardinal", "+"), ("Scorpio", 210, "Water", "Fixed", "-"), ("Sagittarius", 240, "Fire", "Mutable", "+"),
    ("Capricorn", 270, "Earth", "Cardinal", "-"), ("Aquarius", 300, "Air", "Fixed", "+"), ("Pisces", 330, "Water", "Mutable", "-")
]

zodiac_elements = {sign[0]: (sign[2], "hot" if sign[2] in ["Fire", "Air"] else "cold", 
                            "dry" if sign[2] in ["Fire", "Earth"] else "wet") for sign in zodiac_signs}

# Nakshatras and Lunar Mansions (27) with attributes
nakshatras = [
    ("Ashwini", 0, "Ketu", "Swift", "Healing"), ("Bharani", 13.33, "Venus", "Bearing", "Transformation"),
    ("Krittika", 26.66, "Sun", "Cutting", "Purification"), ("Rohini", 40, "Moon", "Growth", "Creativity"),
    ("Mrigashira", 53.33, "Mars", "Searching", "Exploration"), ("Ardra", 66.66, "Rahu", "Storm", "Change"),
    ("Punarvasu", 80, "Jupiter", "Return", "Renewal"), ("Pushya", 93.33, "Saturn", "Nourishment", "Prosperity"),
    ("Ashlesha", 106.66, "Mercury", "Entwining", "Deception"), ("Magha", 120, "Ketu", "Mighty", "Ancestry"),
    ("Purva Phalguni", 133.33, "Venus", "First Red", "Love"), ("Uttara Phalguni", 146.66, "Sun", "Latter Red", "Partnership"),
    ("Hasta", 160, "Moon", "Hand", "Skill"), ("Chitra", 173.33, "Mars", "Bright", "Artistry"),
    ("Swati", 186.66, "Rahu", "Independent", "Freedom"), ("Vishakha", 200, "Jupiter", "Forked", "Determination"),
    ("Anuradha", 213.33, "Saturn", "Success", "Friendship"), ("Jyeshtha", 226.66, "Mercury", "Eldest", "Authority"),
    ("Mula", 240, "Ketu", "Root", "Destruction"), ("Purva Ashadha", 253.33, "Venus", "First Unconquered", "Victory"),
    ("Uttara Ashadha", 266.66, "Sun", "Latter Unconquered", "Leadership"), ("Shravana", 280, "Moon", "Hearing", "Learning"),
    ("Dhanishta", 293.33, "Mars", "Wealthy", "Fame"), ("Shatabhisha", 306.66, "Rahu", "Hundred Healers", "Mystery"),
    ("Purva Bhadrapada", 320, "Jupiter", "First Blessed Foot", "Spirituality"), ("Uttara Bhadrapada", 333.33, "Saturn", "Latter Blessed Foot", "Stability"),
    ("Revati", 346.66, "Mercury", "Wealthy", "Compassion")
]

# Planetary dignities
dignities = {
    "Sun": {"exalted": "Aries", "debilitated": "Libra", "ruler": ["Leo"], "detriment": ["Aquarius"], "fall": "Libra"},
    "Moon": {"exalted": "Taurus", "debilitated": "Scorpio", "ruler": ["Cancer"], "detriment": ["Capricorn"], "fall": "Scorpio"},
    "Mercury": {"exalted": "Virgo", "debilitated": "Pisces", "ruler": ["Gemini", "Virgo"], "detriment": ["Sagittarius", "Pisces"], "fall": "Pisces"},
    "Venus": {"exalted": "Pisces", "debilitated": "Virgo", "ruler": ["Taurus", "Libra"], "detriment": ["Scorpio", "Aries"], "fall": "Virgo"},
    "Mars": {"exalted": "Capricorn", "debilitated": "Cancer", "ruler": ["Aries", "Scorpio"], "detriment": ["Libra", "Taurus"], "fall": "Cancer"},
    "Jupiter": {"exalted": "Cancer", "debilitated": "Capricorn", "ruler": ["Sagittarius", "Pisces"], "detriment": ["Gemini", "Virgo"], "fall": "Capricorn"},
    "Saturn": {"exalted": "Libra", "debilitated": "Aries", "ruler": ["Capricorn", "Aquarius"], "detriment": ["Cancer", "Leo"], "fall": "Aries"}
}

# Theosophical attributes for planets
PLANET_ATTRIBUTES = {
    "Sun": {"element": "Fire", "virtue": "Illumination", "sephiroth": "Tiphareth", "hierarchy": "High", "numerology": (1, "Initiation")},
    "Moon": {"element": "Water", "virtue": "Intuition", "sephiroth": "Yesod", "hierarchy": "Medium", "numerology": (2, "Duality")},
    "Mercury": {"element": "Air", "virtue": "Communication", "sephiroth": "Hod", "hierarchy": "Low", "numerology": (3, "Creativity")},
    "Venus": {"element": "Earth", "virtue": "Love", "sephiroth": "Netzach", "hierarchy": "Medium", "numerology": (4, "Harmony")},
    "Mars": {"element": "Fire", "virtue": "Strength", "sephiroth": "Geburah", "hierarchy": "High", "numerology": (5, "Action")},
    "Jupiter": {"element": "Air", "virtue": "Wisdom", "sephiroth": "Chesed", "hierarchy": "High", "numerology": (6, "Expansion")},
    "Saturn": {"element": "Earth", "virtue": "Discipline", "sephiroth": "Binah", "hierarchy": "High", "numerology": (7, "Structure")},
    "Uranus": {"element": "Air", "virtue": "Innovation", "sephiroth": "Chokhmah", "hierarchy": "Medium", "numerology": (8, "Change")},
    "Neptune": {"element": "Water", "virtue": "Spirituality", "sephiroth": "Kether", "hierarchy": "Low", "numerology": (9, "Mysticism")},
    "Pluto": {"element": "Water", "virtue": "Transformation", "sephiroth": "Daath", "hierarchy": "High", "numerology": (0, "Transcendence")}
}

# Chakras and planetary associations
CHAKRA_MAP = {
    "Sun": ("Solar Plexus", "Manipura", "Power", "Yellow"),
    "Moon": ("Sacral", "Svadhisthana", "Emotion", "Orange"),
    "Mercury": ("Throat", "Vishuddha", "Communication", "Blue"),
    "Venus": ("Heart", "Anahata", "Love", "Green"),
    "Mars": ("Root", "Muladhara", "Survival", "Red"),
    "Jupiter": ("Third Eye", "Ajna", "Wisdom", "Indigo"),
    "Saturn": ("Crown", "Sahasrara", "Spirituality", "Violet"),
    "Uranus": ("Third Eye", "Ajna", "Intuition", "Indigo"),
    "Neptune": ("Crown", "Sahasrara", "Mysticism", "Violet"),
    "Pluto": ("Root", "Muladhara", "Transformation", "Red")
}

# Element colors
element_colors = {"Fire": "red", "Earth": "green", "Air": "yellow", "Water": "blue"}

# Ayanamsa for sidereal calculations
ayanamsa = 24.0

# Global ranges for Fear and Greed Index
ranges = [
    (-1.0, -0.5, "Extreme Fear", "Deep uncertainty and withdrawal dominate."),
    (-0.5, -0.1, "Fear", "Caution and hesitation prevail."),
    (-0.1, 0.1, "Neutral", "Balanced energies, neither fear nor greed dominates."),
    (0.1, 0.5, "Greed", "Optimism and risk-taking emerge."),
    (0.5, 1.0, "Extreme Greed", "Exuberance and overconfidence peak.")
]

# Planetary hours order (traditional Chaldean order)
PLANETARY_HOURS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

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
    return local_time, utc_time, lat, lon, timezone

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

# Calculate planetary hours
def calculate_planetary_hours(local_time, lat, lon):
    observer = setup_observer(lat, lon, local_time.astimezone(pytz.UTC))
    
    observer.horizon = '-0:34'
    sunrise = observer.next_rising(ephem.Sun()).datetime().replace(tzinfo=pytz.UTC)
    sunset = observer.next_setting(ephem.Sun()).datetime().replace(tzinfo=pytz.UTC)
    
    timezone = local_time.tzinfo
    sunrise = sunrise.astimezone(timezone)
    sunset = sunset.astimezone(timezone)
    
    day_length = (sunset - sunrise).total_seconds() / 3600
    night_length = 24 - day_length
    
    day_hour_length = day_length / 12
    night_hour_length = night_length / 12
    
    day_of_week = local_time.weekday()
    day_rulers = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    start_planet = day_rulers[day_of_week]
    start_idx = PLANETARY_HOURS.index(start_planet)
    
    planetary_hours = []
    current_time = sunrise
    for i in range(12):
        planet_idx = (start_idx + i) % 7
        planet = PLANETARY_HOURS[planet_idx]
        end_time = current_time + datetime.timedelta(hours=day_hour_length)
        planetary_hours.append((current_time, end_time, planet, "Day"))
        current_time = end_time
    
    current_time = sunset
    for i in range(12):
        planet_idx = (start_idx + 12 + i) % 7
        planet = PLANETARY_HOURS[planet_idx]
        end_time = current_time + datetime.timedelta(hours=night_hour_length)
        planetary_hours.append((current_time, end_time, planet, "Night"))
        current_time = end_time
    
    current_planet = None
    for start, end, planet, period in planetary_hours:
        if start <= local_time <= end:
            current_planet = (planet, period, start, end)
            break
    
    if current_planet is None:
        closest_hour = min(planetary_hours, key=lambda x: abs((x[0] - local_time).total_seconds()))
        current_planet = (closest_hour[2], closest_hour[3], closest_hour[0], closest_hour[1])
        print(f"Warning: Local time {local_time} not within calculated hours. Using closest: {closest_hour[2]} from {closest_hour[0]} to {closest_hour[1]}")
    
    return planetary_hours, current_planet

# Calculate planetary positions with lunar mansions and chakra associations (Fixed)
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
        
        nak_idx = int(sidereal_long / 13.3333) % 27  # Fixed for 27 nakshatras
        nakshatra_name, _, nak_ruler, nak_quality, nak_attribute = nakshatras[nak_idx]

        chakra_data = CHAKRA_MAP.get(name, ("None", "None", "None", "gray"))
        chakra, chakra_sanskrit, chakra_energy, chakra_color = chakra_data

        data = {
            "sidereal_long": sidereal_long,
            "tropical_long": trop_long,
            "house": house_num,
            "sign": sign,
            "element": element,
            "modality": modality,
            "polarity": polarity,
            "nakshatra": nakshatra_name,
            "nakshatra_ruler": nak_ruler,
            "nakshatra_quality": nak_quality,
            "nakshatra_attribute": nak_attribute,
            "chakra": chakra,
            "chakra_sanskrit": chakra_sanskrit,
            "chakra_energy": chakra_energy,
            "chakra_color": chakra_color,
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
            if name in PLANET_ATTRIBUTES:
                data.update({
                    "theosophical_element": PLANET_ATTRIBUTES[name]["element"],
                    "theosophical_virtue": PLANET_ATTRIBUTES[name]["virtue"],
                    "theosophical_sephiroth": PLANET_ATTRIBUTES[name]["sephiroth"],
                    "theosophical_hierarchy": PLANET_ATTRIBUTES[name]["hierarchy"],
                    "theosophical_numerology": PLANET_ATTRIBUTES[name]["numerology"]
                })
        positions[name] = data

    positions["Ascendant"] = {
        "sidereal_long": asc_sidereal,
        "tropical_long": rad_to_deg(asc_long),
        "house": 1,
        "sign": asc_sign,
        "element": asc_element,
        "modality": asc_modality,
        "polarity": asc_polarity,
        "nakshatra": nakshatras[int(asc_sidereal / 13.3333) % 27][0],  # Fixed for 27 nakshatras
        "nakshatra_ruler": nakshatras[int(asc_sidereal / 13.3333) % 27][2],
        "nakshatra_quality": nakshatras[int(asc_sidereal / 13.3333) % 27][3],
        "nakshatra_attribute": nakshatras[int(asc_sidereal / 13.3333) % 27][4],
        "chakra": "None",
        "chakra_sanskrit": "None",
        "chakra_energy": "None",
        "chakra_color": "gray",
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
        "nakshatra": nakshatras[int(((rad_to_deg(mc_long) - ayanamsa) % 360) / 13.3333) % 27][0],  # Fixed for 27 nakshatras
        "nakshatra_ruler": nakshatras[int(((rad_to_deg(mc_long) - ayanamsa) % 360) / 13.3333) % 27][2],
        "nakshatra_quality": nakshatras[int(((rad_to_deg(mc_long) - ayanamsa) % 360) / 13.3333) % 27][3],
        "nakshatra_attribute": nakshatras[int(((rad_to_deg(mc_long) - ayanamsa) % 360) / 13.3333) % 27][4],
        "chakra": "None",
        "chakra_sanskrit": "None",
        "chakra_energy": "None",
        "chakra_color": "gray",
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

    for a1, a2, aspect, _, _ in aspects:
        if aspect == "Trine":
            for b1, b2, asp, _, _ in aspects:
                if asp == "Trine":
                    common_planet = set([a1, a2]) & set([b1, b2])
                    if common_planet:
                        common = common_planet.pop()
                        other1 = a1 if a1 != common else a2
                        other2 = b1 if b1 != common else b2
                        if other1 != other2 and other1 != common and other2 != common:
                            for c1, c2, asp2, diff2, _ in aspects:
                                if asp2 == "Trine" and {c1, c2} == {other1, other2}:
                                    triad = tuple(sorted([common, other1, other2]))
                                    if triad not in patterns["Triads"]:
                                        patterns["Triads"].append(triad)

    for a1, a2, aspect, _, _ in aspects:
        if aspect == "Square":
            for b1, b2, asp, _, _ in aspects:
                if asp == "Square":
                    planets_set = set([a1, a2, b1, b2])
                    if len(planets_set) == 4:
                        planets = list(planets_set)
                        square_pairs = 0
                        for i in range(len(planets)):
                            for j in range(i + 1, len(planets)):
                                p1, p2 = planets[i], planets[j]
                                for c1, c2, asp2, diff2, _ in aspects:
                                    if asp2 == "Square" and {c1, c2} == {p1, p2}:
                                        square_pairs += 1
                                        break
                        if square_pairs >= 4:
                            square = tuple(sorted(planets))
                            if square not in patterns["Squares"]:
                                patterns["Squares"].append(square)

    for a1, a2, aspect, diff, _ in aspects:
        if aspect == "Quintile":
            patterns["Pentagrams"].append((a1, a2))
        if aspect == "Sextile":
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

# Calculate planetary cycles with symmetrical distance percentages
def calculate_planetary_cycles(observer, planets, positions, local_time, timezone):
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
        
        curr_sidereal = positions[planet]["sidereal_long"]
        cycle_progress = (curr_sidereal % 360) / 360
        days_since_start = cycle_progress * cycle_length if velocity > 0 else (1 - cycle_progress) * cycle_length
        days_to_end = (1 - cycle_progress) * cycle_length if velocity > 0 else cycle_progress * cycle_length
        
        start_date = ephem.Date(original_date - days_since_start)
        end_date = ephem.Date(original_date + days_to_end)
        start_tuple = [int(x) for x in start_date.tuple()[:6]]
        end_tuple = [int(x) for x in end_date.tuple()[:6]]
        start_local = timezone.fromutc(datetime.datetime(*start_tuple)).strftime('%Y-%m-%d %H:%M:%S %Z')
        end_local = timezone.fromutc(datetime.datetime(*end_tuple)).strftime('%Y-%m-%d %H:%M:%S %Z')
        
        start_long = (curr_sidereal - (days_since_start * velocity)) % 360
        max_long = (start_long + 180) % 360
        end_long = (start_long + 360) % 360
        
        dist_to_start = cycle_progress * 100 if velocity > 0 else (1 - cycle_progress) * 100
        dist_to_max = 100.0 - dist_to_start
        
        cycles[planet] = {
            "velocity": velocity,
            "cycle_length": cycle_length,
            "retrograde": " (Retrograde)" if velocity < 0 else "",
            "start_long": start_long,
            "max_long": max_long,
            "end_long": end_long,
            "start_datetime": start_local,
            "end_datetime": end_local,
            "dist_to_start": dist_to_start,
            "dist_to_max": dist_to_max
        }
        max_velocity = max(max_velocity, abs(velocity))

    sun_long = positions["Sun"]["sidereal_long"]
    for planet in cycles:
        vel = cycles[planet]["velocity"]
        long = positions[planet]["sidereal_long"]
        freq = (vel / max_velocity) * math.cos(math.radians(long - sun_long))
        cycles[planet]["frequency"] = max(min(freq, 1.0), -1.0)

    return cycles

# Harmonic Resonance Analysis
def calculate_harmonic_resonance(cycles, positions):
    resonance_pairs = []
    for p1 in cycles:
        for p2 in cycles:
            if p1 >= p2:
                continue
            freq1 = cycles[p1]["frequency"]
            freq2 = cycles[p2]["frequency"]
            long1 = positions[p1]["sidereal_long"]
            long2 = positions[p2]["sidereal_long"]
            diff = min((long1 - long2) % 360, (long2 - long1) % 360)
            
            freq_ratio = min(freq1 / freq2, freq2 / freq1) if freq2 != 0 else 1
            resonance = (1 - (diff / 180)) * freq_ratio
            if resonance > 0.5:
                resonance_pairs.append((p1, p2, resonance))
    
    return sorted(resonance_pairs, key=lambda x: x[2], reverse=True)

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
    trend = "Up" if polarity == "Negative" else "Down"
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

# Fear and Greed Index for a single planet with retrograde effects
def calculate_planet_fear_greed_index(planet_name, positions, cycles, aspects):
    planet_aspects = [(p1, p2, asp, diff, strength) for p1, p2, asp, diff, strength in aspects 
                      if p1 == planet_name or p2 == planet_name]
    velocity = cycles[planet_name]["velocity"]
    sign = positions[planet_name]["sign"]
    long = positions[planet_name]["sidereal_long"]

    aspect_score = sum(strength for _, _, _, _, strength in planet_aspects)
    element_modifiers = {"Fire": 0.1, "Air": 0.05, "Earth": 0.0, "Water": -0.1}
    zodiac_score = element_modifiers[zodiac_elements[sign][0]]
    mean_velocity = 0.111404 if planet_name == "Black Moon Lilith" else 1.0
    velocity_factor = (velocity - mean_velocity) / mean_velocity * 0.3
    
    retrograde_factor = -0.2 if velocity < 0 else 0.0
    if velocity < 0:
        retrograde_impact = -0.1 * (abs(velocity) / mean_velocity)
        retrograde_factor += retrograde_impact
        if sign in dignities.get(planet_name, {}).get("debilitated", []):
            retrograde_factor -= 0.1
        elif sign in dignities.get(planet_name, {}).get("exalted", []):
            retrograde_factor += 0.05
    
    degree_score = math.sin(math.radians(long)) * 0.2

    fear_greed_index = aspect_score + zodiac_score + velocity_factor + retrograde_factor + degree_score
    fear_greed_index = max(min(fear_greed_index, 1.0), -1.0)

    description, range_desc = next((desc, r_desc) for min_v, max_v, desc, r_desc in ranges if min_v <= fear_greed_index <= max_v)

    return fear_greed_index, description, planet_aspects

# Simplified hourly Fear and Greed Index
def calculate_hourly_fear_greed_index(positions, cycles, aspects):
    hourly_fgi = {}
    for planet in positions:
        if planet not in ["Ascendant", "Midheaven"]:
            index, desc, _ = calculate_planet_fear_greed_index(planet, positions, cycles, aspects)
            hourly_fgi[planet] = (float(index), str(desc))
    return hourly_fgi

# Extended forecast calculation for multiple time frames
def calculate_time_frame_forecasts(hourly_fgi, observer, planets, local_time, timezone):
    forecasts = {'hourly': hourly_fgi, 'daily': 0.0, 'weekly': 0.0, 'monthly': 0.0, 'yearly': 0.0}
    
    daily_indices = []
    for hour in range(24):
        future_time = local_time + datetime.timedelta(hours=hour)
        observer.date = future_time.astimezone(pytz.UTC)
        positions, _ = get_planetary_positions(observer)
        cycles = calculate_planetary_cycles(observer, planets, positions, future_time, timezone)
        aspects = calculate_aspects(positions)
        fgi = calculate_hourly_fear_greed_index(positions, cycles, aspects)
        daily_indices.extend([idx for idx, _ in fgi.values()])
    forecasts['daily'] = np.mean(daily_indices) if daily_indices else 0.0
    
    weekly_indices = []
    for day in range(7):
        future_time = local_time + datetime.timedelta(days=day)
        observer.date = future_time.astimezone(pytz.UTC)
        positions, _ = get_planetary_positions(observer)
        cycles = calculate_planetary_cycles(observer, planets, positions, future_time, timezone)
        aspects = calculate_aspects(positions)
        fgi = calculate_hourly_fear_greed_index(positions, cycles, aspects)
        weekly_indices.extend([idx for idx, _ in fgi.values()])
    forecasts['weekly'] = np.mean(weekly_indices) if weekly_indices else 0.0
    
    monthly_indices = []
    for day in range(30):
        future_time = local_time + datetime.timedelta(days=day)
        observer.date = future_time.astimezone(pytz.UTC)
        positions, _ = get_planetary_positions(observer)
        cycles = calculate_planetary_cycles(observer, planets, positions, future_time, timezone)
        aspects = calculate_aspects(positions)
        fgi = calculate_hourly_fear_greed_index(positions, cycles, aspects)
        monthly_indices.extend([idx for idx, _ in fgi.values()])
    forecasts['monthly'] = np.mean(monthly_indices) if monthly_indices else 0.0
    
    yearly_indices = []
    for day in range(0, 365, 10):
        future_time = local_time + datetime.timedelta(days=day)
        observer.date = future_time.astimezone(pytz.UTC)
        positions, _ = get_planetary_positions(observer)
        cycles = calculate_planetary_cycles(observer, planets, positions, future_time, timezone)
        aspects = calculate_aspects(positions)
        fgi = calculate_hourly_fear_greed_index(positions, cycles, aspects)
        yearly_indices.extend([idx for idx, _ in fgi.values()])
    forecasts['yearly'] = np.mean(yearly_indices) if yearly_indices else 0.0
    
    return forecasts

# Enhanced Fear and Greed Index with Quadrants and Quadrature
def calculate_fear_greed_index(positions, cycles, aspects):
    lilith_fgi, description, lilith_aspects = calculate_planet_fear_greed_index("Black Moon Lilith", positions, cycles, aspects)
    velocity = cycles["Black Moon Lilith"]["velocity"]

    range_desc = next(r_desc for min_v, max_v, _, r_desc in ranges if min_v <= lilith_fgi <= max_v)

    transitions = {
        "Upward": [
            ("Extreme Fear to Fear", -0.5, 180),
            ("Fear to Neutral", -0.1, 90),
            ("Neutral to Greed", 0.1, 60),
            ("Greed to Extreme Greed", 0.5, 120)
        ],
        "Downward": [
            ("Extreme Greed to Greed", 0.5, 135),
            ("Greed to Neutral", 0.1, 90),
            ("Neutral to Fear", -0.1, 45),
            ("Fear to Extreme Fear", -0.5, 180)
        ]
    }
    transition_desc = "\n".join(
        f"{direction} Transitions:\n" + "\n".join(f"  {label} at {thresh:.1f} (typical degree: {deg}°)" 
        for label, thresh, deg in trans) for direction, trans in transitions.items())

    cycle_direction = "Upward" if velocity > 0 else "Downward"
    trans_list = transitions[cycle_direction]
    current_status = "Stable at " + description
    for i, (label, thresh, deg) in enumerate(trans_list):
        if lilith_fgi < thresh:
            prev_label = trans_list[i-1][0].split(" to ")[0] if i > 0 else description
            current_status = f"Transitioning from {prev_label} to {label.split(' to ')[1]} (Index: {lilith_fgi:.2f}, Threshold: {thresh:.1f})"
            break
        elif lilith_fgi == thresh:
            current_status = f"At transition point: {label} (Index: {lilith_fgi:.2f})"
            break
    else:
        current_status = f"Stable at {description} (Index: {lilith_fgi:.2f})"

    quad_map = {"Upward": ["Q1", "Q2", "Q3", "Q4"], "Downward": ["Q4", "Q3", "Q2", "Q1"]}
    if cycle_direction == "Upward":
        if -1.0 <= lilith_fgi < -0.5:
            current_quad = "Q4"
        elif -0.5 <= lilith_fgi < 0.0:
            current_quad = "Q3"
        elif 0.0 <= lilith_fgi < 0.5:
            current_quad = "Q1"
        else:
            current_quad = "Q2"
        dist_percent = ((lilith_fgi + 1.0) / 2.0) * 100
    else:
        if -1.0 <= lilith_fgi < -0.5:
            current_quad = "Q1"
        elif -0.5 <= lilith_fgi < 0.0:
            current_quad = "Q2"
        elif 0.0 <= lilith_fgi < 0.5:
            current_quad = "Q4"
        else:
            current_quad = "Q3"
        dist_percent = ((1.0 - lilith_fgi) / 2.0) * 100

    quad_order = quad_map[cycle_direction]
    current_idx = quad_order.index(current_quad)
    
    if cycle_direction == "Upward":
        if current_quad == "Q1":
            past_quad = "Q2"
            next_quad = "Q2"
        elif current_quad == "Q4":
            past_quad = "Q3"
            next_quad = "Q3"
        else:
            past_quad = quad_order[current_idx - 1]
            next_quad = quad_order[current_idx + 1]
    else:
        if current_quad == "Q4":
            past_quad = "Q3"
            next_quad = "Q3"
        elif current_quad == "Q1":
            past_quad = "Q2"
            next_quad = "Q2"
        else:
            past_quad = quad_order[current_idx - 1]
            next_quad = quad_order[current_idx + 1]

    quadrant_info = {
        "current": current_quad,
        "past": past_quad,
        "next": next_quad,
        "distance_percent": dist_percent,
        "cycle_direction": cycle_direction
    }

    quadrature = {}
    for p1, p2, asp, diff, _ in aspects:
        if asp in ["Square", "Opposition"]:
            quadrature[(p1, p2)] = asp

    planet_fgis = {p: calculate_planet_fear_greed_index(p, positions, cycles, aspects)[0] 
                   for p in positions if p not in ["Ascendant", "Midheaven"]}
    weights = {"Sun": 2.0, "Moon": 2.0, "Mercury": 1.0, "Venus": 1.0, "Mars": 1.0, "Jupiter": 1.0, "Saturn": 1.0,
               "Uranus": 0.5, "Neptune": 0.5, "Pluto": 0.5, "Black Moon Lilith": 0.5, "Dark Moon Lilith": 0.5,
               "Asteroid Lilith": 0.5, "Rahu": 0.5, "Ketu": 0.5}
    overall_fgi = sum(planet_fgis[p] * weights.get(p, 1.0) for p in planet_fgis) / sum(weights.get(p, 1.0) for p in planet_fgis)
    overall_desc = next(desc for min_v, max_v, desc, _ in ranges if min_v <= overall_fgi <= max_v)

    sidereal_fgi = sum(math.sin(math.radians(positions[p]["sidereal_long"])) * weights.get(p, 1.0) 
                       for p in positions if p not in ["Ascendant", "Midheaven"]) / sum(weights.get(p, 1.0) for p in planet_fgis)
    sidereal_desc = next(desc for min_v, max_v, desc, _ in ranges if min_v <= sidereal_fgi <= max_v)

    return (lilith_fgi, description, lilith_aspects, range_desc, transition_desc, current_status, 
            quadrant_info, planet_fgis, overall_fgi, overall_desc, sidereal_fgi, sidereal_desc, quadrature)

# Enhanced astrological wheel with planetary hours and lunar mansions
def plot_astrological_wheel(positions, zodiac_signs, local_time, planetary_hours, current_planet):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_aspect('equal')
    ax.axis('off')

    for sign, start, element, modality, polarity in zodiac_signs:
        wedge = Wedge((0, 0), 1, start, start + 30, facecolor=element_colors[element], alpha=0.5)
        ax.add_patch(wedge)
        angle = math.radians(start + 15)
        ax.text(1.1 * math.cos(angle), 1.1 * math.sin(angle), sign, ha='center', va='center', fontsize=10, rotation=-(start + 15))
        ax.text(0.7 * math.cos(angle), 0.7 * math.sin(angle), f"{element}\n{modality}\n{polarity}", ha='center', va='center', fontsize=8)

    for nak_name, start, ruler, quality, attribute in nakshatras:
        angle = math.radians(360 - start + 90)
        x, y = 1.2 * math.cos(angle), 1.2 * math.sin(angle)
        ax.text(x, y, nak_name, fontsize=6, color='purple', rotation=-(start - 90))

    for planet, data in positions.items():
        angle = math.radians(360 - data["sidereal_long"] + 90)
        x, y = 0.9 * math.cos(angle), 0.9 * math.sin(angle)
        ax.plot(x, y, 'o', color=data["color"], label=planet)
        ax.text(x * 1.05, y * 1.05, planet, fontsize=8)

    if current_planet:
        planet, period, start, end = current_planet
        ax.text(0, -1.3, f"Current Planetary Hour: {planet} ({period}, {start.strftime('%H:%M')} - {end.strftime('%H:%M')})", 
                ha='center', va='center', fontsize=10, color='black')

    ax.text(0, 0, "THE 12 SIGNS", ha='center', va='center', fontsize=14, color='purple')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(f"Sidereal Astrological Wheel for {local_time}")
    plt.show()

# Plot planetary hours timeline
def plot_planetary_hours(planetary_hours, local_time):
    fig, ax = plt.subplots(figsize=(12, 6))
    y_pos = 1
    for start, end, planet, period in planetary_hours:
        duration = (end - start).total_seconds() / 3600
        ax.barh(y_pos, duration, left=(start - start.replace(hour=0, minute=0, second=0)).total_seconds() / 3600, 
                color='lightblue' if period == "Day" else 'lightgray', edgecolor='black')
        ax.text((start - start.replace(hour=0, minute=0, second=0)).total_seconds() / 3600 + duration / 2, y_pos, 
                f"{planet}\n{start.strftime('%H:%M')} - {end.strftime('%H:%M')}", ha='center', va='center', fontsize=8)
        y_pos += 1
    
    current_hour = (local_time - local_time.replace(hour=0, minute=0, second=0)).total_seconds() / 3600
    ax.axvline(current_hour, color='red', linestyle='--', label='Current Time')
    
    ax.set_yticks([])
    ax.set_xlabel("Hour of Day")
    ax.set_title(f"Planetary Hours for {local_time.strftime('%Y-%m-%d')}")
    ax.legend()
    plt.show()

# Generate cosmic reflection
def generate_cosmic_reflection(local_time, asc_sign, mc_sign, aspects, patterns, positions, cycles, analysis, 
                              fear_greed_index, description, lilith_aspects, sacred_geo, overall_fgi, overall_desc, 
                              sidereal_fgi, sidereal_desc, current_planet, resonance_pairs, forecasts):
    asc_element, asc_q1, asc_q2 = zodiac_elements[asc_sign]
    mc_element, mc_q1, mc_q2 = zodiac_elements[mc_sign]
    planet_hour = current_planet[0] if current_planet else "Unknown"
    reflection = (f"On {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}, with Ascendant in {asc_sign} ({asc_element}, {asc_q1} and {asc_q2}) "
                  f"and Midheaven in {mc_sign} ({mc_element}, {mc_q1} and {mc_q2}), the heavens weave a cosmic tapestry:\n"
                  f"The sky’s {len(aspects)} aspects form intricate patterns, including {', '.join(k for k, v in patterns.items() if v)}—"
                  f"their {sum(1 for v in patterns.values() if v)} forms reflect the {len(positions)} celestial bodies’ symmetries and polarities.\n"
                  f"Spectral Analysis: {analysis['energy_forecast']}\n"
                  f"Black Moon Lilith Fear and Greed Index: {fear_greed_index:.2f} ({description})\n"
                  f"Overall Planetary Fear and Greed Index: {overall_fgi:.2f} ({overall_desc})\n"
                  f"Sidereal Fear and Greed Index: {sidereal_fgi:.2f} ({sidereal_desc})\n"
                  f"Current Planetary Hour: {planet_hour}\n"
                  f"Harmonic Resonance: {', '.join(f'{p1}-{p2} (Strength: {strength:.2f})' for p1, p2, strength in resonance_pairs[:3])}\n"
                  f"Forecasts: Daily: {forecasts['daily']:.2f}, Weekly: {forecasts['weekly']:.2f}, Monthly: {forecasts['monthly']:.2f}, Yearly: {forecasts['yearly']:.2f}\n"
                  f"This celestial dance unveils a timeless harmony on this day.")
    return reflection

# Main calculation function
def calculate_planetary_positions():
    try:
        local_time, utc_time, lat, lon, timezone = get_local_datetime()
        observer = setup_observer(lat, lon, utc_time)
        positions, planets = get_planetary_positions(observer)

        planetary_hours, current_planet = calculate_planetary_hours(local_time, lat, lon)

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
        print("--------------------------------------------------")
        
        for planet, data in positions.items():
            element, q1, q2 = zodiac_elements[data['sign']]
            extras = (f", Phase={data['phase']:.1f}%" if planet == "Moon" else "") + \
                     (f", Magnitude={data.get('magnitude', 'N/A'):.2f}" if data.get('magnitude') is not None else "") + \
                     (f", Dignity={data.get('dignity', 'N/A')}" if 'dignity' in data else "")
            print(f"{planet}:")
            print(f"  Sidereal Long: {data['sidereal_long']:.2f}°")
            print(f"  Tropical Long: {data['tropical_long']:.2f}°")
            print(f"  Sign: {data['sign']}")
            print(f"  Element: {element}")
            print(f"  Modality: {data['modality']}")
            print(f"  Polarity: {data['polarity']}")
            print(f"  House: {data['house']}")
            print(f"  Nakshatra: {data['nakshatra']} (Ruler: {data['nakshatra_ruler']}, Quality: {data['nakshatra_quality']}, Attribute: {data['nakshatra_attribute']})")
            print(f"  Chakra: {data.get('chakra', 'None')} (Energy: {data.get('chakra_energy', 'None')})")
            print(f"  Theosophical Virtue: {data.get('theosophical_virtue', 'N/A')}")
            print(f"  Theosophical Sephiroth: {data.get('theosophical_sephiroth', 'N/A')}")
            print(f"  Dignity: {data.get('dignity', 'N/A')}")
            print("--------------------------------------------------")

        aspects = calculate_aspects(positions)
        print("\nAspects:\n--------")
        for p1, p2, aspect, diff, strength in aspects:
            print(f"{p1} - {p2}: {aspect} ({diff:.2f}°) [Strength: {strength:.2f}]")

        patterns = build_geometric_patterns(positions, aspects)
        print("\nGeometric Patterns:\n------------------")
        for pattern, instances in patterns.items():
            if instances:
                print(f"{pattern}:")
                for inst in instances:
                    print(f"  {inst}")

        cycles = calculate_planetary_cycles(observer, planets, positions, local_time, timezone)
        print("\nPlanetary Cycles (Sorted by Frequency, -1 to +1):")
        for planet, data in sorted(cycles.items(), key=lambda x: x[1]["frequency"]):
            print(f"{planet}:")
            print(f"  Velocity: {data['velocity']:.2f}°/day{data['retrograde']}")
            print(f"  Cycle Length: {data['cycle_length']:.2f} days")
            print(f"  Frequency: {data['frequency']:.2f}")
            print(f"  Start Longitude: {data['start_long']:.2f}° at {data['start_datetime']}")
            print(f"  Max Longitude: {data['max_long']:.2f}°")
            print(f"  End Longitude: {data['end_long']:.2f}° at {data['end_datetime']}")
            print(f"  Distance to Start: {data['dist_to_start']:.2f}%")
            print(f"  Distance to Max: {data['dist_to_max']:.2f}% (Symmetrical Sum: {data['dist_to_start'] + data['dist_to_max']:.2f}%)")

        resonance_pairs = calculate_harmonic_resonance(cycles, positions)
        print("\nHarmonic Resonance Analysis (Top Pairs):")
        for p1, p2, strength in resonance_pairs[:5]:
            print(f"  {p1} - {p2}: Resonance Strength = {strength:.2f}")

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

        (fear_greed_index, description, lilith_aspects, range_desc, transition_desc, current_status, 
         quadrant_info, planet_fgis, overall_fgi, overall_desc, sidereal_fgi, sidereal_desc, quadrature) = calculate_fear_greed_index(positions, cycles, aspects)
        
        print("\nBlack Moon Lilith Fear and Greed Index:")
        print(f"Index: {fear_greed_index:.2f} ({description})\nRange Description: {range_desc}")
        print("Lilith Aspects Contributing to Index:")
        for p1, p2, aspect, diff, strength in lilith_aspects:
            print(f"{p1} - {p2}: {aspect} ({diff:.2f}°) [Strength: {strength:.2f}]")
        print(transition_desc)
        print(f"Current Status: {current_status}")
        print(f"Cycle Direction: {quadrant_info['cycle_direction']}")
        print(f"Current Quadrant: {quadrant_info['current']}")
        print(f"Past Quadrant: {quadrant_info['past']}")
        print(f"Next Quadrant: {quadrant_info['next']}")
        print(f"Distance Percentage: {quadrant_info['distance_percent']:.2f}% ({'from Extreme Fear to Extreme Greed' if quadrant_info['cycle_direction'] == 'Upward' else 'from Extreme Greed to Extreme Fear'})")

        print("\nQuadrature Analysis:")
        for (p1, p2), asp in quadrature.items():
            print(f"  {p1} - {p2}: {asp}")

        print("\nOverall Planetary Fear and Greed Index:")
        print(f"Overall Index: {overall_fgi:.2f} ({overall_desc})")
        print("Individual Planet Indices:")
        for planet, fgi in planet_fgis.items():
            desc = next(d for min_v, max_v, d, _ in ranges if min_v <= fgi <= max_v)
            print(f"  {planet}: {fgi:.2f} ({desc})")

        print("\nSidereal Fear and Greed Index:")
        print(f"Index: {sidereal_fgi:.2f} ({sidereal_desc})")

        hourly_fgi = calculate_hourly_fear_greed_index(positions, cycles, aspects)
        print("\nHourly Fear and Greed Index:")
        for planet, (index, desc) in hourly_fgi.items():
            print(f"  {planet}: {index:.2f} ({desc})")

        forecasts = calculate_time_frame_forecasts(hourly_fgi, observer, planets, local_time, timezone)
        print("\nFear and Greed Forecasts:")
        for timeframe, value in forecasts.items():
            if timeframe == 'hourly':
                continue
            desc = next((d for min_v, max_v, d, _ in ranges if min_v <= value <= max_v), "Neutral")
            print(f"  {timeframe.capitalize()}: {value:.2f} ({desc})")

        reflection = generate_cosmic_reflection(local_time, positions["Ascendant"]["sign"], positions["Midheaven"]["sign"], 
                                               aspects, patterns, positions, cycles, analysis, fear_greed_index, description, 
                                               lilith_aspects, sacred_geo, overall_fgi, overall_desc, sidereal_fgi, sidereal_desc,
                                               current_planet, resonance_pairs, forecasts)
        print("\nCosmic Reflection:\n-----------------\n" + reflection)

        print("\nGenerating Sidereal Astrological Wheel Plot...")
        plot_astrological_wheel(positions, zodiac_signs, local_time, planetary_hours, current_planet)

        print("\nGenerating Planetary Hours Timeline...")
        plot_planetary_hours(planetary_hours, local_time)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calculate_planetary_positions()
