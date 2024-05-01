"""
CloudFormation template transform macro: Explode
"""

#pylint: disable=broad-exception-raised

import re
import logging
import json

EXPLODE_RE = re.compile(r"(?i)!Explode (?P<explode_key>\w+)")
logger = logging.getLogger(__name__)


def walk_resource(resource, map_data):
    """Recursively process a resource."""
    if isinstance(resource, dict):
        new_resource = {}
        for key, value in resource.items():
            if isinstance(value, (dict, list)):
                new_resource[key] = walk_resource(value, map_data)
            elif isinstance(value, str):
                new_resource[key] = replace_explode_in_string(value, map_data)
            else:
                new_resource[key] = value
    elif isinstance(resource, list):
        new_resource = []
        for value in resource:
            if isinstance(value, (dict, list)):
                new_resource.append(walk_resource(value, map_data))
            elif isinstance(value, str):
                new_resource.append(replace_explode_in_string(value, map_data))
            else:
                new_resource.append(value)

    else:
        # if the resource is of type string
        new_resource = replace_explode_in_string(resource, map_data)
    return new_resource


def replace_explode_in_string(value, map_data):
    """Recursively process and replace Explode instances in a string."""
    match = EXPLODE_RE.search(value)
    while match:
        explode_key = match.group("explode_key")
        try:
            replace_value = map_data[explode_key]
        except KeyError as exc:
            d = json.dumps(map_data, indent=4) 
            raise Exception(
                f"Missing item {explode_key} in mapping while processing: " + 
                f"{value}\nMap Data:\n{d}"
            ) from exc
        if isinstance(replace_value, int):
            value = replace_value
            # No further explosion is possible on an int
            match = None
        else:
            value = value.replace(match.group(0), replace_value)
            match = EXPLODE_RE.search(value)
    return value


def handle_section_transform(section, mappings):
    """Go through template and explode objects in the section."""
    new_section = {}
    for resource_name, resource in section.items():
        try:
            explode_map = resource["ExplodeMap"]
            del resource["ExplodeMap"]
        except KeyError:
            # This resource does not have an ExplodeMap, so copy it verbatim
            # and move on
            new_section[resource_name] = resource
            continue
        try:
            explode_map_data = mappings[explode_map]
        except KeyError as exc:
            # This resource refers to a mapping entry which doesn't exist, so
            # fail
            raise Exception(
                f"Unable to find mapping for exploding object {resource_name}"
            ) from exc
        resource_instances = explode_map_data.keys()
        for resource_instance in resource_instances:
            new_resource = walk_resource(resource, explode_map_data[resource_instance])
            if "ResourceName" in explode_map_data[resource_instance]:
                new_resource_name = explode_map_data[resource_instance]["ResourceName"]
            else:
                new_resource_name = resource_name + resource_instance
            new_section[new_resource_name] = new_resource
    return new_section


def handle_transform(fragment):
    """Go through template and explode objects in the fragment."""
    mappings = fragment["Mappings"]
    if "Conditions" in fragment:
        fragment["Conditions"] = handle_section_transform(
            fragment["Conditions"], mappings
        )
    fragment["Resources"] = handle_section_transform(fragment["Resources"], mappings)
    if "Outputs" in fragment:
        fragment["Outputs"] = handle_section_transform(fragment["Outputs"], mappings)
    return fragment


def handler(event, _context):
    """Handle invocation in Lambda (when CloudFormation processes the Macro)"""
    fragment = event["fragment"]
    status = "success"

    try:
        fragment = handle_transform(fragment)
    except Exception as e:
        logger.error(str(e))
        status = "failure"

    return {
        "requestId": event["requestId"],
        "status": status,
        "fragment": fragment,
    }

