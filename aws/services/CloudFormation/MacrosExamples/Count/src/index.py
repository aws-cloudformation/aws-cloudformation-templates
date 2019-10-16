import copy
import json

def process_template(template,parameters):
    new_template = copy.deepcopy(template)
    status = 'success'

    for name, resource in template['Resources'].items():
        if 'Count' in resource:
            
            # Check if the value of Count is referenced to a parameter passed in the template
            try:
                refValue = new_template['Resources'][name]['Count'].pop('Ref')
                # Convert referenced parameter to an integer value
                count = int(parameters[refValue])
                # Remove the Count property from this resource
                new_template['Resources'][name].pop('Count')
            
            except AttributeError:
                # Use numeric count value
                count = new_template['Resources'][name].pop('Count')
            
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

def update_placeholder(resource_structure, iteration):
    # Convert the json into a string
    resourceString = json.dumps(resource_structure)
    # Count the number of times the placeholder is found in the string
    placeHolderCount = resourceString.count('%d')

    # If the placeholder is found then replace it
    if placeHolderCount > 0:
        print("Found {} occurrences of decimal placeholder in JSON, replacing with iterator value {}".format(placeHolderCount, iteration))
        # Make a list of the values that we will use to replace the decimal placeholders - the values will all be the same
        placeHolderReplacementValues = [iteration] * placeHolderCount
        # Replace the decimal placeholders using the list - the syntax below expands the list
        resourceString = resourceString % (*placeHolderReplacementValues,)
        # Convert the string back to json and return it
        return json.loads(resourceString)
    else:
        print("No occurences of decimal placeholder found in JSON, therefore nothing will be replaced")
        return resource_structure

def multiply(resource_name, resource_structure, count):
    resources = {}
    # Loop according to the number of times we want to multiply, creating a new resource each time
    for iteration in range(1, (count + 1)):
        print("Multiplying '{}', iteration count {}".format(resource_name,iteration))
        multipliedResourceStructure = update_placeholder(resource_structure,iteration)
        resources[resource_name+str(iteration)] = multipliedResourceStructure
    return resources


def handler(event, context):
    result = process_template(event['fragment'],event['templateParameterValues'])
    return {
        'requestId': event['requestId'],
        'status': result[0],
        'fragment': result[1],
    }
