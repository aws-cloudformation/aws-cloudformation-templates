""" Multiply resources inside a cloudfomration template """

import copy


def process_template(template):
    new_template = copy.deepcopy(template)
    status = 'success'

    for name, resource in template['Resources'].items():
        if 'Count' in resource:
            count = new_template['Resources'][name].pop('Count')
            multiplied = multiply(name, new_template['Resources'][name], count)
            if not set(multiplied.keys()) & set(new_template['Resources'].keys()):
                new_template['Resources'].update(multiplied)
            else:
                status = 'failed'
                return status, template
    return status, new_template


def multiply(resource_name, resource_structure, count):
    resources = {}
    for iteration in range(1, count):
        resources[resource_name+str(iteration)] = resource_structure
    return resources


def handler(event, context):
    result = process_template(event['fragment'])
    return {
        'requestId': event['requestId'],
        'status': result[0],
        'fragment': result[1],
    }
