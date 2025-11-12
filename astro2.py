import ephem
from datetime import datetime, timezone
import pytz
from math import degrees, radians

# --- Helper functions ---

def get_zodiac_sign(longitude):
    signs = [
        ("Aries", 0), ("Taurus", 30), ("Gemini", 60), ("Cancer", 90),
        ("Leo", 120), ("Virgo", 150), ("Libra", 180), ("Scorpio", 210),
        ("Sagittarius", 240), ("Capricorn", 270), ("Aquarius", 300), ("Pisces", 330)
    ]
    lon = longitude % 360
    for name, start in signs:
        if start <= lon < start + 30:
            return name, start
    return "Pisces", 330

def get_constellation(body, observer):
    return ephem.constellation(body)[1]

def get_extra_zodiac_sign(longitude):
    extended_signs = [
        ("Aries", 0, 30), ("Taurus", 30, 60), ("Gemini", 60, 90), ("Cancer", 90, 120),
        ("Leo", 120, 150), ("Virgo", 150, 180), ("Libra", 180, 210), ("Scorpio", 210, 240),
        ("Ophiuchus", 240, 270), ("Sagittarius", 270, 300), ("Capricorn", 300, 330),
        ("Aquarius", 330, 360), ("Pisces", 360, 390), ("Cetus", 390, 420)
    ]
    lon = longitude % 360
    for name, start, end in extended_signs:
        if start <= lon < end:
            return name, start
    return "Pisces", 330

def calculate_aspect(lon1, lon2):
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    # Major aspects
    if abs(diff - 0) < 1:
        return "Conjunction", 0
    elif abs(diff - 60) < 1:
        return "Sextile", 60
    elif abs(diff - 90) < 1:
        return "Square", 90
    elif abs(diff - 120) < 1:
        return "Trine", 120
    elif abs(diff - 180) < 1:
        return "Opposition", 180
    # Minor aspects
    elif abs(diff - 30) < 1:
        return "Semi-sextile", 30
    elif abs(diff - 45) < 1:
        return "Semi-square", 45
    elif abs(diff - 72) < 1:
        return "Quintile", 72
    elif abs(diff - 135) < 1:
        return "Sesquiquadrate", 135
    elif abs(diff - 144) < 1:
        return "Biquintile", 144
    elif abs(diff - 150) < 1:
        return "Quincunx", 150
    return None, diff

