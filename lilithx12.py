from datetime import datetime
import math
import ephem
import pytz

# Demon and angelic data (unchanged for brevity)
demons_data = {
    "Bael": {
        "dominant_day": 0,
        "attributes": {
            "description": "King of Hell, appears as a cat, toad, or man.",
            "element": "Fire",
            "planet": "Saturn",
            "constellation": "Capricornus",
            "hierarchy": "King",
            "rank": "High",
            "energy": {
                "type": "Positive",
                "frequency": 432,
                "vibration": "Grounding",
                "intensity": "Strong",
                "power": 80,
                "amplitude": 0.9,
                "phase": 0,
                "phase_shift": 0.1,
                "angular_momentum": 0.75,
                "interference": "Destructive",
                "coherence": "Low",
                "magnetism": "Attractive",
                "electricity": "High Voltage",
                "inertia": "Stable",
                "potential_energy": "High",
                "kinetic_energy": "Moderate",
                "em_field": "Chaotic"
            },
            "qualities": ["Invisibility", "Themes of power"],
            "unique_positive": ["Control", "Influence"],
            "unique_negative": ["Manipulation", "Deceit"],
            "vulnerabilities": ["Humility", "Self-awareness"],
            "masonic_standard": "Wisdom",
            "symbol": "♠",
            "numerology": (1, "Initiation"),
            "esoteric_meaning": "Control over oneself and others.",
            "manifold": "Fiery",
            "orders": "Orders of Power",
            "triad": "The Four Kings",
            "sacred_geometry": "Tetrahedron",
            "astro_sigil": "♑︎",
            "kepler_triangle": (1, 2, math.sqrt(3))
        },
        "angelic_counterpart": "Uriel",
        "past_demon": "Astaroth",
        "future_demon": "Paimon",
    },
    "Agares": {
        "dominant_day": 1,
        "attributes": {
            "description": "Duke of Hell, teaches languages and retrieves runaways.",
            "element": "Water",
            "planet": "Mercury",
            "constellation": "Aquarius",
            "hierarchy": "Duke",
            "rank": "Medium",
            "energy": {
                "type": "Balanced",
                "frequency": 528,
                "vibration": "Flowing",
                "intensity": "Moderate",
                "power": 60,
                "amplitude": 0.7,
                "phase": math.pi / 2,
                "phase_shift": 0.2,
                "angular_momentum": 0.5,
                "interference": "Constructive",
                "coherence": "Medium",
                "magnetism": "Neutral",
                "electricity": "Medium Voltage",
                "inertia": "Dynamic",
                "potential_energy": "Moderate",
                "kinetic_energy": "Moderate",
                "em_field": "Harmonic"
            },
            "qualities": ["Persuasion", "Language"],
            "unique_positive": ["Contentment", "Communication"],
            "unique_negative": ["Confusion", "Misunderstanding"],
            "vulnerabilities": ["Stagnation", "Isolation"],
            "masonic_standard": "Truth",
            "symbol": "♣",
            "numerology": (2, "Duality"),
            "esoteric_meaning": "Power of communication and integration.",
            "manifold": "Fluid",
            "orders": "Orders of Knowledge",
            "triad": "The Judges",
            "sacred_geometry": "Icosahedron",
            "astro_sigil": "♒︎",
            "kepler_triangle": (1, 3, math.sqrt(8))
        },
        "angelic_counterpart": "Mikhail",
        "past_demon": "Bael",
        "future_demon": "Marbas",
    },
    "Paimon": {
        "dominant_day": 2,
        "attributes": {
            "description": "King of Hell, teaches arts and sciences.",
            "element": "Air",
            "planet": "Jupiter",
            "constellation": "Libra",
            "hierarchy": "King",
            "rank": "High",
            "energy": {
                "type": "Positive",
                "frequency": 639,
                "vibration": "Expansive",
                "intensity": "High",
                "power": 90,
                "amplitude": 0.95,
                "phase": math.pi,
                "phase_shift": 0.15,
                "angular_momentum": 0.85,
                "interference": "Constructive",
                "coherence": "High",
                "magnetism": "Attractive",
                "electricity": "High Voltage",
                "inertia": "Light",
                "potential_energy": "High",
                "kinetic_energy": "High",
                "em_field": "Resonant"
            },
            "qualities": ["Knowledge", "Teaching"],
            "unique_positive": ["Mastery", "Wisdom"],
            "unique_negative": ["Overconfidence", "Obsession"],
            "vulnerabilities": ["Doubt", "Ignorance"],
            "masonic_standard": "Knowledge",
            "symbol": "♠",
            "numerology": (3, "Creativity"),
            "esoteric_meaning": "Influence over thought and clarity of ideas.",
            "manifold": "Airy",
            "orders": "Orders of Philosophers",
            "triad": "The Enlightened",
            "sacred_geometry": "Octahedron",
            "astro_sigil": "♎︎",
            "kepler_triangle": (1, 4, math.sqrt(15))
        },
        "angelic_counterpart": "Zophiel",
        "past_demon": "Agares",
        "future_demon": "Asmoday",
    }
}

