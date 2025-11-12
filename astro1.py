import ephem
from datetime import datetime
import pytz
from math import degrees

# --- 1. Helper Functions ---

def get_zodiac_sign(longitude):
    """Converts an ecliptic longitude to a zodiac sign name."""
    signs = [("Aries", 0), ("Taurus", 30), ("Gemini", 60), ("Cancer", 90),
             ("Leo", 120), ("Virgo", 150), ("Libra", 180), ("Scorpio", 210),
             ("Sagittarius", 240), ("Capricorn", 270), ("Aquarius", 300), ("Pisces", 330)]
    lon = longitude % 360
    for name, start in signs:
        if start <= lon < start + 30:
            return name, start
    return "Pisces", 330


def get_day_ruler(day_of_week_index):
    """Determines the planetary ruler of the day."""
    rulers = {6: 'Sun', 0: 'Moon', 1: 'Mars', 2: 'Mercury', 3: 'Jupiter', 4: 'Venus', 5: 'Saturn'}
    return rulers.get(day_of_week_index, 'Unknown')


def get_chaldean_hour_ruler(day_ruler, current_hour):
    """Determines the planetary ruler of the current Chaldean hour."""
    hour_rulers = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
    day_ruler_index = hour_rulers.index(day_ruler)
    hour_ruler_index = (day_ruler_index + current_hour) % 7
    return hour_rulers[hour_ruler_index]


# --- 2. Esoteric Data Dictionaries ---

PLANETARY_FREQUENCIES = {
    'Saturn': 147.85, 'Jupiter': 183.58, 'Mars': 144.72, 'Sun': 126.22,
    'Venus': 221.23, 'Mercury': 141.27, 'Moon': 210.42,
    'Uranus': 207.36, 'Neptune': 211.44, 'Pluto': 140.25
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
    'Pluto': {'sephirah': 'Malkuth', 'path': '32nd Path', 'tarot': 'Judgment'}
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
    'Pluto': {'qlipha': 'Oreb Zaraq', 'demon': 'Moloch'}
}


# --- 3. The Celestial Object Class ---

class CelestialObject:
    def __init__(self, name, object_name, duality, octagonal_angle=None):
        self.name = name
        self.object_name = object_name
        self.duality = duality
        self.octagonal_angle = octagonal_angle
        self.zodiac_sign = None
        self.sign_start_long = 0
        self.positive_percent = 0
        self.negative_percent = 0
        self.details = {}

    def update_all(self, observer, current_minute, current_second):
        """Compute planetary data and esoteric correspondences."""
        self.body = getattr(ephem, self.object_name)()
        self.body.compute(observer)

        ecliptic_coords = ephem.Ecliptic(self.body)
        lon = ecliptic_coords.lon
        self.zodiac_sign, self.sign_start_long = get_zodiac_sign(degrees(lon))

        # Symbolic energy balance
        time_progress = (current_second / 60.0) * 100
        transit_progress = ((degrees(lon) - self.sign_start_long) / 30.0) * 100
        self.positive_percent = (time_progress + transit_progress) / 2
        self.negative_percent = 100 - self.positive_percent

        self.frequency = PLANETARY_FREQUENCIES.get(self.object_name, 0)
        self.kabbalistic = KABBALISTIC_DATA.get(self.object_name, {})
        self.qliphothic = QLIPHOTHIC_DATA.get(self.object_name, {})

        self.details = {
            "Ecliptic Longitude": f"{degrees(lon):.2f}°",
            "Ecliptic Latitude": f"{degrees(ecliptic_coords.lat):.2f}°",
            "Right Ascension": f"{self.body.ra}",
            "Declination": f"{self.body.dec}",
            "Constellation": ephem.constellation(self.body)[1],
            "Frequency (Hz)": f"{self.frequency:.2f}",
            "Kabbalistic Sephirah": self.kabbalistic.get('sephirah', 'Unknown'),
            "Qliphothic Realm": self.qliphothic.get('qlipha', 'Unknown'),
        }

        if hasattr(self.body, 'earth_distance'):
            self.details["Distance (AU)"] = f"{self.body.earth_distance:.4f}"
        if hasattr(self.body, 'moon_phase'):
            self.details["Moon Phase"] = f"{self.body.moon_phase:.2f}"

        future_observer = ephem.Observer()
        future_observer.date = observer.date + 1
        future_body = getattr(ephem, self.object_name)()
        future_body.compute(future_observer)
        future_ecliptic = ephem.Ecliptic(future_body)
        speed = degrees(future_ecliptic.lon - lon)
        if speed < 0:
            speed += 360
        self.details["Speed (°/day)"] = f"{speed:.4f}"

    def get_interpretation(self):
        """Textual interpretation of the planetary state."""
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
        return interp

    def __repr__(self):
        pos_title = "Virtue" if self.octagonal_angle is not None else "Positive"
        neg_title = "Sin" if self.octagonal_angle is not None else "Negative"

        report = (f"{'='*60}\n"
                  f"--- {self.name} ({self.object_name}) ---\n"
                  f"  Duality: {self.duality}\n")
        if self.octagonal_angle is not None:
            report += f"  Octagonal Position: {self.octagonal_angle}°\n"
        report += (f"  Energetic Balance: {neg_title}: {self.negative_percent:.1f}% | {pos_title}: {self.positive_percent:.1f}%\n"
                  f"  Current Transit: {self.name} in {self.zodiac_sign}\n"
                  f"  Details:\n")
        for key, value in self.details.items():
            report += f"    - {key}: {value}\n"
        report += f"\n  Esoteric Interpretation:\n    {self.get_interpretation()}\n"
        return report


