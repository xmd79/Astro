import ephem
import pandas as pd
import numpy as np
from itertools import combinations
from datetime import datetime, timedelta

# List of celestial objects
celestial_objects = {
    'Sun': ephem.Sun(),
    'Moon': ephem.Moon(),
    'Mercury': ephem.Mercury(),
    'Venus': ephem.Venus(),
    'Mars': ephem.Mars(),
    'Jupiter': ephem.Jupiter(),
    'Saturn': ephem.Saturn(),
    'Uranus': ephem.Uranus(),
    'Neptune': ephem.Neptune(),
    'Pluto': ephem.Pluto()
}

# Zodiac sign boundaries in degrees
zodiac_bounds = [
    (0, 'Aries'), (30, 'Taurus'), (60, 'Gemini'), (90, 'Cancer'),
    (120, 'Leo'), (150, 'Virgo'), (180, 'Libra'), (210, 'Scorpio'),
    (240, 'Sagittarius'), (270, 'Capricorn'), (300, 'Aquarius'), (330, 'Pisces'), (360, 'Aries')
]

def get_zodiac_sign(longitude):
    """Determine the zodiac sign based on the ecliptic longitude."""
    for i in range(len(zodiac_bounds) - 1):
        if zodiac_bounds[i][0] <= longitude < zodiac_bounds[i + 1][0]:
            return zodiac_bounds[i][1]
    return None

def get_planetary_positions(date):
    """Get the positions of celestial bodies for a given date."""
    observer = ephem.Observer()
    observer.date = date
    positions = {}
    
    for name, body in celestial_objects.items():
        body.compute(observer)
        longitude = body.hlon * 180 / np.pi  # Convert from radians to degrees
        positions[name] = {
            'longitude': longitude,
            'zodiac': get_zodiac_sign(longitude),
        }
    
    return positions

def calculate_aspect(angle1, angle2):
    """Calculate the absolute angle between two celestial bodies."""
    return abs(angle1 - angle2) % 360

def classify_aspects(positions):
    """Identify major and minor aspects based on angular differences."""
    aspects = {}
    body_keys = list(positions.keys())
    
    for i in range(len(body_keys)):
        for j in range(i + 1, len(body_keys)):
            body1 = body_keys[i]
            body2 = body_keys[j]
            angle_diff = calculate_aspect(positions[body1]['longitude'], positions[body2]['longitude'])
            
            # Classify major aspects
            if angle_diff < 8:  # Conjunction
                aspects[(body1, body2)] = "Conjunction"
            elif 172 < angle_diff < 188:  # Opposition
                aspects[(body1, body2)] = "Opposition"
            elif 82 < angle_diff < 98:  # Square
                aspects[(body1, body2)] = "Square"
            elif 112 < angle_diff < 128:  # Trine
                aspects[(body1, body2)] = "Trine"
            elif 52 < angle_diff < 68:  # Sextile
                aspects[(body1, body2)] = "Sextile"
                
            # Classify minor aspects
            if 40 < angle_diff < 50:  # Semi-square
                aspects[(body1, body2)] = "Semi-square"
            elif 130 < angle_diff < 140:  # Sesquiquadrate
                aspects[(body1, body2)] = "Sesquiquadrate"
            elif 70 < angle_diff < 80:  # Quintile
                aspects[(body1, body2)] = "Quintile"
            elif 144 < angle_diff < 154:  # Biquintile
                aspects[(body1, body2)] = "Biquintile"
            elif 50 < angle_diff < 55:  # Septile
                aspects[(body1, body2)] = "Septile"
    
    return aspects

def calculate_cycle_percentages(positions):
    """Calculate the current cycle percentage for each celestial object."""
    cycle_lengths = {
        'Sun': 365.25, 
        'Moon': 29.53, 
        'Mercury': 87.97, 
        'Venus': 224.70, 
        'Mars': 686.98, 
        'Jupiter': 4333.0, 
        'Saturn': 10759.22, 
        'Uranus': 30688.5, 
        'Neptune': 60182.0, 
        'Pluto': 90560.0  
    }
    
    percentages = {}
    for body, data in positions.items():
        current_long = data['longitude']
        percentage = (current_long / 360) * 100
        percentages[body] = {
            'current_position': current_long,
            'cycle_percentage': percentage,
            'cycle_length_days': cycle_lengths[body],
        }
    
    return percentages

def get_datetime_info():
    """Generate current date and output for various celestial bodies."""
    current_date = datetime.now()

    # Get planetary positions for today
    positions = get_planetary_positions(current_date)

    # Calculate aspects
    aspects = classify_aspects(positions)

    # Calculate cycle percentages
    cycle_percentages = calculate_cycle_percentages(positions)

    # Get the data in a structured format
    status_and_dates = {
        'date': current_date,
        'positions': positions,
        'aspects': aspects,
        'cycle_percentages': cycle_percentages
    }

    return status_and_dates

