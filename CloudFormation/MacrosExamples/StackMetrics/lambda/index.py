"Macro handler"

def handler(event, _):
    "Process the template fragment"

    template = event["fragment"]

    template["Resources"]["StackMetrics"] = {
        "Type": "Custom::StackMetrics",
        "Properties": {
            "ServiceToken": {
                "Fn::ImportValue": "StackMetricsMacroFunction",
            },
            "StackName": {
                "Ref": "AWS::StackName",
            },
            "ResourceCount": len(template["Resources"].keys()),
            "ServiceTimeout": 120
        },
    }

    return {
        "requestId": event["requestId"],
        "status": "success",
        "fragment": template,
    }
