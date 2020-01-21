"""
CloudFormation template transform macro: Explode
"""

import re
import sys


EXPLODE_RE = re.compile(r'(?i)!Explode (?P<explode_key>\w+)')


def walk_resource(resource, map_data):
    """Recursively process a resource."""
    if isinstance(resource, dict):
        new_resource = {}
        for key, value in resource.items():
            if isinstance(value, dict):
                new_resource[key] = walk_resource(value, map_data)
            elif isinstance(value, list):
                new_resource[key] = [walk_resource(x, map_data) for x in value]
            elif isinstance(value, str):
                new_resource[key] = replace_explode_in_string(value, map_data)
            else:
                new_resource[key] = value
    else:
        # if the resource is of type string
        new_resource = replace_explode_in_string(resource, map_data)
    return new_resource


def replace_explode_in_string(value, map_data):
    """Recursively process and replace Explode instances in a string."""
    match = EXPLODE_RE.search(value)
    while match:
        explode_key = match.group('explode_key')
        try:
            replace_value = map_data[explode_key]
        except KeyError:
            print("Missing item {} in mapping while processing {}: {}".format(
                explode_key,
                key,
                value))
        if isinstance(replace_value, int):
            value = replace_value
            # No further explosion is possible on an int
            match = None
        else:
            value = value.replace(match.group(0), replace_value)
            match = EXPLODE_RE.search(value)
    return value


def handle_transform(template):
    """Go through template and explode resources."""
    mappings = template['Mappings']
    resources = template['Resources']
    new_resources = {}
    for resource_name, resource in resources.items():
        try:
            explode_map = resource['ExplodeMap']
            del resource['ExplodeMap']
        except KeyError:
            # This resource does not have an ExplodeMap, so copy it verbatim
            # and move on
            new_resources[resource_name] = resource
            continue
        try:
            explode_map_data = mappings[explode_map]
        except KeyError:
            # This resource refers to a mapping entry which doesn't exist, so
            # fail
            print('Unable to find mapping for exploding resource {}'.format(resource_name))
            raise
        resource_instances = explode_map_data.keys()
        for resource_instance in resource_instances:
            new_resource = walk_resource(resource, explode_map_data[resource_instance])
            if 'ResourceName' in explode_map_data[resource_instance]:
                new_resource_name = explode_map_data[resource_instance]['ResourceName']
            else:
                new_resource_name = resource_name + resource_instance
            new_resources[new_resource_name] = new_resource
    template['Resources'] = new_resources
    return template


def handler(event, _context):
    """Handle invocation in Lambda (when CloudFormation processes the Macro)"""
    fragment = event["fragment"]
    status = "success"

    try:
        fragment = handle_transform(event["fragment"])
    except:
        status = "failure"

    return {
        "requestId": event["requestId"],
        "status": status,
        "fragment": fragment,
    }


if __name__ == "__main__":
    """
    If run from the command line, parse the file specified and output it
    This is quite naive; CF YAML tags like !GetAtt will break it (as will
    !Explode, but you can hide that in a string). Probably best to use JSON.
    Releatedly, always outputs JSON.
    """
    if len(sys.argv) == 2:
        import json
        filename = sys.argv[1]
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            try:
                import yaml
            except ImportError:
                print("Please install PyYAML to test yaml templates")
                sys.exit(1)
            with open(filename, 'r') as file_handle:
                loaded_fragment = yaml.safe_load(file_handle)
        elif filename.endswith(".json"):
            with open(sys.argv[1], 'r') as file_handle:
                loaded_fragment = json.load(file_handle)
        else:
            print("Test file needs to end .yaml, .yml or .json")
            sys.exit(1)
        new_fragment = handle_transform(loaded_fragment)
        print(json.dumps(new_fragment))
