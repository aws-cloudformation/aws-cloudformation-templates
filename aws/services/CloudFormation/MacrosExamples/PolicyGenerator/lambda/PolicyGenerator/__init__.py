import os
import samtranslator.policy_templates_data

_thisdir = os.path.dirname(os.path.abspath(__file__))

# ./schema.json
SCHEMA_FILE = samtranslator.policy_templates_data.SCHEMA_FILE 

# ./policy_templates.json
POLICY_TEMPLATES_FILE = os.path.join(_thisdir, "policy_templates.json")
