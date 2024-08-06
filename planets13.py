import ephem
import datetime
import pytz
import math
from astroquery.jplhorizons import Horizons
from astropy.time import Time

def get_moon_phase_momentum(current_time):
    tz = pytz.timezone('Etc/GMT-3')
    current_time = tz.normalize(current_time.astimezone(tz))
    current_date = current_time.date()

    moon = ephem.Moon(current_date)
    moon_phase = moon.phase

    previous_new_moon = ephem.previous_new_moon(current_date)
    previous_new_moon_datetime = ephem.Date(previous_new_moon).datetime()
    previous_new_moon_datetime = previous_new_moon_datetime.replace(tzinfo=pytz.timezone('Etc/GMT-3'))
    moon_age = (current_time - previous_new_moon_datetime).days

    moon.compute(current_time)
    moon_sign = ephem.constellation(moon)[1]

    moon_ra = moon.ra
    moon_dec = moon.dec
    moon_distance_km = moon.earth_distance * ephem.meters_per_au / 1000
    moon_angular_diameter = math.degrees(moon.size / moon_distance_km)
    moon_speed_km_hr = moon_distance_km / (1 / 24)
    moon_energy = (moon_phase / 100) ** 2

    map_data = get_astro_map_data(current_time)

    moon_data = {
        'moon_phase': moon_phase,
        'moon_age': moon_age,
        'moon_sign': moon_sign,
        'moon_ra': moon_ra,
        'moon_dec': moon_dec,
        'moon_distance_km': moon_distance_km,
        'moon_angular_diameter': moon_angular_diameter,
        'moon_speed_km_hr': moon_speed_km_hr,
        'moon_energy': moon_energy,
        'astro_map': map_data
    }

    return moon_data

def get_astro_map_data(current_time):
    tz = pytz.timezone('Etc/GMT-3')
    current_time = tz.normalize(current_time.astimezone(tz))

    obs = ephem.Observer()
    obs.lon = '-118.248405'
    obs.lat = '34.052187'
    obs.date = current_time
    obs.pressure = 0
    obs.horizon = '-0:34'

    sun = ephem.Sun(obs)
    moon = ephem.Moon(obs)
    sun.compute(obs)
    moon.compute(obs)

    north_node = ephem.FixedBody()
    north_node._ra = ephem.degrees('18:00:00')
    north_node._dec = ephem.degrees('+5:00:00')
    north_node.compute(obs)
    north_node_sign = ephem.constellation(north_node)[1]

    ascendant = ephem.FixedBody()
    ascendant._ra = ephem.degrees('12:00:00')
    ascendant._dec = ephem.degrees('+0:00:00')
    ascendant.compute(obs)
    ascendant_sign = ephem.constellation(ascendant)[1]

    mc = ephem.FixedBody()
    mc._ra = ephem.degrees('6:00:00')
    mc._dec = ephem.degrees('+0:00:00')
    mc.compute(obs)
    mc_sign = ephem.constellation(mc)[1]

    astro_map_data = {
        'ascendant': ascendant_sign,
        'midheaven': mc_sign,
        'sun': {
            'sign': ephem.constellation(sun)[1],
            'degree': math.degrees(sun.ra)
        },
        'moon': {
            'sign': ephem.constellation(moon)[1],
            'degree': math.degrees(moon.ra)
        },
        'north_node': north_node_sign
    }

    return astro_map_data

