var aws = require("aws-sdk");

exports.handler = function(event, context) {

    if (event.RequestType == "Update" || event.RequestType == "Delete") {
        sendResponse(event, context, "SUCCESS", event.PhysicalResourceId, {"Message" : "HostedZone Name does not need to be Updated or Removed!"});
        return;
    }

    console.log("Get HostedZone Name for =>" + JSON.stringify(event));
    var hostedZoneId = event.ResourceProperties.hostedZoneId;
    var route53 = new aws.Route53({apiVersion: '2013-04-01'});
    route53.getHostedZone({Id: hostedZoneId}, function(err, data) {

        if (err == undefined) {

            var zoneName = data.HostedZone.Name;
            zoneName = zoneName.substring(0, zoneName.length - 1);
            sendResponse(event, context, "SUCCESS", zoneName, {"Message" : "HostedZone Name Found!", "HostedZoneName":zoneName});

        } else {sendResponse(event, context, "FAILED", '', {"Message" : err});}

    });
};

function sendResponse(event, context, responseStatus, resourceId, responseData) {
    
    const responseMessage = responseStatus == "SUCCESS" ? "See the details in CloudWatch Log Stream: " + context.logStreamName : JSON.stringify(responseData.Message);

    var responseBody = JSON.stringify({
        Status: responseStatus,
        Reason: responseMessage,
        PhysicalResourceId: resourceId,
        StackId: event.StackId,
        RequestId: event.RequestId,
        LogicalResourceId: event.LogicalResourceId,
        Data: responseData
    });

    console.log("Sending response " + responseStatus + ": " + responseBody);

    var https = require("https");
    var url = require("url");
 
    var parsedUrl = url.parse(event.ResponseURL);
    var options = {
        hostname: parsedUrl.hostname,
        port: 443,
        path: parsedUrl.path,
        method: "PUT",
        headers: {
            "content-type": "",
            "content-length": responseBody.length
        }
    };
 
    var request = https.request(options, function(response) {
        context.done();
    });
 
    request.on("error", function(error) {
        console.log("sendResponse Error:" + error);
        context.done();
    });
  
    request.write(responseBody);
    request.end();

}