angelic_data = {
    "Uriel": {
        "description": "Archangel of Wisdom and Illumination.",
        "element": "Earth",
        "planet": "Saturn",
        "constellation": "Taurus",
        "hierarchy": "Archangel",
        "rank": "High",
        "energy": {
            "type": "Positive",
            "frequency": 396,
            "vibration": "Stabilizing",
            "intensity": "Strong",
            "power": 85,
            "amplitude": 0.9,
            "phase": math.pi / 4,
            "phase_shift": -0.1,
            "angular_momentum": 0.8,
            "interference": "Constructive",
            "coherence": "High",
            "magnetism": "Repulsive",
            "electricity": "Stable Current",
            "inertia": "Heavy",
            "potential_energy": "High",
            "kinetic_energy": "Moderate",
            "em_field": "Harmonic"
        },
        "qualities": ["Wisdom", "Protection"],
        "unique_positive": ["Insight", "Stability"],
        "unique_negative": ["Rigidity", "Judgment"],
        "vulnerabilities": ["Chaos", "Disorder"],
        "symbol": "🕯️",
        "numerology": (4, "Foundation"),
        "esoteric_meaning": "Illumination of truth and structure.",
        "sacred_geometry": "Cube",
        "astro_sigil": "♉︎",
        "kepler_triangle": (1, 2, math.sqrt(3))
    },
    "Mikhail": {
        "description": "Archangel of Protection and Justice.",
        "element": "Fire",
        "planet": "Sun",
        "constellation": "Leo",
        "hierarchy": "Archangel",
        "rank": "High",
        "energy": {
            "type": "Positive",
            "frequency": 741,
            "vibration": "Radiant",
            "intensity": "High",
            "power": 95,
            "amplitude": 0.98,
            "phase": 3 * math.pi / 2,
            "phase_shift": -0.2,
            "angular_momentum": 0.9,
            "interference": "Constructive",
            "coherence": "Very High",
            "magnetism": "Attractive",
            "electricity": "High Voltage",
            "inertia": "Light",
            "potential_energy": "High",
            "kinetic_energy": "High",
            "em_field": "Radiant"
        },
        "qualities": ["Justice", "Courage"],
        "unique_positive": ["Leadership", "Purity"],
        "unique_negative": ["Wrath", "Overzealousness"],
        "vulnerabilities": ["Pride", "Arrogance"],
        "symbol": "⚔️",
        "numerology": (1, "Leadership"),
        "esoteric_meaning": "Divine protection and purification.",
        "sacred_geometry": "Tetrahedron",
        "astro_sigil": "♌︎",
        "kepler_triangle": (1, 3, math.sqrt(8))
    },
    "Zophiel": {
        "description": "Angel of Beauty and Intellect.",
        "element": "Air",
        "planet": "Jupiter",
        "constellation": "Sagittarius",
        "hierarchy": "Cherubim",
        "rank": "Medium",
        "energy": {
            "type": "Positive",
            "frequency": 852,
            "vibration": "Elevating",
            "intensity": "High",
            "power": 88,
            "amplitude": 0.92,
            "phase": math.pi,
            "phase_shift": -0.15,
            "angular_momentum": 0.82,
            "interference": "Constructive",
            "coherence": "High",
            "magnetism": "Attractive",
            "electricity": "High Voltage",
            "inertia": "Light",
            "potential_energy": "High",
            "kinetic_energy": "High",
            "em_field": "Resonant"
        },
        "qualities": ["Intellect", "Inspiration"],
        "unique_positive": ["Creativity", "Clarity"],
        "unique_negative": ["Detachment", "Idealism"],
        "vulnerabilities": ["Confusion", "Groundlessness"],
        "symbol": "✨",
        "numerology": (3, "Creativity"),
        "esoteric_meaning": "Elevation of thought and spirit.",
        "sacred_geometry": "Octahedron",
        "astro_sigil": "♐︎",
        "kepler_triangle": (1, 4, math.sqrt(15))
    }
}

