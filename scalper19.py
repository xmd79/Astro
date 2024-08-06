#!/usr/bin/env python3

import requests
import numpy as np
import talib
import ephem
import pytz
import datetime
import math
import time
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException
from colorama import init, Fore, Style
from scipy.stats import linregress

# Load credentials from file
with open("credentials.txt", "r") as f:
    api_key = f.readline().strip()
    api_secret = f.readline().strip()

# Instantiate Binance client
client = BinanceClient(api_key, api_secret)

# Initialize colorama
init(autoreset=True)

symbol = "BTCUSDC"
timeframes = ["5m", "1m"]
candle_map = {}

# Define a function to get candles
def get_candles(symbol, timeframe, limit=1000):
    try:
        klines = client.get_klines(symbol=symbol, interval=timeframe, limit=limit)
        return [{
            "time": k[0] / 1000,
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        } for k in klines]
    except BinanceAPIException as e:
        print(f"Error fetching candles for {symbol} at {timeframe}: {e}")
        return []

def get_moon_phase_momentum():
    tz = pytz.timezone('Etc/GMT-3')
    current_time = datetime.datetime.now(tz)
    moon = ephem.Moon(current_time)
    moon_phase = moon.phase

    previous_new_moon = ephem.previous_new_moon(current_time)
    previous_new_moon_datetime = ephem.Date(previous_new_moon).datetime()
    moon_age = (current_time - previous_new_moon_datetime.replace(tzinfo=tz)).days
    
    moon.compute(current_time)
    moon_sign = ephem.constellation(moon)[1]

    return {
        'moon_phase': moon_phase,
        'moon_age': moon_age,
        'moon_sign': moon_sign
    }

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
                separation = abs(p.ra - o.ra) * 180 / ephem.pi  # Convert radians to degrees
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
    }
    for aspect, (center, orb) in aspects.items():
        if abs(separation_deg - center) <= orb:
            return aspect
    return None

def calculate_house_positions():
    current_time = ephem.now()
    obs = ephem.Observer()
    obs.date = current_time

    houses = {}
    for i in range(12):
        # Each house is associated with 30 degrees in the zodiac
        house_start = i * 30  # Start of each house in degrees
        house_end = house_start + 30  # End of the house

        # For each planet, check which house it falls into
        for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 
                            'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
            planet = getattr(ephem, planet_name)()
            planet.compute(obs)
            planet_longitude = math.degrees(planet.ra) % 360  # Convert radians to degrees and normalize

            if house_start <= planet_longitude < house_end:
                houses[f'House {i + 1}'] = {
                    'planet': planet_name,
                    'zodiac_sign': ephem.constellation(planet)[1]
                }
                break
        else:
            houses[f'House {i + 1}'] = {'planet': None, 'zodiac_sign': None}  # No planet in the house

    return houses

def print_house_positions():
    houses = calculate_house_positions()
    print("\nVedic Houses and their Corresponding Planets and Zodiac Signs:")
    for house, data in houses.items():
        if data['planet']:
            print(f"{house}: Planet - {data['planet']}, Sign - {data['zodiac_sign']}")
        else:
            print(f"{house}: No planet present.")

def evaluate_market_mood(aspects):
    mood_signals = {
        'Bullish': 0,
        'Bearish': 0,
    }

    for aspect in aspects:
        if aspect['aspect'] in ['Conjunction', 'Trine']:
            mood_signals['Bullish'] += 1
        elif aspect['aspect'] in ['Square', 'Opposition']:
            mood_signals['Bearish'] += 1

    return mood_signals

def generate_report(timeframe, candles, astro_moon_data):
    print(f"\nTimeframe: {timeframe}")

    # Current close price
    current_close = candles[-1]["close"]
    print(f"Current Close Price: {current_close:.2f}")

    # Technical indicators
    rsi = talib.RSI(np.array([c["close"] for c in candles]), timeperiod=14)[-1]
    ema_50 = talib.EMA(np.array([c["close"] for c in candles]), timeperiod=50)[-1]
    ema_200 = talib.EMA(np.array([c["close"] for c in candles]), timeperiod=200)[-1]

    print(f"RSI: {rsi:.2f}")
    print(f"50-period EMA: {ema_50:.2f}")
    print(f"200-period EMA: {ema_200:.2f}")

    # Determine market status based on EMAs
    if current_close > ema_50 and current_close > ema_200:
        print(f"{Fore.GREEN}Market is in an Uptrend{Style.RESET_ALL}")
    elif current_close < ema_50 and current_close < ema_200:
        print(f"{Fore.RED}Market is in a Downtrend{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Market is in a Consolidation Phase{Style.RESET_ALL}")

    # Astrological Data
    aspects = get_current_aspects()
    mood_signals = evaluate_market_mood(aspects)
    
    bullish_aspects = mood_signals['Bullish']
    bearish_aspects = mood_signals['Bearish']

    print(f"\nMarket Mood based on Astrology: {'Bullish' if bullish_aspects > bearish_aspects else 'Bearish' if bearish_aspects > bullish_aspects else 'Neutral'}\n")

    print("Astrological Aspects:")
    for aspect in aspects:
        print(f"{aspect['planet1']} {aspect['aspect']} {aspect['planet2']} (Separation: {aspect['separation']:.2f})")
        if aspect['aspect'] in ['Conjunction', 'Trine']:
            print(f" - This aspect is considered Bullish: {aspect['planet1']} and {aspect['planet2']} are in a favorable alignment.")
        elif aspect['aspect'] in ['Square', 'Opposition']:
            print(f" - This aspect is considered Bearish: {aspect['planet1']} and {aspect['planet2']} are in a challenging alignment.")

    # Determining dominant mood based on bullish and bearish aspects
    if bullish_aspects > bearish_aspects:
        print(f"{Fore.GREEN}Overall Astro Signal: Bullish Mood indicated, with {bullish_aspects} positive aspects outperforming {bearish_aspects} negative ones.{Style.RESET_ALL}")
    elif bearish_aspects > bullish_aspects:
        print(f"{Fore.RED}Overall Astro Signal: Bearish Mood indicated, with {bearish_aspects} negative aspects outnumbering {bullish_aspects} positive ones.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Overall Astro Signal: Neutral Mood indicated, with equal positive and negative influences.{Style.RESET_ALL}")

    # Moon Data
    print("\nAstrological Data:")
    print(f"Moon Phase: {astro_moon_data['moon_phase']:.2f}")
    print(f"Moon Age: {astro_moon_data['moon_age']} days")
    print(f"Moon Sign: {astro_moon_data['moon_sign']}")

# The main loop for continuous analysis
if __name__ == "__main__":
    while True:
        candle_map.clear()  # Clear old data

        # Fetch candles for all timeframes
        for timeframe in timeframes:
            candle_map[timeframe] = get_candles(symbol, timeframe)

        # Get astrological data
        astro_moon_data = get_moon_phase_momentum()

        # Analyze timeframes
        for timeframe in timeframes:
            candles = candle_map[timeframe]

            if len(candles) > 0:
                generate_report(timeframe, candles, astro_moon_data)
                print_house_positions()  # Print House Info
                print()  # Add a newline for better separation of timeframes.

        time.sleep(5)  # Wait for 5 seconds before the next iteration