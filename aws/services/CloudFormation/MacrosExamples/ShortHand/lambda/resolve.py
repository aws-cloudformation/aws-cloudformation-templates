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

import json

SPEC = json.load(open("spec.json"))

def resource(name):
    """
    Returns resource types that match `name`, working right-to-left
    E.g. S3::Bucket will match AWS::S3::Bucket
    """

    return [
        key for key in SPEC["ResourceTypes"].keys()
        if key.endswith(name)
    ]