def get_planet_data(current_time, planet_name):
    tz = pytz.timezone('Etc/GMT-3')
    current_time = tz.normalize(current_time.astimezone(tz))

    planet = getattr(ephem, planet_name)()
    planet.compute(current_time)

    planet_ra = planet.ra
    planet_dec = planet.dec
    planet_distance_km = planet.earth_distance * ephem.meters_per_au / 1000
    planet_angular_diameter = math.degrees(planet.size / planet_distance_km)
    planet_speed_km_hr = planet_distance_km / (1 / 24)
    planet_energy = planet.elong
    planet_sign = ephem.constellation(planet)[1]
    cycle_progress = calculate_cycle_progress(planet_ra, get_orbit_period(planet_name))
    is_below_45_degrees = planet_dec < math.radians(45)  # Check if below 45 degrees
    
    # Additional specifications for each planet
    planet_specifications = get_planet_specifications(planet_name)

    planet_data = {
        'name': planet_name,
        'ra': planet_ra,
        'dec': planet_dec,
        'distance_km': planet_distance_km,
        'angular_diameter': planet_angular_diameter,
        'speed_km_hr': planet_speed_km_hr,
        'energy': planet_energy,
        'sign': planet_sign,
        'cycle_progress': cycle_progress,
        'is_below_45_deg': is_below_45_degrees,
        **planet_specifications  # Include specifications
    }

    return planet_data

def get_orbit_period(planet_name):
    orbit_periods = {
        'Mercury': 88,
        'Venus': 225,
        'Earth': 365.25,
        'Mars': 687,
        'Jupiter': 4333,
        'Saturn': 10759,
        'Uranus': 30687,
        'Neptune': 60190,
        'Pluto': 90560,
        'Sun': 365.25,
        'Moon': 27.32,
    }
    return orbit_periods.get(planet_name, None)

def calculate_cycle_progress(current_position, orbit_period):
    percentage = (current_position / (2 * math.pi) * 100) % 100  # Normalize within 0-100%
    return percentage

def get_all_planet_data(current_time):
    planets = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Sun', 'Moon']
    all_planet_data = {}

    for planet in planets:
        all_planet_data[planet] = get_planet_data(current_time, planet)

    return all_planet_data

