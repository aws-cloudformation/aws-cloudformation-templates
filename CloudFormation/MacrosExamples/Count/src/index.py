"Lambda implementation for the Count macro"
import copy
import json

def process_template(template,parameters):
    "Process the template to multiply resources"

    # Make a copy of the template to modify
    new_template = copy.deepcopy(template)
    status = 'success'

    for name, resource in template['Resources'].items():
        if 'Count' in resource:
            if isinstance(new_template['Resources'][name]['Count'], dict):
                # Check if the value of Count is referenced to a parameter passed in the template
                refValue = new_template['Resources'][name]['Count'].pop('Ref')
                # Convert referenced parameter to an integer value
                count_str = str(parameters[refValue])
                # Remove the Count property from this resource
                new_template['Resources'][name].pop('Count')
            else:
                # Use literal value
                count_str = str(new_template['Resources'][name].pop('Count'))

            if count_str.isnumeric():
                count = int(count_str)
            elif '[' in count_str:
                count = json.loads(count_str.replace("'", '"'))
            else:
                count = [count_str]

            print(f"Found 'Count' property with value {count} in '{name}' resource....multiplying!")
            # Remove the original resource from the template but take a local copy of it
            resourceToMultiply = new_template['Resources'].pop(name)
            # Create a new block of the resource multiplied with names ending in the
            # iterator and the placeholders substituted
            resourcesAfterMultiplication = multiply(name, resourceToMultiply, count)
            if not set(resourcesAfterMultiplication.keys()) & set(new_template['Resources'].keys()):
                new_template['Resources'].update(resourcesAfterMultiplication)
            else:
                status = 'failed'
                return status, template
        else:
            print(f"Did not find 'Count' property in '{name}' resource....Nothing to do!")
    return status, new_template

def update_placeholder(resource_structure, iteration, value=None):
    "Update the placeholders in the resource structure"

    # Convert the json into a string
    resource_string = json.dumps(resource_structure)
    # Count the number of times the placeholder is found in the string
    decimal_placeholder_count = resource_string.count('%d')
    string_placeholder_count = 0 if value is None else resource_string.count('%s')

    # If the decimal placeholder is found then replace it
    if decimal_placeholder_count > 0:
        print(f"Found {decimal_placeholder_count} occurrences of decimal placeholder in JSON, " +
              f"replacing with iterator {iteration}")
        # Replace the decimal placeholders
        resource_string = resource_string.replace('%d', str(iteration))

    # If the string placeholder is found then replace it
    if string_placeholder_count > 0:
        print(f"Found {string_placeholder_count} occurrences of string placeholder in JSON, " +
              f"replacing with value {value}")
        # Replace the string placeholders
        resource_string = resource_string.replace('%s', str(value))

    if decimal_placeholder_count > 0 or string_placeholder_count > 0:
        # Convert the string back to json and return it
        return json.loads(resource_string)
    
    print("No occurences of decimal placeholder found in JSON, " + 
            "therefore nothing will be replaced")
    return resource_structure

def multiply(resource_name, resource_structure, count):
    "Multiply the resource structure by the count"

    resources = {}
    # Loop according to the number of times we want to multiply, creating a new resource each time
    if isinstance(count, int):
        for iteration in range(1, (count + 1)):
            print(f"Multiplying '{resource_name}', iteration count {iteration}")
            multiplied_resource_structure = update_placeholder(resource_structure,iteration)
            resources[resource_name+str(iteration)] = multiplied_resource_structure
    else:
        for iteration, value in enumerate(count):
            print(f"Multiplying '{resource_name}', iteration count {iteration}")
            multiplied_resource_structure = update_placeholder(resource_structure,iteration,value)
            resources[resource_name+str(iteration)] = multiplied_resource_structure
    return resources

def handler(event, _):
    "Lambda handler"

    result = process_template(event['fragment'],event['templateParameterValues'])
    return {
        'requestId': event['requestId'],
        'status': result[0],
        'fragment': result[1],
    }
