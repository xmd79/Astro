import ephem
import datetime
import pytz
import math

# Define the 72 angels and demons with corrected syntax
ANGELS_DEMONS = [
    {"angel": "Vehuiah", "demon": "Bael", "start_degree": 0, "end_degree": 5, "zodiac": "Aries", "planet": "Mars", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Jelial", "demon": "Agares", "start_degree": 5, "end_degree": 10, "zodiac": "Aries", "planet": "Mars", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Sitael", "demon": "Vassago", "start_degree": 10, "end_degree": 15, "zodiac": "Aries", "planet": "Mars", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Elemiah", "demon": "Gamigin", "start_degree": 15, "end_degree": 20, "zodiac": "Aries", "planet": "Mars", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Mahasiah", "demon": "Marbas", "start_degree": 20, "end_degree": 25, "zodiac": "Aries", "planet": "Mars", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Lelahel", "demon": "Valefor", "start_degree": 25, "end_degree": 30, "zodiac": "Aries", "planet": "Mars", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Achaiah", "demon": "Amon", "start_degree": 30, "end_degree": 35, "zodiac": "Taurus", "planet": "Venus", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Cahetel", "demon": "Barbatos", "start_degree": 35, "end_degree": 40, "zodiac": "Taurus", "planet": "Venus", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Haziel", "demon": "Paimon", "start_degree": 40, "end_degree": 45, "zodiac": "Taurus", "planet": "Venus", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Aladiah", "demon": "Buer", "start_degree": 45, "end_degree": 50, "zodiac": "Taurus", "planet": "Venus", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Lauviah", "demon": "Gusion", "start_degree": 50, "end_degree": 55, "zodiac": "Taurus", "planet": "Venus", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Hahaiah", "demon": "Sitri", "start_degree": 55, "end_degree": 60, "zodiac": "Taurus", "planet": "Venus", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Iezalel", "demon": "Beleth", "start_degree": 60, "end_degree": 65, "zodiac": "Gemini", "planet": "Mercury", "sephirah": "Binah", "qliphah": "Sathariel"},
    {"angel": "Mebahel", "demon": "Leraje", "start_degree": 65, "end_degree": 70, "zodiac": "Gemini", "planet": "Mercury", "sephirah": "Binah", "qliphah": "Sathariel"},
    {"angel": "Hariel", "demon": "Eligos", "start_degree": 70, "end_degree": 75, "zodiac": "Gemini", "planet": "Mercury", "sephirah": "Binah", "qliphah": "Sathariel"},
    {"angel": "Hekamiah", "demon": "Zepar", "start_degree": 75, "end_degree": 80, "zodiac": "Gemini", "planet": "Mercury", "sephirah": "Binah", "qliphah": "Sathariel"},
    {"angel": "Lauviah", "demon": "Botis", "start_degree": 80, "end_degree": 85, "zodiac": "Gemini", "planet": "Mercury", "sephirah": "Binah", "qliphah": "Sathariel"},
    {"angel": "Caliel", "demon": "Bathin", "start_degree": 85, "end_degree": 90, "zodiac": "Gemini", "planet": "Mercury", "sephirah": "Binah", "qliphah": "Sathariel"},
    {"angel": "Leuviah", "demon": "Saleos", "start_degree": 90, "end_degree": 95, "zodiac": "Cancer", "planet": "Moon", "sephirah": "Chesed", "qliphah": "Gha’agsheblah"},
    {"angel": "Pahaliah", "demon": "Purson", "start_degree": 95, "end_degree": 100, "zodiac": "Cancer", "planet": "Moon", "sephirah": "Chesed", "qliphah": "Gha’agsheblah"},
    {"angel": "Nelkhael", "demon": "Morax", "start_degree": 100, "end_degree": 105, "zodiac": "Cancer", "planet": "Moon", "sephirah": "Chesed", "qliphah": "Gha’agsheblah"},
    {"angel": "Yeiayel", "demon": "Ipos", "start_degree": 105, "end_degree": 110, "zodiac": "Cancer", "planet": "Moon", "sephirah": "Chesed", "qliphah": "Gha’agsheblah"},
    {"angel": "Melahel", "demon": "Aim", "start_degree": 110, "end_degree": 115, "zodiac": "Cancer", "planet": "Moon", "sephirah": "Chesed", "qliphah": "Gha’agsheblah"},
    {"angel": "Haheuiah", "demon": "Naberius", "start_degree": 115, "end_degree": 120, "zodiac": "Cancer", "planet": "Moon", "sephirah": "Chesed", "qliphah": "Gha’agsheblah"},
    {"angel": "Nithael", "demon": "Glasya-Labolas", "start_degree": 120, "end_degree": 125, "zodiac": "Leo", "planet": "Sun", "sephirah": "Geburah", "qliphah": "Golachab"},
    {"angel": "Haaiah", "demon": "Bune", "start_degree": 125, "end_degree": 130, "zodiac": "Leo", "planet": "Sun", "sephirah": "Geburah", "qliphah": "Golachab"},
    {"angel": "Yerathel", "demon": "Ronove", "start_degree": 130, "end_degree": 135, "zodiac": "Leo", "planet": "Sun", "sephirah": "Geburah", "qliphah": "Golachab"},
    {"angel": "Seheiah", "demon": "Berith", "start_degree": 135, "end_degree": 140, "zodiac": "Leo", "planet": "Sun", "sephirah": "Geburah", "qliphah": "Golachab"},
    {"angel": "Reiyel", "demon": "Astaroth", "start_degree": 140, "end_degree": 145, "zodiac": "Leo", "planet": "Sun", "sephirah": "Geburah", "qliphah": "Golachab"},
    {"angel": "Omael", "demon": "Forneus", "start_degree": 145, "end_degree": 150, "zodiac": "Leo", "planet": "Sun", "sephirah": "Geburah", "qliphah": "Golachab"},
    {"angel": "Lecabel", "demon": "Foras", "start_degree": 150, "end_degree": 155, "zodiac": "Virgo", "planet": "Mercury", "sephirah": "Tiphareth", "qliphah": "Thagirion"},
    {"angel": "Vasariah", "demon": "Asmoday", "start_degree": 155, "end_degree": 160, "zodiac": "Virgo", "planet": "Mercury", "sephirah": "Tiphareth", "qliphah": "Thagirion"},
    {"angel": "Yehuiah", "demon": "Gaap", "start_degree": 160, "end_degree": 165, "zodiac": "Virgo", "planet": "Mercury", "sephirah": "Tiphareth", "qliphah": "Thagirion"},
    {"angel": "Lehahiah", "demon": "Furfur", "start_degree": 165, "end_degree": 170, "zodiac": "Virgo", "planet": "Mercury", "sephirah": "Tiphareth", "qliphah": "Thagirion"},
    {"angel": "Chavakiah", "demon": "Marchosias", "start_degree": 170, "end_degree": 175, "zodiac": "Virgo", "planet": "Mercury", "sephirah": "Tiphareth", "qliphah": "Thagirion"},
    {"angel": "Menadel", "demon": "Stolas", "start_degree": 175, "end_degree": 180, "zodiac": "Virgo", "planet": "Mercury", "sephirah": "Tiphareth", "qliphah": "Thagirion"},
    {"angel": "Aniel", "demon": "Phenex", "start_degree": 180, "end_degree": 185, "zodiac": "Libra", "planet": "Venus", "sephirah": "Netzach", "qliphah": "A’arab Zaraq"},
    {"angel": "Haamiah", "demon": "Halphas", "start_degree": 185, "end_degree": 190, "zodiac": "Libra", "planet": "Venus", "sephirah": "Netzach", "qliphah": "A’arab Zaraq"},
    {"angel": "Rehael", "demon": "Malphas", "start_degree": 190, "end_degree": 195, "zodiac": "Libra", "planet": "Venus", "sephirah": "Netzach", "qliphah": "A’arab Zaraq"},
    {"angel": "Ieiazel", "demon": "Raum", "start_degree": 195, "end_degree": 200, "zodiac": "Libra", "planet": "Venus", "sephirah": "Netzach", "qliphah": "A’arab Zaraq"},
    {"angel": "Hahahel", "demon": "Focalor", "start_degree": 200, "end_degree": 205, "zodiac": "Libra", "planet": "Venus", "sephirah": "Netzach", "qliphah": "A’arab Zaraq"},
    {"angel": "Mikael", "demon": "Vepar", "start_degree": 205, "end_degree": 210, "zodiac": "Libra", "planet": "Venus", "sephirah": "Netzach", "qliphah": "A’arab Zaraq"},
    {"angel": "Veuliah", "demon": "Sabnock", "start_degree": 210, "end_degree": 215, "zodiac": "Scorpio", "planet": "Mars", "sephirah": "Hod", "qliphah": "Samael"},
    {"angel": "Yelahiah", "demon": "Shax", "start_degree": 215, "end_degree": 220, "zodiac": "Scorpio", "planet": "Mars", "sephirah": "Hod", "qliphah": "Samael"},
    {"angel": "Sealiah", "demon": "Vine", "start_degree": 220, "end_degree": 225, "zodiac": "Scorpio", "planet": "Mars", "sephirah": "Hod", "qliphah": "Samael"},
    {"angel": "Ariel", "demon": "Bifrons", "start_degree": 225, "end_degree": 230, "zodiac": "Scorpio", "planet": "Mars", "sephirah": "Hod", "qliphah": "Samael"},
    {"angel": "Asaliah", "demon": "Vual", "start_degree": 230, "end_degree": 235, "zodiac": "Scorpio", "planet": "Mars", "sephirah": "Hod", "qliphah": "Samael"},
    {"angel": "Mihael", "demon": "Haagenti", "start_degree": 235, "end_degree": 240, "zodiac": "Scorpio", "planet": "Mars", "sephirah": "Hod", "qliphah": "Samael"},
    {"angel": "Vehuel", "demon": "Crocell", "start_degree": 240, "end_degree": 245, "zodiac": "Sagittarius", "planet": "Jupiter", "sephirah": "Yesod", "qliphah": "Gamaliel"},
    {"angel": "Daniel", "demon": "Furcas", "start_degree": 245, "end_degree": 250, "zodiac": "Sagittarius", "planet": "Jupiter", "sephirah": "Yesod", "qliphah": "Gamaliel"},
    {"angel": "Hahasiah", "demon": "Balam", "start_degree": 250, "end_degree": 255, "zodiac": "Sagittarius", "planet": "Jupiter", "sephirah": "Yesod", "qliphah": "Gamaliel"},
    {"angel": "Imamiah", "demon": "Alloces", "start_degree": 255, "end_degree": 260, "zodiac": "Sagittarius", "planet": "Jupiter", "sephirah": "Yesod", "qliphah": "Gamaliel"},
    {"angel": "Nanael", "demon": "Camio", "start_degree": 260, "end_degree": 265, "zodiac": "Sagittarius", "planet": "Jupiter", "sephirah": "Yesod", "qliphah": "Gamaliel"},
    {"angel": "Nithael", "demon": "Murmur", "start_degree": 265, "end_degree": 270, "zodiac": "Sagittarius", "planet": "Jupiter", "sephirah": "Yesod", "qliphah": "Gamaliel"},
    {"angel": "Mebahiah", "demon": "Orobas", "start_degree": 270, "end_degree": 275, "zodiac": "Capricorn", "planet": "Saturn", "sephirah": "Malkuth", "qliphah": "Lilith"},
    {"angel": "Poiel", "demon": "Gremory", "start_degree": 275, "end_degree": 280, "zodiac": "Capricorn", "planet": "Saturn", "sephirah": "Malkuth", "qliphah": "Lilith"},
    {"angel": "Nemamiah", "demon": "Ose", "start_degree": 280, "end_degree": 285, "zodiac": "Capricorn", "planet": "Saturn", "sephirah": "Malkuth", "qliphah": "Lilith"},
    {"angel": "Yeialel", "demon": "Amy", "start_degree": 285, "end_degree": 290, "zodiac": "Capricorn", "planet": "Saturn", "sephirah": "Malkuth", "qliphah": "Lilith"},
    {"angel": "Harahel", "demon": "Orias", "start_degree": 290, "end_degree": 295, "zodiac": "Capricorn", "planet": "Saturn", "sephirah": "Malkuth", "qliphah": "Lilith"},
    {"angel": "Mitzrael", "demon": "Vapula", "start_degree": 295, "end_degree": 300, "zodiac": "Capricorn", "planet": "Saturn", "sephirah": "Malkuth", "qliphah": "Lilith"},
    {"angel": "Umabel", "demon": "Zagan", "start_degree": 300, "end_degree": 305, "zodiac": "Aquarius", "planet": "Uranus", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Iahhel", "demon": "Volac", "start_degree": 305, "end_degree": 310, "zodiac": "Aquarius", "planet": "Uranus", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Anauel", "demon": "Andras", "start_degree": 310, "end_degree": 315, "zodiac": "Aquarius", "planet": "Uranus", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Mehiel", "demon": "Haures", "start_degree": 315, "end_degree": 320, "zodiac": "Aquarius", "planet": "Uranus", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Damabiah", "demon": "Andrealphus", "start_degree": 320, "end_degree": 325, "zodiac": "Aquarius", "planet": "Uranus", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Manakel", "demon": "Cimejes", "start_degree": 325, "end_degree": 330, "zodiac": "Aquarius", "planet": "Uranus", "sephirah": "Kether", "qliphah": "Thaumiel"},
    {"angel": "Eiael", "demon": "Amducias", "start_degree": 330, "end_degree": 335, "zodiac": "Pisces", "planet": "Neptune", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Habuhiah", "demon": "Belial", "start_degree": 335, "end_degree": 340, "zodiac": "Pisces", "planet": "Neptune", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Rochel", "demon": "Decarabia", "start_degree": 340, "end_degree": 345, "zodiac": "Pisces", "planet": "Neptune", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Jabamiah", "demon": "Seere", "start_degree": 345, "end_degree": 350, "zodiac": "Pisces", "planet": "Neptune", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Haiaiel", "demon": "Dantalion", "start_degree": 350, "end_degree": 355, "zodiac": "Pisces", "planet": "Neptune", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
    {"angel": "Mumiah", "demon": "Andromalius", "start_degree": 355, "end_degree": 360, "zodiac": "Pisces", "planet": "Neptune", "sephirah": "Chokmah", "qliphah": "Ghagiel"},
]

# Planetary bodies
PLANETS = {
    "Sun": ephem.Sun, "Moon": ephem.Moon, "Mercury": ephem.Mercury, "Venus": ephem.Venus,
    "Mars": ephem.Mars, "Jupiter": ephem.Jupiter, "Saturn": ephem.Saturn,
    "Uranus": ephem.Uranus, "Neptune": ephem.Neptune, "Pluto": ephem.Pluto
}

# Exalted planets
EXALTED = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo", "Venus": "Pisces",
    "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra"
}

# Observer setup
def get_observer(date):
    obs = ephem.Observer()
    obs.lat = '37.7749'  # San Francisco (adjust as needed)
    obs.lon = '-122.4194'
    obs.date = date
    obs.elevation = 0
    return obs

# Get zodiac sign
def get_zodiac(ra):
    deg = math.degrees(ra) % 360
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
    else: return "Pisces"

# Get planetary positions with retrograde detection
def get_planetary_positions(obs):
    positions = {}
    for name, planet_class in PLANETS.items():
        planet = planet_class()
        planet.compute(obs)
        ra = float(planet.ra)
        deg = math.degrees(ra) % 360
        # Check retrograde by comparing RA at two times
        obs_future = get_observer(obs.date + 1/24)  # 1 hour later
        planet_future = planet_class()
        planet_future.compute(obs_future)
        retrograde = float(planet_future.ra) < float(planet.ra)
        exalted = get_zodiac(ra) == EXALTED.get(name, "")
        positions[name] = {
            "ra": ra, "dec": float(planet.dec), "zodiac": get_zodiac(ra),
            "degree": deg, "retrograde": retrograde, "exalted": exalted
        }
    return positions

# Get aspects
def get_aspects(positions):
    aspects = {"Conjunction": [], "Opposition": [], "Square": [], "Trine": [], "Sextile": []}
    planet_names = list(positions.keys())
    for i, p1 in enumerate(planet_names):
        for p2 in planet_names[i+1:]:
            angle = abs(positions[p1]["degree"] - positions[p2]["degree"])
            if angle > 180: angle = 360 - angle
            if 0 <= angle <= 10:
                aspects["Conjunction"].append(f"{p1} conjunct {p2} ({angle:.2f}°)")
            elif 170 <= angle <= 190:
                aspects["Opposition"].append(f"{p1} opposite {p2} ({angle:.2f}°)")
            elif 80 <= angle <= 100:
                aspects["Square"].append(f"{p1} square {p2} ({angle:.2f}°)")
            elif 110 <= angle <= 130:
                aspects["Trine"].append(f"{p1} trine {p2} ({angle:.2f}°)")
            elif 50 <= angle <= 70:
                aspects["Sextile"].append(f"{p1} sextile {p2} ({angle:.2f}°)")
    return aspects

# Get active angels and demons
def get_active_entities(positions):
    active = []
    for entity in ANGELS_DEMONS:
        for planet, pos in positions.items():
            if entity["start_degree"] <= pos["degree"] < entity["end_degree"]:
                influence = "Angelic" if pos["exalted"] or pos["zodiac"] in ["Taurus", "Cancer", "Libra", "Pisces"] else "Demonic"
                if pos["retrograde"]: influence = "Demonic"
                active.append({
                    "angel": entity["angel"], "demon": entity["demon"],
                    "planet": planet, "degree": pos["degree"],
                    "zodiac": pos["zodiac"], "influence": influence,
                    "sephirah": entity["sephirah"], "qliphah": entity["qliphah"]
                })
    return active

# Generate forecast
def generate_forecast(start_time, interval, steps):
    forecast = []
    for i in range(steps):
        time = start_time + interval * i
        obs = get_observer(time)
        positions = get_planetary_positions(obs)
        aspects = get_aspects(positions)
        entities = get_active_entities(positions)
        forecast.append({
            "time": time,
            "positions": positions,
            "aspects": aspects,
            "entities": entities
        })
    return forecast

# Format output
def format_output(data, title):
    print(f"\n=== {title} ===")
    pdt_time = data['time'].astimezone(pytz.timezone('America/Los_Angeles'))
    print(f"Time: {pdt_time.strftime('%Y-%m-%d %I:%M %p PDT')}")
    print("\nPlanetary Positions:")
    for planet, pos in data["positions"].items():
        status = []
        if pos["retrograde"]: status.append("Retrograde")
        if pos["exalted"]: status.append("Exalted")
        status_str = f" ({', '.join(status)})" if status else ""
        print(f"{planet}: {pos['zodiac']} {pos['degree']:.2f}°{status_str}")
    print("\nAspects:")
    for aspect_type, aspect_list in data["aspects"].items():
        for aspect in aspect_list:
            print(f"{aspect_type}: {aspect}")
    print("\nActive Angels/Demons:")
    for entity in data["entities"]:
        print(f"Planet: {entity['planet']} | Angel: {entity['angel']} | Demon: {entity['demon']} | "
              f"Influence: {entity['influence']} | Sephirah: {entity['sephirah']} | Qliphah: {entity['qliphah']}")

# Main execution
def main():
    # Base time: April 13, 2025, 02:52 PM PDT
    pdt = pytz.timezone('America/Los_Angeles')
    base_time = pdt.localize(datetime.datetime(2025, 4, 13, 14, 52))
    utc_time = base_time.astimezone(pytz.UTC)

    # Current hour
    obs = get_observer(utc_time)
    positions = get_planetary_positions(obs)
    aspects = get_aspects(positions)
    entities = get_active_entities(positions)
    format_output({
        "time": utc_time,
        "positions": positions,
        "aspects": aspects,
        "entities": entities
    }, "Current Hour")

    # Next hours (until end of April 13)
    hours_left = 24 - base_time.hour - 1
    hourly_forecast = generate_forecast(utc_time, datetime.timedelta(hours=1), hours_left)
    for i, forecast in enumerate(hourly_forecast):
        format_output(forecast, f"Hour {i+1} Forecast")

    # Current day
    format_output({
        "time": utc_time,
        "positions": positions,
        "aspects": aspects,
        "entities": entities
    }, "Current Day (April 13, 2025)")

    # Next days (April 14–19)
    daily_forecast = generate_forecast(utc_time + datetime.timedelta(days=1), datetime.timedelta(days=1), 6)
    for i, forecast in enumerate(daily_forecast):
        format_output(forecast, f"Day {i+1} Forecast (April {14+i})")

    # Current week
    print("\n=== Current Week (April 13–19, 2025) ===")
    print("Key Transit: Mars enters Leo on April 18.")
    format_output({
        "time": utc_time,
        "positions": positions,
        "aspects": aspects,
        "entities": entities
    }, "Week Summary")

    # Next weeks (April 20–30)
    weekly_forecast = generate_forecast(utc_time + datetime.timedelta(days=7), datetime.timedelta(days=7), 2)
    for i, forecast in enumerate(weekly_forecast):
        format_output(forecast, f"Week {i+1} Forecast (April {20+i*7}–{26+i*7})")

    # Current month
    print("\n=== Current Month (April 2025) ===")
    print("Key Events: Venus direct (April 12), Mars enters Leo (April 18).")
    format_output({
        "time": utc_time,
        "positions": positions,
        "aspects": aspects,
        "entities": entities
    }, "Month Summary")

    # Next months (May–December)
    monthly_forecast = generate_forecast(utc_time + datetime.timedelta(days=30), datetime.timedelta(days=30), 8)
    months = ["May", "June", "July", "August", "September", "October", "November", "December"]
    for i, forecast in enumerate(monthly_forecast):
        print(f"\n=== Month Forecast: {months[i]} 2025 ===")
        if months[i] == "May":
            print("Key Event: Saturn enters Aries on May 24.")
        format_output(forecast, f"{months[i]} Summary")

if __name__ == "__main__":
    main()