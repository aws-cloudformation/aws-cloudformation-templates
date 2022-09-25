import copy
import json

def process_template(template,parameters):
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

            print("Found 'Count' property with value {} in '{}' resource....multiplying!".format(count,name))
            # Remove the original resource from the template but take a local copy of it
            resourceToMultiply = new_template['Resources'].pop(name)
            # Create a new block of the resource multiplied with names ending in the iterator and the placeholders substituted
            resourcesAfterMultiplication = multiply(name, resourceToMultiply, count)
            if not set(resourcesAfterMultiplication.keys()) & set(new_template['Resources'].keys()):
                new_template['Resources'].update(resourcesAfterMultiplication)
            else:
                status = 'failed'
                return status, template
        else:
            print("Did not find 'Count' property in '{}' resource....Nothing to do!".format(name))
    return status, new_template

def update_placeholder(resource_structure, iteration, value=None):
    # Convert the json into a string
    resourceString = json.dumps(resource_structure)
    # Count the number of times the placeholder is found in the string
    decimalPlaceHolderCount = resourceString.count('%d')
    stringPlaceHolderCount = 0 if value is None else resourceString.count('%s')

    # If the decimal placeholder is found then replace it
    if decimalPlaceHolderCount > 0:
        print("Found {} occurrences of decimal placeholder in JSON, replacing with iterator {}".format(decimalPlaceHolderCount, iteration))
        # Replace the decimal placeholders
        resourceString = resourceString.replace('%d', str(iteration))

    # If the string placeholder is found then replace it
    if stringPlaceHolderCount > 0:
        print("Found {} occurrences of string placeholder in JSON, replacing with value {}".format(stringPlaceHolderCount, value))
        # Replace the string placeholders
        resourceString = resourceString.replace('%s', str(value))

    if decimalPlaceHolderCount > 0 or stringPlaceHolderCount > 0:
        # Convert the string back to json and return it
        return json.loads(resourceString)
    else:
        print("No occurences of decimal placeholder found in JSON, therefore nothing will be replaced")
        return resource_structure

def multiply(resource_name, resource_structure, count):
    resources = {}
    # Loop according to the number of times we want to multiply, creating a new resource each time
    if isinstance(count, int):
        for iteration in range(1, (count + 1)):
            print("Multiplying '{}', iteration count {}".format(resource_name,iteration))
            multipliedResourceStructure = update_placeholder(resource_structure,iteration)
            resources[resource_name+str(iteration)] = multipliedResourceStructure
    else:
        for iteration, value in enumerate(count):
            print("Multiplying '{}', iteration count {}".format(resource_name,iteration))
            multipliedResourceStructure = update_placeholder(resource_structure,iteration,value)
            resources[resource_name+str(iteration)] = multipliedResourceStructure
    return resources

def handler(event, context):
    result = process_template(event['fragment'],event['templateParameterValues'])
    return {
        'requestId': event['requestId'],
        'status': result[0],
        'fragment': result[1],
    }