def get_vedic_houses(date, observer, planet_data):
    date_ephem = ephem.Date(date)

    obs = ephem.Observer()
    obs.lon = str(observer['longitude'])
    obs.lat = str(observer['latitude'])
    obs.date = date_ephem

    sidereal_time = float(obs.sidereal_time())
    asc_deg = obs.radec_of(date_ephem, 0)[0] * 180 / ephem.pi  # Ascendant in degrees
    mc_deg = (sidereal_time - asc_deg + 180) % 360  # Midheaven

    house_cusps = []
    for i in range(1, 13):
        cusp_deg = (i * 30 - asc_deg) % 360
        cusp_sign = get_vedic_sign(cusp_deg)
        house_cusps.append((i, cusp_sign))

    house_cusps_dict = {house: sign for house, sign in house_cusps}

    # Determine current planet positions relative to the houses
    planets_in_houses = {i: [] for i in range(1, 13)}
    for planet in planet_data.values():
        planet_deg = (math.degrees(planet['ra']) + 360) % 360  # Normalize to 0-360
        house_number = (planet_deg // 30 + 1) % 12  # Calculate which house
        if house_number == 0:
            house_number = 12  # Adjust for 12th house index
        planets_in_houses[house_number].append(planet['name'])

    house_cusps_dict['planets'] = planets_in_houses

    return house_cusps_dict

def get_vedic_sign(deg):
    deg = (deg + 360) % 360
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    return signs[int(deg // 30)]

def get_star_positions(date, observer):
    obs = ephem.Observer()
    obs.lon = str(observer['longitude'])
    obs.lat = str(observer['latitude'])
    obs.date = ephem.Date(date)

    star_positions = []
    for star in stars:
        fixed_body = ephem.FixedBody()
        fixed_body._ra = star[1]
        fixed_body._dec = star[2]
        fixed_body.compute(obs)
        ra_deg = math.degrees(fixed_body.ra)
        dec_deg = math.degrees(fixed_body.dec)
        star_positions.append((star[0], ra_deg, dec_deg))

    return star_positions

def get_current_aspects():
    obs = ephem.Observer()
    obs.lon = '21.21621'  # Longitude of Timișoara  
    obs.lat = '45.75415'  # Latitude of Timișoara
    obs.date = ephem.now()

    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
               'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

    aspects = []
    for planet in planets:
        p = getattr(ephem, planet)()
        p.compute(obs)
        for other_planet in planets:
            if other_planet != planet:
                o = getattr(ephem, other_planet)()
                o.compute(obs)
                separation = abs(p.ra - o.ra)
                separation = separation * 180 / ephem.pi  # Convert from radians to degrees
                aspect = check_aspect(separation)
                if aspect:
                    aspects.append({
                        'planet1': planet,
                        'planet2': other_planet,
                        'aspect': aspect,
                        'separation': separation
                    })

    return aspects

def check_aspect(separation_deg):
    aspects = {
        'Conjunction': (0, 10),
        'Sextile': (60, 8),
        'Square': (90, 8),
        'Trine': (120, 8),
        'Opposition': (180, 10),
        'Quincunx': (150, 8),
        'Semi-sextile': (30, 2),
        'Sesquisquare': (135, 2),
        'Semi-square': (45, 2),
        'Biquintile': (144, 2)
    }
    for aspect, (center, orb) in aspects.items():
        if abs(separation_deg - center) <= orb:
            return aspect
    return None

def get_planet_specifications(planet_name):
    specifications = {
        'Mercury': {
            'Kepler\'s Law': 'Mercury has the shortest orbital period of all the planets, completing its orbit in about 88 Earth days.',
            'Semi-major Axis (AU)': 0.387,
            'Eccentricity': 0.2056,
            'Inclination (degrees)': 7.0
        },
        'Venus': {
            'Kepler\'s Law': 'Venus has a bright, reflective atmosphere with the longest rotational period of any planet, taking about 243 Earth days to rotate once.',
            'Semi-major Axis (AU)': 0.723,
            'Eccentricity': 0.0068,
            'Inclination (degrees)': 3.39
        },
        'Earth': {
            'Kepler\'s Law': 'Earth is the only planet known to support life and orbits the Sun every 365.25 days.',
            'Semi-major Axis (AU)': 1.000,
            'Eccentricity': 0.0167,
            'Inclination (degrees)': 0.0
        },
        'Mars': {
            'Kepler\'s Law': 'Mars has two moons and a day length similar to Earth, taking about 687 Earth days to orbit the Sun.',
            'Semi-major Axis (AU)': 1.524,
            'Eccentricity': 0.0934,
            'Inclination (degrees)': 1.85
        },
        'Jupiter': {
            'Kepler\'s Law': 'Jupiter has the fastest rotation of any planet, completing a rotation in about 10 hours while taking 12 Earth years to orbit the Sun.',
            'Semi-major Axis (AU)': 5.204,
            'Eccentricity': 0.0484,
            'Inclination (degrees)': 1.30
        },
        'Saturn': {
            'Kepler\'s Law': 'Saturn is known for its extensive ring system and takes roughly 29.5 Earth years to complete one orbit around the Sun.',
            'Semi-major Axis (AU)': 9.582,
            'Eccentricity': 0.0565,
            'Inclination (degrees)': 2.49
        },
        'Uranus': {
            'Kepler\'s Law': 'Uranus rotates on its side, with an axial tilt of 98 degrees, taking about 84 Earth years to orbit the Sun.',
            'Semi-major Axis (AU)': 19.218,
            'Eccentricity': 0.0472,
            'Inclination (degrees)': 0.77
        },
        'Neptune': {
            'Kepler\'s Law': 'Neptune has the longest orbital period of all the planets, taking approximately 165 Earth years to complete one orbit.',
            'Semi-major Axis (AU)': 30.068,
            'Eccentricity': 0.0086,
            'Inclination (degrees)': 1.77
        },
        'Pluto': {
            'Kepler\'s Law': 'Pluto has a highly eccentric orbit and takes about 248 Earth years to orbit the Sun.',
            'Semi-major Axis (AU)': 39.482,
            'Eccentricity': 0.2488,
            'Inclination (degrees)': 17.14
        },
        'Sun': {
            'Kepler\'s Law': 'The Sun is the center of our solar system and has its own gravitational pull, influencing the orbits of the planets.',
            'Semi-major Axis (AU)': 0,  # Not applicable
            'Eccentricity': 0,  # Not applicable
            'Inclination (degrees)': 0  # Not applicable
        },
        'Moon': {
            'Kepler\'s Law': 'The Moon orbits the Earth and completes its orbit approximately every 27.3 days.',
            'Semi-major Axis (AU)': 0.00257,  # Average distance from Earth to Moon
            'Eccentricity': 0.0549,  # Eccentricity of the Moon's orbit around Earth
            'Inclination (degrees)': 5.145  # Inclination of the Moon's orbit
        }
    }
    return specifications.get(planet_name, {})

# Define a list of fixed stars with their RA and DEC
stars = [
    ('Sirius', ephem.degrees('6:45:08.9'), ephem.degrees('-16:42:58')),
    ('Betelgeuse', ephem.degrees('5:55:10.3'), ephem.degrees('+7:24:25')),
    ('Rigel', ephem.degrees('5:14:32.3'), ephem.degrees('-8:12:06'))
]

# Example usage
current_time = datetime.datetime.now(pytz.timezone('Etc/GMT-3'))

# Get moon phase and other details
moon_data = get_moon_phase_momentum(current_time)
print("Moon Data:")
print(f"Moon Phase: {moon_data['moon_phase']}")
print(f"Moon Age: {moon_data['moon_age']}")
print(f"Moon Sign: {moon_data['moon_sign']}")
print(f"Moon RA: {moon_data['moon_ra']:.2f}")
print(f"Moon DEC: {moon_data['moon_dec']:.2f}")
print(f"Moon Distance (km): {moon_data['moon_distance_km']:.2f}")
print(f"Moon Angular Diameter: {moon_data['moon_angular_diameter']:.2f}")
print(f"Moon Speed (km/hr): {moon_data['moon_speed_km_hr']:.2f}")
print(f"Moon Energy: {moon_data['moon_energy']:.2f}")
print(f"Astrological Map: {moon_data['astro_map']}")

# Get current planetary data and print their additional details
all_planet_data = get_all_planet_data(current_time)
print("\nCurrent Planetary Data:")
planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
           'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
for planet_name in planets:
    planet_data = all_planet_data[planet_name]
    print(f"{planet_data['name']} Data:")
    print(f"  RA: {planet_data['ra']:.2f}")
    print(f"  DEC: {planet_data['dec']:.2f}")
    print(f"  Distance (km): {planet_data['distance_km']:.2f}")
    print(f"  Speed (km/hr): {planet_data['speed_km_hr']:.2f}")
    print(f"  Energy: {planet_data['energy']:.2f}")
    print(f"  Sign: {planet_data['sign']}")
    print(f"  Cycle Progress: {planet_data['cycle_progress']:.2f}%")
    print(f"  Below 45°: {'Yes' if planet_data['is_below_45_deg'] else 'No'}")

    # Print specific planet details
    for key, value in planet_data.items():
        print(f"  {key}: {value}")
    print("\n")

# Get Vedic houses
observer = {'longitude': '21.21621', 'latitude': '45.75415'}
vedic_houses = get_vedic_houses(current_time, observer, all_planet_data)
print("Vedic Houses:")
for house, sign in vedic_houses.items():
    if house == 'planets':
        print("Planets in Houses:")
        for house_num, planets in sign.items():
            print(f"  House {house_num}: {', '.join(planets) if planets else 'None'}")
    else:
        print(f"House {house}: {sign}")

# Get star positions
star_positions = get_star_positions(current_time, observer)
print("\nStar Positions:")
for star in star_positions:
    print(f"{star[0]} - RA: {star[1]:.2f}, DEC: {star[2]:.2f}")

# Get current aspects
aspects = get_current_aspects()
print("\nCurrent Aspects:")
for aspect in aspects:
    print(f"{aspect['planet1']} - {aspect['planet2']}: {aspect['aspect']} (Separation: {aspect['separation']:.2f}°)")