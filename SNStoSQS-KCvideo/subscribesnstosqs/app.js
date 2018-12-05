const AWS = require('aws-sdk');
const sns = new AWS.SNS({region: 'us-east-2'});
const response = require('cfn-response');

exports.handler = function(event, context, callback) {
  const snsTopicArn = event.ResourceProperties.SNSarn;
  const sqsEndpoint = event.ResourceProperties.SQSarn;
  var params = {
    Protocol: 'sqs',
    TopicArn: snsTopicArn,
    Endpoint: sqsEndpoint
  }
  var eventType = event.RequestType;
  switch (eventType) {
    case "Create":
      sns.subscribe(params, (err, data) => {
        if (err) {
          console.log("SNS subscription dobbindi: " + err);
          response.send(event, context, response.FAILED);
        } else {
          console.log(data);
          response.send(event, context, response.SUCCESS, data);
        }
      });
      break;
    case "Delete":
      var params = {
        TopicArn: snsTopicArn
      };
      sns.listSubscriptionsByTopic(params, (err, data) => {
        if (err) {
          console.log("Error in listing the subscriptions: " + err);
          response.send(event, context, response.FAILED);
        } else {
          var subscriptions = data.Subscriptions;
          for(var i=0; i<subscriptions.length; i++) {
            if (subscriptions[i].Endpoint === sqsEndpoint) {
              var subsArn = subscriptions[i].SubscriptionArn
              console.log("Unsubscribing this subscription: ");
              console.log(subsArn);
              sns.unsubscribe({SubscriptionArn: subsArn}, (err, data) => {
                if (err) {
                  console.log( "Error in unsubscribing the topic: " + err);
                  response.send(event, context, response.FAILED);
                } else {
                  console.log(data);
                  response.send(event, context, response.SUCCESS, data);
                }
              });
            }
          }
        }
      });
      break;
    default:
      response.send(event, context, response.SUCCESS, {});
  }
}