PLANETS = {
    "Sun": ephem.Sun, "Moon": ephem.Moon, "Mercury": ephem.Mercury, "Venus": ephem.Venus,
    "Mars": ephem.Mars, "Jupiter": ephem.Jupiter, "Saturn": ephem.Saturn,
    "Uranus": ephem.Uranus, "Neptune": ephem.Neptune, "Pluto": ephem.Pluto
}

def get_goetia_demons():
    return demons_data

def get_angelic_entities():
    return angelic_data

def get_planetary_positions():
    observer = ephem.Observer()
    observer.date = datetime.utcnow()
    observer.lat, observer.lon = '0', '0'  # Equatorial reference
    positions = {}
    for planet_name, planet_class in PLANETS.items():
        planet = planet_class()
        planet.compute(observer)
        positions[planet_name] = {
            "ra": float(planet.ra) * 180 / math.pi,  # Degrees
            "dec": float(planet.dec) * 180 / math.pi,  # Degrees
            "az": float(planet.az) * 180 / math.pi,
            "alt": float(planet.alt) * 180 / math.pi,
            "body": planet  # Store the ephem.Body object for transits
        }
    return positions

def get_planetary_aspects(positions):
    aspects = []
    planet_names = list(positions.keys())
    for i, p1 in enumerate(planet_names):
        for p2 in planet_names[i+1:]:
            angle = abs(positions[p1]["ra"] - positions[p2]["ra"])
            if angle > 180:
                angle = 360 - angle
            if 0 <= angle <= 10:
                aspects.append(f"{p1} conjunct {p2} ({angle:.2f}°)")
            elif 170 <= angle <= 190:
                aspects.append(f"{p1} opposite {p2} ({angle:.2f}°)")
            elif 110 <= angle <= 130:
                aspects.append(f"{p1} trine {p2} ({angle:.2f}°)")
            elif 80 <= angle <= 100:
                aspects.append(f"{p1} square {p2} ({angle:.2f}°)")
    return aspects

def get_planetary_transits(positions):
    transits = []
    for planet, pos in positions.items():
        # Use the pre-computed ephem.Body object directly
        zodiac_sign = ephem.constellation(pos["body"])[1]
        transits.append(f"{planet} in {zodiac_sign}")
    return transits

def align_demons_to_time(demons):
    alignment = {}
    demon_count = len(demons)
    positions = get_planetary_positions()
    for index, (demon, details) in enumerate(demons.items()):
        angle = (2 * math.pi / demon_count) * index
        planet = details["attributes"]["planet"]
        planet_pos = positions.get(planet, {"ra": 0, "dec": 0, "az": 0, "alt": 0, "body": None})
        alignment[demon] = {
            "demon": demon,
            "angle": angle,
            "dominant_day": details["dominant_day"],
            "attributes": details["attributes"],
            "angelic_counterpart": details["angelic_counterpart"],
            "planetary_position": planet_pos
        }
    return alignment

def get_demon_influence_for_now(demons, alignment, angels):
    demon_count = len(demons)
    if demon_count == 0:
        raise ValueError("No demons defined.")

    now = datetime.now(pytz.UTC)
    total_seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    seconds_per_demon = 86400 / demon_count
    current_demon_index = int(total_seconds // seconds_per_demon) % demon_count
    
    current_demon = list(demons.keys())[current_demon_index]
    current_demon_details = alignment[current_demon]
    angelic_entity = angels[current_demon_details["angelic_counterpart"]]
    
    positions = get_planetary_positions()
    aspects = get_planetary_aspects(positions)
    transits = get_planetary_transits(positions)
    
    demon_power = current_demon_details["attributes"]["energy"]["power"]
    angel_power = angelic_entity["energy"]["power"]
    total_energy = demon_power + angel_power
    neg_ratio = demon_power / total_energy
    pos_ratio = angel_power / total_energy
    
    most_negative = max(demons.items(), key=lambda x: x[1]["attributes"]["energy"]["power"])[0]
    most_positive = max(angels.items(), key=lambda x: x[1]["energy"]["power"])[0]
    
    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "current_demon": current_demon,
        "demon_details": current_demon_details,
        "angelic_entity": angelic_entity,
        "planetary_aspects": aspects,
        "planetary_transits": transits,
        "all_planetary_positions": positions,
        "negativity_ratio": neg_ratio,
        "positivity_ratio": pos_ratio,
        "most_negative_reversal": most_negative,
        "most_positive_reversal": most_positive
    }

