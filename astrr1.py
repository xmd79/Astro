import ephem
from datetime import datetime, timedelta
import pytz
import geocoder
from tabulate import tabulate
from datetime import timezone

class EnneagramAstroTable:
    def __init__(self):
        # Define the Enneagram types (1 to 9)
        self.types = list(range(1, 10))
        
        # Define connections between types
        self.connections = {
            1: [4, 7],
            2: [4, 8],
            3: [6, 9],
            4: [1, 2],
            5: [7, 8],
            6: [3, 9],
            7: [1, 5],
            8: [2, 5],
            9: [3, 6]
        }
        
        # Define astrological symbols and their corresponding planets/bodies
        self.symbols = {
            1: "Aries (♈)",      # Associated with Mars
            2: "Virgo (♍)",      # Associated with Mercury
            3: "Scorpio (♏)",    # Associated with Pluto
            4: "Mars (♂)",       # Directly Mars
            5: "Saturn (♄)",     # Directly Saturn
            6: "Sagittarius (♐)",# Associated with Jupiter
            7: "Aquarius (♒)",   # Associated with Uranus
            8: "Pisces (♓)",     # Associated with Neptune
            9: "Capricorn (♑)"   # Associated with Saturn
        }
        
        # Map types to their corresponding ephem celestial bodies
        self.planets = {
            1: ephem.Mars(),     # Aries -> Mars
            2: ephem.Mercury(),  # Virgo -> Mercury
            3: ephem.Pluto(),    # Scorpio -> Pluto
            4: ephem.Mars(),     # Mars -> Mars
            5: ephem.Saturn(),   # Saturn -> Saturn
            6: ephem.Jupiter(),  # Sagittarius -> Jupiter
            7: ephem.Uranus(),   # Aquarius -> Uranus
            8: ephem.Neptune(),  # Pisces -> Neptune
            9: ephem.Saturn()    # Capricorn -> Saturn
        }
        
        # Define basic descriptions for each type
        self.descriptions = {
            1: "The Reformer - Principled, purposeful, self-controlled, perfectionistic.",
            2: "The Helper - Generous, demonstrative, people-pleasing, possessive.",
            3: "The Achiever - Adaptable, excelling, driven, image-conscious.",
            4: "The Individualist - Expressive, dramatic, self-absorbed, temperamental.",
            5: "The Investigator - Perceptive, innovative, secretive, isolated.",
            6: "The Loyalist - Engaging, responsible, anxious, suspicious.",
            7: "The Enthusiast - Spontaneous, versatile, acquisitive, scattered.",
            8: "The Challenger - Self-confident, decisive, willful, confrontational.",
            9: "The Peacemaker - Receptive, reassuring, complacent, resigned."
        }

        # Set up the observer for astronomical calculations
        self.setup_observer()

    def setup_observer(self):
        """Set up the observer with current location and time."""
        # Get current date and time
        self.current_datetime = datetime.now()
        print(f"Current Date and Time: {self.current_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

        # Get approximate location from IP
        g = geocoder.ip('me')
        if g.ok:
            self.latitude, self.longitude = g.latlng
            print(f"Estimated Location - Latitude: {self.latitude}, Longitude: {self.longitude}")
        else:
            print("Could not determine location. Using default coordinates.")
            self.latitude, self.longitude = 0, 0

        # Set up observer
        self.observer = ephem.Observer()
        self.observer.lat = str(self.latitude)
        self.observer.lon = str(self.longitude)
        self.observer.elev = 0
        self.observer.date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    def get_planet_position(self, type_num):
        """Get the current position of the planet associated with the type."""
        if type_num not in self.types:
            return "N/A"
        planet = self.planets[type_num]
        planet.compute(self.observer)
        ra = planet.ra
        dec = planet.dec
        return f"RA: {ra}, Dec: {dec}"

    def get_planet_name(self, type_num):
        """Get the name of the planet associated with the type."""
        if type_num not in self.types:
            return "N/A"
        planet = self.planets[type_num]
        return planet.name

    def generate_astro_table(self):
        """Generate a complete table mapping all Enneagram types to astrological data."""
        table_data = []
        for type_num in self.types:
            row = {
                "Type": type_num,
                "Description": self.descriptions[type_num],
                "Symbol": self.symbols[type_num],
                "Planet": self.get_planet_name(type_num),
                "Position": self.get_planet_position(type_num),
                "Connections": ", ".join(map(str, self.connections[type_num]))
            }
            table_data.append(row)
        
        print("\nEnneagram Astrological Data Table:")
        print(tabulate(table_data, headers="keys", tablefmt="grid"))

def main():
    # Instantiate the Enneagram astrological table
    enneagram = EnneagramAstroTable()
    
    print("\nWelcome to the Enneagram Astrological Data Table Generator!")
    print("This tool provides a complete mapping of Enneagram types to astrological data.")
    
    # Generate and display the table
    enneagram.generate_astro_table()

if __name__ == "__main__":
    main()