def categorize_aspects(aspects):
    """Categorizes aspects into predictive signals using positive and negative energy."""
    positive_energy_aspects = {"Conjunction", "Trine", "Sextile"}
    negative_energy_aspects = {"Opposition", "Square", "Semi-square", "Sesquiquadrate"}

    signals = {
        'positive_energy': [],
        'negative_energy': []
    }

    for (body1, body2), aspect in aspects.items():
        if aspect in positive_energy_aspects:
            signals['positive_energy'].append((body1, body2, aspect))
        elif aspect in negative_energy_aspects:
            signals['negative_energy'].append((body1, body2, aspect))

    return signals

def analyze_market_cycles(positions):
    """Analyze market predictive signals based on celestial aspects."""
    all_aspects = classify_aspects(positions)
    predicted_signals = categorize_aspects(all_aspects)

    # Create a summary of findings
    summary = {}
    summary['positive_energy'] = predicted_signals['positive_energy']
    summary['negative_energy'] = predicted_signals['negative_energy']

    # Overall prediction based on the balance of energies
    overall_prediction = ''
    if len(summary['positive_energy']) > len(summary['negative_energy']):
        overall_prediction = "Predicted Market Cycle: Up"
    elif len(summary['negative_energy']) > len(summary['positive_energy']):
        overall_prediction = "Predicted Market Cycle: Down"
    else:
        overall_prediction = "Market Cycle Uncertain"

    return summary, overall_prediction

def analyze_combinations(positions):
    """Analyze combinations of celestial bodies for specific patterns."""
    aspects = classify_aspects(positions)
    combination_analysis = {}

    for size in range(2, len(celestial_objects) + 1):
        combos = list(combinations(positions.keys(), size))
        
        for combo in combos:
            combo_aspects = {key: aspects[key] for key in aspects.keys() if set(key).issubset(combo)}
            positive_count = sum(1 for a in combo_aspects.values() if a in {"Conjunction", "Trine", "Sextile"})
            negative_count = sum(1 for a in combo_aspects.values() if a in {"Opposition", "Square", "Semi-square", "Sesquiquadrate"})
            
            if positive_count > negative_count:
                combination_analysis[combo] = "Pattern Indicates: Upward Trend Continuation"
            elif negative_count > positive_count:
                combination_analysis[combo] = "Pattern Indicates: Downward Trend Continuation"
            else:
                combination_analysis[combo] = "Uncertain Trend"

    return combination_analysis

# Function to check for trend reversals based on cyclical analysis
def evaluate_trend_reversal(combination_analysis):
    """Evaluate patterns in combinations for trend reversals."""
    reversals = {}
    
    for combo, analysis in combination_analysis.items():
        if "Upward" in analysis and combo in combination_analysis:
            reversals[combo] = "Possible Reversal from Upward"
        elif "Downward" in analysis and combo in combination_analysis:
            reversals[combo] = "Possible Reversal from Downward"
    
    return reversals

def overall_analysis(market_summary, combination_analysis):
    """Provide an overall analysis of positive and negative patterns and their ratios."""
    total_positive = len(market_summary['positive_energy'])
    total_negative = len(market_summary['negative_energy'])

    # Further evaluate combinations for their contribution to the overall totals
    for analysis in combination_analysis.values():
        if "Upward" in analysis:
            total_positive += 1
        elif "Downward" in analysis:
            total_negative += 1

    total_patterns = total_positive + total_negative
    ratio_positive_to_negative = total_positive / total_negative if total_negative > 0 else float('inf')  # Avoid division by zero
    
    overall_result = {
        'total_positive': total_positive,
        'total_negative': total_negative,
        'ratio_positive_to_negative': ratio_positive_to_negative,
        'dominance': 'Positive' if total_positive > total_negative else 'Negative' if total_negative > total_positive else 'Equal'
    }

    return overall_result

# Example Usage
if __name__ == "__main__":
    current_status = get_datetime_info()
    print("Current Status and Positions:")
    print(current_status)

    # Analyze market cycles based on planetary positions
    market_summary, market_prediction = analyze_market_cycles(current_status['positions'])
    print("\nMarket Cycle Analysis:")
    print(f"Positive Energy Aspects: {market_summary['positive_energy']}")
    print(f"Negative Energy Aspects: {market_summary['negative_energy']}")
    print(market_prediction)

    # Analyze combinations for patterns
    combination_analysis = analyze_combinations(current_status['positions'])
    print("\nCombination Pattern Analysis:")
    for combo, result in combination_analysis.items():
        print(f"{combo}: {result}")

    # Evaluate possible trend reversals based on combination analysis
    trend_reversals = evaluate_trend_reversal(combination_analysis)
    print("\nTrend Reversal Analysis:")
    for combo, result in trend_reversals.items():
        print(f"{combo}: {result}")

    # Overall analysis of positive and negative patterns
    overall_result = overall_analysis(market_summary, combination_analysis)
    print("\nOverall Analysis:")
    print(f"Total Positive Patterns: {overall_result['total_positive']}")
    print(f"Total Negative Patterns: {overall_result['total_negative']}")
    print(f"Ratio of Positive to Negative Patterns: {overall_result['ratio_positive_to_negative']:.2f}")
    print(f"Dominance: {overall_result['dominance']}")