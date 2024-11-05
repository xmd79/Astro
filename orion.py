import ephem

# Define a function to get the current positions of stars in Orion
def get_real_time_orion_stars(observer):
    # Define stars from Orion with their coordinates (RA, Dec)
    orion_stars = {
        'Betelgeuse': {'coords': ('05:55:10.305', '+07:24:25.427')},
        'Bellatrix': {'coords': ('05:25:07.863', '+06:20:58.956')},
        'Alnilam': {'coords': ('05:27:42.025', '-01:12:06.223')},
        'Mintaka': {'coords': ('05:32:00.402', '-00:17:56.640')},
        'Alnitak': {'coords': ('05:40:45.525', '-01:56:33.900')},
        'Saiph': {'coords': ('05:47:45.390', '-09:40:10.500')},
        'Rigel': {'coords': ('05:14:32.300', '-08:12:06.900')}
    }

    stars_info = {}
    
    # Calculate the position of each star
    for star_name, info in orion_stars.items():
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

# Set up the observer
def setup_observer(latitude, longitude, elevation=0):
    observer = ephem.Observer()
    observer.lat = str(latitude)  # e.g., '34.0522' for Los Angeles
    observer.lon = str(longitude)  # e.g., '-118.2437'
    observer.elevation = elevation  # Elevation in meters
    observer.date = ephem.now()  # Current UTC time
    return observer

# Display the star information
def display_stars_info(stars_info):
    print("Orion Stars Position and Information:")
    print("{:<15} {:<10} {:<10} {:<10} {:<15}".format("Star Name", "Altitude", "Azimuth", "Magnitude", "Status"))
    print("-" * 65)
    for star_name, info in stars_info.items():
        print("{:<15} {:<10.2f} {:<10.2f} {:<10} {:<15}".format(
            star_name,
            info['altitude'] * 180.0 / 3.14159,  # Convert from radians to degrees
            info['azimuth'] * 180.0 / 3.14159,
            info['magnitude'],
            info['status']
        ))

# Main function
def main():
    # Set your observer location (latitude, longitude)
    latitude = 34.0522  # Example: Los Angeles
    longitude = -118.2437

    observer = setup_observer(latitude, longitude)
    orion_stars_info = get_real_time_orion_stars(observer)
    display_stars_info(orion_stars_info)

if __name__ == "__main__":
    main()