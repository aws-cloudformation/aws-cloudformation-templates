import json

DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
TIMES = ['morning', 'afternoon', 'evening', 'night', 'day', 'late_night']

def lambda_handler(event, _):
    """
    Lambda handler to generate a personalized greeting message.
    """
    # Extracting parameters from the event
    name = event.get("name", "").strip()
    city = event.get("city", "").strip()
    time = event.get("time", "day").strip()
    day = event.get("day", None)

    # Validating and defaulting the time
    if time not in TIMES:
        time = "day"
    
    # Validating and defaulting the day
    if day and day not in DAYS:
        day = None

    # Generating the greeting message
    greetings = f"Good {time}, {name or 'there'} from {city or 'everywhere'}."
    
    if day:
        greetings += f" Happy {day}!"

    # Adding a time-specific message
    if time in ['morning', 'late_night']:
        greetings += " Hope you have a great start to your day!"
    elif time == 'evening':
        greetings += " Wishing you a relaxing evening!"

    # Returning the response
    return {
        'statusCode': 200,
        'body': json.dumps(greetings)
    }
