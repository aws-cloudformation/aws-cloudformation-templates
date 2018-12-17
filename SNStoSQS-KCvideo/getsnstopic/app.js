const AWS = require('aws-sdk');
const cfn = new AWS.CloudFormation({region: 'us-east-2'});
const response = require('cfn-response');

exports.handler = function(event, context, callback) {
  var eventType = event.RequestType;
  var respData = {};
  if (eventType == "Create") {
    var params = {
      StackName: event.ResourceProperties.StackName
    }
    cfn.describeStacks(params, (err, data) => {
      if (err) {
        console.log("Describe stack failed: " + err);
        response.send(event, context, response.FAILED);
      } else {
        var temp = data.Stacks[0].Outputs;
        for(var i=0; i<temp.length; i++) {
          if (temp[i].OutputKey === 'MySNSTopicTopicARN') {
            respData.SnsTopicName = temp[i].OutputValue;
            response.send(event, context, response.SUCCESS, respData);
          }
        }
      }
    });
  } else {
    response.send(event, context, response.SUCCESS, respData);
  }
};