def get_day_ruler(day_index):
    rulers = {6: 'Sun', 0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter', 4: 'Venus', 5: 'Saturn'}
    return rulers.get(day_index, 'Unknown')

def get_chaldean_hour_ruler(day_ruler, current_hour):
    hour_rulers = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
    idx = hour_rulers.index(day_ruler)
    return hour_rulers[(idx + current_hour) % 7]

# --- Calculation of Lilith and lunar nodes ---

def calculate_lunar_apogee(observer):
    moon = ephem.Moon(observer)
    moon.compute(observer)
    moon_ecl = ephem.Ecliptic(moon)
    moon_lon = degrees(moon_ecl.lon)
    jd = observer.date
    days_since_epoch = float(jd) - 2451545.0
    mean_apogee_lon = (83.353 + (11.109337 * days_since_epoch / 365.25)) % 360
    
    # Create a fixed body for Lilith
    lilith = ephem.FixedBody()
    lilith._ra = ephem.degrees(radians(mean_apogee_lon))
    lilith._dec = ephem.degrees(0)
    lilith.compute(observer)
    
    return lilith, mean_apogee_lon

def calculate_lunar_nodes(observer):
    moon = ephem.Moon(observer)
    moon.compute(observer)
    moon_ecl = ephem.Ecliptic(moon)
    moon_lon = degrees(moon_ecl.lon)
    jd = observer.date
    days_since_epoch = float(jd) - 2451545.0
    mean_node_lon = (-19.354819 + (19.354819 * days_since_epoch / 365.25) + 125.044) % 360
    
    # Create a fixed body for Rahu (North Node)
    rahu = ephem.FixedBody()
    rahu._ra = ephem.degrees(radians(mean_node_lon))
    rahu._dec = ephem.degrees(0)
    rahu.compute(observer)
    
    ketu_lon = (mean_node_lon + 180) % 360
    # Create a fixed body for Ketu (South Node)
    ketu = ephem.FixedBody()
    ketu._ra = ephem.degrees(radians(ketu_lon))
    ketu._dec = ephem.degrees(0)
    ketu.compute(observer)
    
    return rahu, ketu, mean_node_lon, ketu_lon

# --- Data dictionaries ---

PLANETARY_FREQUENCIES = {
    'Saturn': 147.85, 'Jupiter': 183.58, 'Mars': 144.72, 'Sun': 126.22,
    'Venus': 221.23, 'Mercury': 141.27, 'Moon': 210.42,
    'Uranus': 207.36, 'Neptune': 211.44, 'Pluto': 140.25,
    'Lilith': 188.65, 'Rahu': 165.32, 'Ketu': 175.45
}

KABBALISTIC_DATA = {
    'Saturn': {'sephirah': 'Binah', 'path': '32nd Path', 'tarot': 'The Universe'},
    'Jupiter': {'sephirah': 'Chesed', 'path': '21st Path', 'tarot': 'The Wheel of Fortune'},
    'Mars': {'sephirah': 'Geburah', 'path': '27th Path', 'tarot': 'The Tower'},
    'Sun': {'sephirah': 'Tiphareth', 'path': '30th Path', 'tarot': 'The Sun'},
    'Venus': {'sephirah': 'Netzach', 'path': '24th Path', 'tarot': 'The Empress'},
    'Mercury': {'sephirah': 'Hod', 'path': '12th Path', 'tarot': 'The Magician'},
    'Moon': {'sephirah': 'Yesod', 'path': '13th Path', 'tarot': 'The High Priestess'},
    'Uranus': {'sephirah': 'Daath', 'path': 'Void', 'tarot': 'The Fool'},
    'Neptune': {'sephirah': 'Kether', 'path': '11th Path', 'tarot': 'The Hanged Man'},
    'Pluto': {'sephirah': 'Malkuth', 'path': '32nd Path', 'tarot': 'Judgment'},
    'Lilith': {'sephirah': 'Gamaliel', 'path': '13th Path', 'tarot': 'The High Priestess'},
    'Rahu': {'sephirah': 'Daath', 'path': 'Void', 'tarot': 'The Fool'},
    'Ketu': {'sephirah': 'Yesod', 'path': '13th Path', 'tarot': 'The High Priestess'}
}

QLIPHOTHIC_DATA = {
    'Saturn': {'qlipha': 'Satariel', 'demon': 'Lucifuge'},
    'Jupiter': {'qlipha': "Gha'agsheblah", 'demon': 'Astaroth'},
    'Mars': {'qlipha': 'Golachab', 'demon': 'Samael'},
    'Sun': {'qlipha': 'Thagirion', 'demon': 'Belphegor'},
    'Venus': {'qlipha': 'Harab Serapel', 'demon': 'Baal'},
    'Mercury': {'qlipha': 'Samael', 'demon': 'Adrammelech'},
    'Moon': {'qlipha': 'Gamaliel', 'demon': 'Lilith'},
    'Uranus': {'qlipha': 'Thaumiel', 'demon': 'Satan'},
    'Neptune': {'qlipha': "A'arab Zaraq", 'demon': 'Asmodeus'},
    'Pluto': {'qlipha': 'Oreb Zaraq', 'demon': 'Moloch'},
    'Lilith': {'qlipha': 'Gamaliel', 'demon': 'Lilith'},
    'Rahu': {'qlipha': 'Thaumiel', 'demon': 'Satan'},
    'Ketu': {'qlipha': 'Gamaliel', 'demon': 'Lilith'}
}

PLATONIC_SOLIDS = {
    'Tetrahedron': {'element': 'Fire', 'planet': 'Mars', 'zodiac': 'Aries', 'chakra': 'Solar Plexus'},
    'Cube': {'element': 'Earth', 'planet': 'Saturn', 'zodiac': 'Capricorn', 'chakra': 'Root'},
    'Octahedron': {'element': 'Air', 'planet': 'Mercury', 'zodiac': 'Gemini', 'chakra': 'Heart'},
    'Icosahedron': {'element': 'Water', 'planet': 'Venus', 'zodiac': 'Scorpio', 'chakra': 'Sacral'},
    'Dodecahedron': {'element': 'Aether', 'planet': 'Jupiter', 'zodiac': 'Pisces', 'chakra': 'Crown'}
}

# --- Class for celestial objects ---

class CelestialObject:
    def __init__(self, name, object_name, duality, octagonal_angle=None):
        self.name = name
        self.object_name = object_name
        self.duality = duality
        self.octagonal_angle = octagonal_angle
        self.zodiac_sign = None
        self.extra_zodiac_sign = None
        self.sign_start_long = 0
        self.positive_percent = 0
        self.negative_percent = 0
        self.details = {}
        self.aspects = {}
        self.body = None
        self.mean_apogee_lon = None  # store separately

    def update_all(self, observer, current_minute, current_second):
        """Compute planetary data and esoteric correspondences."""
        if self.object_name == 'Lilith':
            self.body, self.mean_apogee_lon = calculate_lunar_apogee(observer)
        elif self.object_name == 'Rahu':
            self.body, _, _, _ = calculate_lunar_nodes(observer)
        elif self.object_name == 'Ketu':
            _, self.body, _, _ = calculate_lunar_nodes(observer)
        else:
            self.body = getattr(ephem, self.object_name)()
            self.body.compute(observer)

        # Ensure the body is computed before creating Ecliptic
        if self.body:
            ecl = ephem.Ecliptic(self.body)
            lon = degrees(ecl.lon)
            self.zodiac_sign, self.sign_start_long = get_zodiac_sign(lon)
            self.extra_zodiac_sign, _ = get_extra_zodiac_sign(lon)

            # Symbolic energy balance
            time_progress = (current_second / 60) * 100
            transit_progress = ((lon - self.sign_start_long) / 30) * 100
            self.positive_percent = (time_progress + transit_progress) / 2
            self.negative_percent = 100 - self.positive_percent

            # Fetch frequencies and esoteric data
            self.frequency = PLANETARY_FREQUENCIES.get(self.object_name, 0)
            self.kabbalistic = KABBALISTIC_DATA.get(self.object_name, {})
            self.qliphothic = QLIPHOTHIC_DATA.get(self.object_name, {})

            # Compose details
            self.details = {
                "Ecliptic Longitude": f"{lon:.2f}°",
                "Ecliptic Latitude": f"{degrees(ecl.lat):.2f}°",
                "Right Ascension": f"{self.body.ra}",
                "Declination": f"{self.body.dec}",
                "Constellation": get_constellation(self.body, observer),
                "Extended Zodiac": self.extra_zodiac_sign,
                "Frequency (Hz)": f"{self.frequency:.2f}",
                "Kabbalistic Sephirah": self.kabbalistic.get('sephirah', 'Unknown'),
                "Qliphothic Realm": self.qliphothic.get('qlipha', 'Unknown'),
            }
            if hasattr(self.body, 'earth_distance'):
                self.details["Distance (AU)"] = f"{self.body.earth_distance:.4f}"
            if hasattr(self.body, 'moon_phase'):
                self.details["Moon Phase"] = f"{self.body.moon_phase:.2f}"

            # Speed calculation
            future_observer = ephem.Observer()
            future_observer.date = observer.date + 1
            if self.object_name == 'Lilith':
                future_body, _ = calculate_lunar_apogee(future_observer)
            elif self.object_name == 'Rahu':
                future_body, _, _, _ = calculate_lunar_nodes(future_observer)
            elif self.object_name == 'Ketu':
                _, future_body, _, _ = calculate_lunar_nodes(future_observer)
            else:
                future_body = getattr(ephem, self.object_name)()
                future_body.compute(future_observer)
            future_ecl = ephem.Ecliptic(future_body)
            speed = degrees(future_ecl.lon - ecl.lon)
            if speed < 0:
                speed += 360
            self.details["Speed (°/day)"] = f"{speed:.4f}"

    def calculate_aspects(self, all_objects):
        """Calculate aspects with other objects."""
        if not self.body:
            return
        lon = degrees(ephem.Ecliptic(self.body).lon)
        for name, obj in all_objects.items():
            if name != self.name and obj.body:
                other_lon = degrees(ephem.Ecliptic(obj.body).lon)
                aspect, orb = calculate_aspect(lon, other_lon)
                if aspect:
                    self.aspects[name] = {"aspect": aspect, "orb": orb}

    def get_interpretation(self):
        neg, pos = self.duality.split(' vs. ')
        interp = f"The energy of {self.name} in {self.zodiac_sign} currently favors the "
        if self.positive_percent > 60:
            interp += f"**Expression of {pos}** at {self.positive_percent:.1f}%.\n"
            interp += "Lesson: This energy is flowing constructively. Embrace this state to align with your higher purpose."
        elif self.positive_percent < 40:
            interp += f"**Challenge of {neg}** at {self.negative_percent:.1f}%.\n"
            interp += "Lesson: The shadow side is prominent. This is an area for conscious awareness and inner work."
        else:
            interp += f"**Balance between {neg} and {pos}**.\n"
            interp += f"Lesson: You stand at a point of choice. Conscious will is required to tip the scales towards {pos}."
        if self.aspects:
            interp += "\nAspects:\n"
            for other_name, data in self.aspects.items():
                interp += f"- {data['aspect']} with {other_name} (orb: {data['orb']:.2f}°)\n"
        return interp

    def __repr__(self):
        pos_title = "Virtue" if self.octagonal_angle is not None else "Positive"
        neg_title = "Sin" if self.octagonal_angle is not None else "Negative"
        report = f"{'='*60}\n"
        report += f"--- {self.name} ({self.object_name}) ---\n"
        report += f"  Duality: {self.duality}\n"
        if self.octagonal_angle is not None:
            report += f"  Octagonal Position: {self.octagonal_angle}°\n"
        report += (
            f"  Energetic Balance: {neg_title}: {self.negative_percent:.1f}% | {pos_title}: {self.positive_percent:.1f}%\n"
            f"  Current Transit: {self.name} in {self.zodiac_sign}\n"
            f"  Extended Zodiac: {self.name} in {self.extra_zodiac_sign}\n"
            f"  Details:\n"
        )
        for k, v in self.details.items():
            report += f"    - {k}: {v}\n"
        report += f"\n  Esoteric Interpretation:\n    {self.get_interpretation()}\n"
        return report

# --- Main function for comprehensive analysis ---

def get_comprehensive_esoteric_analysis(timezone_str=None):
    if timezone_str:
        try:
            local_tz = pytz.timezone(timezone_str)
        except:
            local_tz = datetime.now().astimezone().tzinfo
    else:
        local_tz = datetime.now().astimezone().tzinfo

    local_now = datetime.now(local_tz)
    current_hour = local_now.hour
    current_minute = local_now.minute
    current_second = local_now.second
    day_index = local_now.weekday()
    week_of_month = (local_now.day - 1) // 7 + 1

    full_report = (
        f"Local Datetime: {local_now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}\n"
        f"Time Context: Day of Week: {local_now.strftime('%A')} | "
        f"Week of Month: {week_of_month} | Month: {local_now.strftime('%B')}\n"
    )

    day_ruler = get_day_ruler(day_index)
    hour_ruler = get_chaldean_hour_ruler(day_ruler, current_hour)
    full_report += (
        f"\n--- Esoteric Geometry of the Current Time Cycle ---\n"
        f"Day Ruler: {day_ruler} | Hour Ruler: {hour_ruler}\n"
        f"The energy of the **{day_ruler}** sets the theme for the day, "
        f"while the **{hour_ruler}** governs the immediate 'weather'.\n"
        f"{'='*60}\n"
    )

    # Fix the deprecated datetime.utcnow() with datetime.now(datetime.UTC)
    utc_now = datetime.now(timezone.utc).astimezone(pytz.UTC)
    observer = ephem.Observer()
    observer.date = utc_now

    # Define objects
    core_octagon_model = [
        {"name": "Foundation", "object": "Saturn", "duality": "Sloth vs. Diligence", "angle": 0},
        {"name": "Expansion", "object": "Jupiter", "duality": "Greed vs. Charity", "angle": 45},
        {"name": "Action", "object": "Mars", "duality": "Wrath vs. Patience", "angle": 90},
        {"name": "Ego", "object": "Sun", "duality": "Pride vs. Humility", "angle": 135},
        {"name": "Desire", "object": "Venus", "duality": "Lust vs. Chastity", "angle": 180},
        {"name": "Mind", "object": "Mercury", "duality": "Envy vs. Kindness", "angle": 225},
        {"name": "Instinct", "object": "Moon", "duality": "Gluttony vs. Temperance", "angle": 270},
    ]
    outer_ring_model = [
        {"name": "The Revolutionary", "object": "Uranus", "duality": "Rebellion vs. Innovation"},
        {"name": "The Mystic", "object": "Neptune", "duality": "Illusion vs. Divine Connection"},
        {"name": "The Alchemist", "object": "Pluto", "duality": "Destruction vs. Transformation"},
    ]
    shadow_nodes_model = [
        {"name": "Dark Moon", "object": "Lilith", "duality": "Rejection vs. Independence"},
        {"name": "North Node", "object": "Rahu", "duality": "Obsession vs. Direction"},
        {"name": "South Node", "object": "Ketu", "duality": "Detachment vs. Release"},
    ]

    # Instantiate all objects
    all_objects = {}
    for m in core_octagon_model + outer_ring_model + shadow_nodes_model:
        obj = CelestialObject(m["name"], m["object"], m["duality"], m.get("angle"))
        all_objects[m["name"]] = obj

    # Update all objects
    for name, obj in all_objects.items():
        obj.update_all(observer, current_minute, current_second)

    # Calculate aspects
    for name, obj in all_objects.items():
        obj.calculate_aspects(all_objects)

    # Compose report
    report = full_report
    report += "\n### THE CORE OCTAGON: FOUNDATION OF THE SELF ###\n\n"
    for m in core_octagon_model:
        report += str(all_objects[m["name"]])
    report += "\n### THE OUTER RING: TRANSPERSONAL FORCES ###\n\n"
    for m in outer_ring_model:
        report += str(all_objects[m["name"]])
    report += "\n### THE SHADOW NODES: KARMIC INFLUENCES ###\n\n"
    for m in shadow_nodes_model:
        report += str(all_objects[m["name"]])

    # Add Platonic solids
    report += "\n### PLATONIC SOLIDS: SACRED GEOMETRY ###\n\n"
    for solid, data in PLATONIC_SOLIDS.items():
        report += (
            f"--- {solid} ---\n"
            f"  Element: {data['element']}\n"
            f"  Planetary Correspondence: {data['planet']}\n"
            f"  Zodiacal Correspondence: {data['zodiac']}\n"
            f"  Chakra Correspondence: {data['chakra']}\n\n"
        )

    # Add the VOID / SPIRIT section
    report += (
        "\n### THE VOID / SPIRIT ###\n"
        "  Represents: The unmanifested potential from which all emerges.\n"
        "  It is the Great Architect's design upon the Trestleboard before the first stone is laid.\n"
        "\n  --- Astrological Correspondences ---\n"
        "    - Planet: Pluto (as the transformer of potential into manifestation)\n"
        "    - Zodiac: Ophiuchus (the serpent bearer, the hidden 13th sign)\n"
        "    - Element: Spirit / Aether\n"
        "    - Tarot: The Fool (0), The Universe (21)\n"
        "    - Masonic Tool: The Unwritten Volume, The Perfect Ashlar in Potential\n"
        "    - Esoteric Meaning: Pure potential, the source of all duality, the silent observer.\n"
        "    - Frequency: 963 Hz (Solfeggio frequency associated with awakening intuition)\n"
        "    - Kabbalistic: Daath (the hidden sephirah of knowledge)\n"
        "    - Qliphothic: Thaumiel (the twin divinities, the realm of opposing forces)\n"
        f"\n  Current Energetic State: This is the canvas upon which the energies of the "
        f"**{day_ruler}** (Day) and **{hour_ruler}** (Hour) are currently painting.\n"
        f"{'='*60}\n"
    )

    return report

# --- Run the analysis ---
if __name__ == "__main__":
    print(get_comprehensive_esoteric_analysis())