# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""
Convert an object from our custom format into something more explicit
"""

import resolve
import re

SUB_RE = re.compile(r"\$\{(?!!)")

def handle_value(value):
    if SUB_RE.match(value):
        return {
            "Fn::Sub": value,
        }

    return value

def unroll_props(rolled):
    props = {}

    for key, value in rolled.items():
        key_parts = key.split(".")

        current = props

        for part in key_parts[:-1]:
            if part not in current:
                current[part] = {}
                current = current[part]

        current[key_parts[-1]] = handle_value(value)

    return props

def parse_name(name):
    parts = name.split()

    ident = [
        part
        for part in parts
        if "=" not in part
    ]

    props = unroll_props({
        key: value
        for key, value in [
            part.split("=")
            for part
            in parts if "=" in part
        ]
    })

    return ident, props

def convert(value):
    if isinstance(value, str):
        yield parse_name(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            ident, props = parse_name(k)
            props.update(unroll_props(v))
            yield ident, props
    elif isinstance(value, list):
        for v in value:
            for ident, props in convert(v):
                yield ident, props
    else:
        raise Exception("Bad format at: {}".format(value))

def convert_template(template):
    resources = {}
    counts = {}

    for ident, props in convert(template.get("Resources", [])):
        resource = {}

        if len(ident) == 1:
            name = None
            resource["Type"] = ident[0]
        else:
            name = ident[0]
            resource["Type"] = ident[1]

        resource["Properties"] = props

        types = resolve.resource(resource["Type"])

        if len(types) != 1:
            raise Exception("Ambiguous or unknown resource type: {}".format(resource["Type"]))

        resource["Type"] = types[0]

        # Handle un-named resources
        if not name:
            name = resource["Type"].split("::")[-1]
            if resource["Type"] not in counts:
                counts[resource["Type"]] = 1
            else:
                counts[resource["Type"]] += 1

            while "{}{}".format(name, counts[resource["Type"]]) in resources:
                counts[resource["Type"]] += 1

            name = "{}{}".format(name, counts[resource["Type"]])

        resources[name] = resource

    template["Resources"] = resources

    return template