# --- 4. Main Analysis Function ---

def get_comprehensive_esoteric_analysis(timezone_str=None):
    """Performs the complete esoteric analysis and returns the full report."""
    if timezone_str:
        try:
            local_tz = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
            print(f"Warning: Unknown timezone '{timezone_str}'. Using system local.")
            local_tz = datetime.now().astimezone().tzinfo
    else:
        local_tz = datetime.now().astimezone().tzinfo

    local_now = datetime.now(local_tz)
    current_hour = local_now.hour
    current_minute = local_now.minute
    current_second = local_now.second
    day_of_week_index = local_now.weekday()
    week_of_month = (local_now.day - 1) // 7 + 1

    full_report = (
        f"Local Datetime: {local_now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}\n"
        f"Time Context: Day of Week: {local_now.strftime('%A')} | "
        f"Week of Month: {week_of_month} | Month: {local_now.strftime('%B')}\n"
    )

    day_ruler = get_day_ruler(day_of_week_index)
    hour_ruler = get_chaldean_hour_ruler(day_ruler, current_hour)
    full_report += (
        f"\n--- Esoteric Geometry of the Current Time Cycle ---\n"
        f"Day Ruler: {day_ruler} | Hour Ruler: {hour_ruler}\n"
        f"The energy of the **{day_ruler}** sets the theme for the day, "
        f"while the **{hour_ruler}** governs the immediate 'weather'.\n"
        f"{'='*60}\n"
    )

    utc_now = local_now.astimezone(pytz.UTC)
    observer = ephem.Observer()
    observer.date = utc_now

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

    full_report += "\n### THE CORE OCTAGON: FOUNDATION OF THE SELF ###\n\n"
    for model in core_octagon_model:
        obj = CelestialObject(model["name"], model["object"], model["duality"], model["angle"])
        obj.update_all(observer, current_minute, current_second)
        full_report += str(obj)

    full_report += "\n### THE OUTER RING: TRANSPERSONAL FORCES ###\n\n"
    for model in outer_ring_model:
        obj = CelestialObject(model["name"], model["object"], model["duality"])
        obj.update_all(observer, current_minute, current_second)
        full_report += str(obj)

    # Add the VOID/SPIRIT section only once
    if "### THE VOID / SPIRIT ###" not in full_report:
        full_report += (
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

    return full_report


# --- 5. Entry Point ---

if __name__ == "__main__":
    print(get_comprehensive_esoteric_analysis())
