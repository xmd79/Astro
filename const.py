import ephem

# Define a function to get the current positions of stars in various constellations
def get_real_time_stars(observer):
    # Define notable stars from various constellations
    stars_data = {
        # Stars from Orion
        'Betelgeuse (Orion)': {'coords': ('05:55:10.305', '+07:24:25.427')},
        'Bellatrix (Orion)': {'coords': ('05:25:07.863', '+06:20:58.956')},
        'Alnilam (Orion)': {'coords': ('05:27:42.025', '-01:12:06.223')},
        'Mintaka (Orion)': {'coords': ('05:32:00.402', '-00:17:56.640')},
        'Alnitak (Orion)': {'coords': ('05:40:45.525', '-01:56:33.900')},
        'Saiph (Orion)': {'coords': ('05:47:45.390', '-09:40:10.500')},
        'Rigel (Orion)': {'coords': ('05:14:32.300', '-08:12:06.900')},
        
        # Stars from Ursa Major
        'Dubhe (Ursa Major)': {'coords': ('11:03:43.96', '+61:45:03.8')},
        'Merak (Ursa Major)': {'coords': ('11:01:50.8', '+53:32:59')},
        'Phecda (Ursa Major)': {'coords': ('13:23:55.946', '+54:55:31.6')},
        'Megrez (Ursa Major)': {'coords': ('13:23:55.26', '+54:56:09.5')},
        'Furud (Ursa Major)': {'coords': ('12:15:16.12', '+54:17:22.5')},
        'Alioth (Ursa Major)': {'coords': ('12:54:23.14', '+54:55:31.1')},
        'Mizar (Ursa Major)': {'coords': ('13:23:55.26', '+54:56:09.5')},
        
        # Stars from Scorpius
        'Antares (Scorpius)': {'coords': ('16:29:24.47', '-26:25:55.31')},
        'Shaula (Scorpius)': {'coords': ('17:24:29.79', '-37:05:36.27')},
        'Sargas (Scorpius)': {'coords': ('17:24:29.79', '-37:05:36.27')},
        
        # Stars from Cassiopeia
        'Shedir (Cassiopeia)': {'coords': ('00:40:28.89', '+57:11:37.70')},
        'Caph (Cassiopeia)': {'coords': ('00:56:00.57', '+59:18:49.49')},
        'Ruchbah (Cassiopeia)': {'coords': ('01:56:26.91', '+60:28:46.73')},
        
        # Stars from Taurus
        'Aldebaran (Taurus)': {'coords': ('04:35:55.27', '+16:50:24.91')},
        'Elnath (Taurus)': {'coords': ('05:26:17.88', '+28:36:27.48')},
        
        # Stars from Gemini
        'Castor (Gemini)': {'coords': ('07:34:36.99', '+31:53:18.29')},
        'Pollux (Gemini)': {'coords': ('07:45:18.42', '+28:01:34.53')},
        
        # Stars from Leo
        'Regulus (Leo)': {'coords': ('10:08:22.26', '+11:58:02.7')},
        
        # Stars from Virgo
        'Spica (Virgo)': {'coords': ('13:25:11.55', '-11:09:40.64')},
        
        # Stars from Sagittarius
        'Kaus Australis (Sagittarius)': {'coords': ('18:24:35.39', '-34:24:18.64')},
        'Kaus Media (Sagittarius)': {'coords': ('18:25:46.53', '-27:22:13.33')},
        'Kaus Borealis (Sagittarius)': {'coords': ('18:23:04.88', '-21:36:56.13')},
        
        # Zodiac Constellations
        # Aries
        'Hamal (Aries)': {'coords': ('02:07:02.73', '+23:27:53.6')},
        # Cancer
        'Acubens (Cancer)': {'coords': ('08:52:47.37', '+8:34:58.25')},
        # Libra
        'Zubenelgenubi (Libra)': {'coords': ('14:15:38.30', '-16:02:58.64')},
        # Capricornus
        'Dabih (Capricornus)': {'coords': ('20:25:31.54', '-14:39:23.8')},
        # Aquarius
        'Sadalmelik (Aquarius)': {'coords': ('22:00:52.87', '-00:29:36.8')},
        # Pisces
        'Fumalsamakah (Pisces)': {'coords': ('23:05:27.96', '+01:58:58.8')},
        
        # Andromeda
        'Alpheratz (Andromeda)': {'coords': ('00:08:25.12', '+29:05:25.50')},
        
        # Perseus
        'Mirfak (Perseus)': {'coords': ('03:11:36.39', '+49:51:38.92')},
        
        # Cygnus
        'Deneb (Cygnus)': {'coords': ('20:41:26.81', '+45:16:49.23')},
        
        # Lyra
        'Vega (Lyra)': {'coords': ('18:36:56.33', '+38:02:00.22')},
        
        # Bootes
        'Arcturus (Bootes)': {'coords': ('14:15:39.67', '+19:10:56.67')},
        
        # Draco
        'Thuban (Draco)': {'coords': ('14:04:22.40', '+54:30:00.0')},
        'Eltanin (Draco)': {'coords': ('17:40:19.31', '+51:20:36.03')},
        'Gamma Draconis (Draco)': {'coords': ('17:10:57.97', '+51:24:19.47')},
        
        # Sirius
        'Sirius (Canis Major)': {'coords': ('06:45:08.917', '-16:42:58.017')},  # Sirius coordinates
        
        # Additional constellations
        # Centaurus
        'Alpha Centauri (Centaurus)': {'coords': ('14:39:36.49', '-60:50:02.36')},
        'Betacca (Centaurus)': {'coords': ('14:36:00.53', '-60:39:55.68')},
        
        # Aquila
        'Altair (Aquila)': {'coords': ('19:50:47.49', '+08:52:06.35')},
        
        # Canis Minor
        'Procyon (Canis Minor)': {'coords': ('07:39:18.12', '+05:13:29.92')},
        
        # Cassiopeia
        'Ruchbah (Cassiopeia)': {'coords': ('01:56:26.91', '+60:28:46.73')},
        
        # Pegasus
        'Markab (Pegasus)': {'coords': ('23:12:43.39', '+15:57:00.70')},
        'Scheat (Pegasus)': {'coords': ('23:03:10.46', '+28:06:58.80')},
        
        # Lyra
        'Lyra (Lyra)': {'coords': ('18:36:56.33', '+38:02:00.22')}
    }

    stars_info = {}
    
    # Calculate the position of each star
    for star_name, info in stars_data.items():
        star = ephem.FixedBody()
        star._ra, star._dec = info['coords']
        star.compute(observer)

        # Determine visibility
        visibility_status = "Visible" if star.alt > 0 else "Below Horizon"

        stars_info[star_name] = {
            'altitude': star.alt,
            'azimuth': star.az,
            'magnitude': star.mag if hasattr(star, 'mag') else 'N/A',
            'distance': 'N/A',  # Distance information would require additional data
            'status': visibility_status
        }

    return stars_info

# Set up the observer with Timisoara, Romania coordinates
def setup_observer():
    observer = ephem.Observer()
    observer.lat = '45.7489'  # Timisoara, Romania latitude
    observer.lon = '21.2087'  # Timisoara, Romania longitude
    observer.elevation = 95   # Elevation in meters
    observer.date = ephem.now()  # Current UTC time
    return observer

# Display the star information
def display_stars_info(stars_info):
    print("Notable Stars Position and Information:")
    print("{:<30} {:<10} {:<10} {:<10} {:<15}".format("Star Name", "Altitude", "Azimuth", "Magnitude", "Status"))
    print("-" * 80)
    for star_name, info in stars_info.items():
        print("{:<30} {:<10.2f} {:<10.2f} {:<10} {:<15}".format(
            star_name,
            info['altitude'] * 180.0 / 3.14159,  # Convert from radians to degrees
            info['azimuth'] * 180.0 / 3.14159,
            info['magnitude'],
            info['status']
        ))

# Main function
def main():
    observer = setup_observer()
    stars_info = get_real_time_stars(observer)
    display_stars_info(stars_info)

if __name__ == "__main__":
    main()