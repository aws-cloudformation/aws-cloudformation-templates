"""Generate a greeting as a demo of an API"""

import json

DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
TIMES = ['morning', 'afternoon', 'evening', 'night', 'day']


def lambda_handler(event, _):
    """
    Lambda handler
    """
    name = event.get("name", "you")
    city = event.get("city", "world")
    time = event.get("time", "day")
    day = event.get("day", None)

    if time not in TIMES:
        time = "day"
    if day and day not in DAYS:
        day = None

    greetings = f"Good {time}, {name} of {city}."
    if day:
        greetings += f" Happy {day}"

    return {
        'statusCode': 200,
        'body': json.dumps(greetings)
    }