def print_influence(info):
    print(f"--- Current Influence Analysis ---")
    print(f"Current Time: {info['current_time']}")
    
    print("\n=== Demonic Influence ===")
    print(f"Current Demon: {info['current_demon']}")
    print(f"Angle on Unit Circle: {info['demon_details']['angle']:.2f} radians (~{info['demon_details']['angle']*180/math.pi:.2f}°)")
    attrs = info["demon_details"]["attributes"]
    print(f"Description: {attrs['description']}")
    print(f"Element: {attrs['element']}")
    print(f"Planet: {attrs['planet']}")
    print(f"Constellation: {attrs['constellation']}")
    print(f"Manifold: {attrs['manifold']}")
    print(f"Hierarchy: {attrs['hierarchy']}")
    print(f"Rank: {attrs['rank']}")
    print(f"Sacred Geometry: {attrs['sacred_geometry']}")
    print(f"Astro Sigil: {attrs['astro_sigil']}")
    print(f"Kepler Triangle: {attrs['kepler_triangle']}")
    
    energy = attrs["energy"]
    print("\nDemon Energy Profile:")
    for key, value in energy.items():
        print(f"  {key.capitalize()}: {value}")
    
    print(f"Qualities: {', '.join(attrs['qualities'])}")
    print(f"Unique Positive: {', '.join(attrs['unique_positive'])}")
    print(f"Unique Negative: {', '.join(attrs['unique_negative'])}")
    print(f"Vulnerabilities: {', '.join(attrs['vulnerabilities'])}")
    print(f"Symbol: {attrs['symbol']}")
    print(f"Numerology: {attrs['numerology'][0]} - {attrs['numerology'][1]}")
    print(f"Esoteric Meaning: {attrs['esoteric_meaning']}")
    
    print("\n=== Angelic Counterforce ===")
    angel = info["angelic_entity"]
    print(f"Counterpart: {info['demon_details']['angelic_counterpart']}")
    print(f"Description: {angel['description']}")
    print(f"Element: {angel['element']}")
    print(f"Planet: {angel['planet']}")
    print(f"Constellation: {angel['constellation']}")
    print(f"Hierarchy: {angel['hierarchy']}")
    print(f"Rank: {angel['rank']}")
    print(f"Sacred Geometry: {angel['sacred_geometry']}")
    print(f"Astro Sigil: {angel['astro_sigil']}")
    print(f"Kepler Triangle: {angel['kepler_triangle']}")
    
    print("\nAngel Energy Profile:")
    for key, value in angel["energy"].items():
        print(f"  {key.capitalize()}: {value}")
    
    print(f"Qualities: {', '.join(angel['qualities'])}")
    print(f"Unique Positive: {', '.join(angel['unique_positive'])}")
    print(f"Unique Negative: {', '.join(angel['unique_negative'])}")
    print(f"Vulnerabilities: {', '.join(angel['vulnerabilities'])}")
    print(f"Symbol: {angel['symbol']}")
    print(f"Numerology: {angel['numerology'][0]} - {angel['numerology'][1]}")
    print(f"Esoteric Meaning: {angel['esoteric_meaning']}")
    
    print("\n=== Celestial Context ===")
    print("Planetary Transits:")
    for transit in info["planetary_transits"]:
        print(f"  {transit}")
    print("\nPlanetary Aspects:")
    for aspect in info["planetary_aspects"]:
        print(f"  {aspect}")
    print("\nAll Planetary Positions:")
    for planet, data in info["all_planetary_positions"].items():
        print(f"  {planet}: RA {data['ra']:.2f}°, Dec {data['dec']:.2f}°, Az {data['az']:.2f}°, Alt {data['alt']:.2f}°")
    
    print("\n=== Energy Balance ===")
    print(f"Negativity Ratio: {info['negativity_ratio']:.2f}")
    print(f"Positivity Ratio: {info['positivity_ratio']:.2f}")
    print(f"Most Negative Reversal: {info['most_negative_reversal']} (Demon)")
    print(f"Most Positive Reversal: {info['most_positive_reversal']} (Angel)")

if __name__ == "__main__":
    demons = get_goetia_demons()
    angels = get_angelic_entities()
    alignment = align_demons_to_time(demons)
    
    try:
        influence_info = get_demon_influence_for_now(demons, alignment, angels)
        print_influence(influence_info)
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")