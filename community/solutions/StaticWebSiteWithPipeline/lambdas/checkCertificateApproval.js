const aws = require('aws-sdk');

exports.handler = (event, context, callback) => {

    console.log('Check Certification Validation =>'+ JSON.stringify(event));

    if (event.RequestType == "Update" || event.RequestType == "Delete") {
        sendResponse(event, context, "SUCCESS", event.PhysicalResourceId, {"Message" : "Certificate Approval Status does not need to be Updated or Removed!"});
        return;
    }

    var certificateARN = event.ResourceProperties.certificateARN;
    if (certificateARN == undefined) {
        sendResponse(event, context, "FAILED", '', {"Message" : "Invalid Certificate ARN!"});
        return;
    }

    var numberOfCalls = event.numberOfCalls;
    if (numberOfCalls == undefined) {numberOfCalls = process.env.INVOCATION_LIMIT;}
    if (numberOfCalls == undefined) {numberOfCalls = 10;}

    if (numberOfCalls > 0) {

        checkCertificate(event, context, numberOfCalls);

    } else {
        
        const resourceId = String(event.RequestId);
        sendResponse(event, context, "FAILED", resourceId, {"Message":"Max function invocation reached!"});

    }
    
};

function checkCertificate(event, context, nextCall) {

    if (nextCall > 0) {
        
        const certificateARN = event.ResourceProperties.certificateARN;
        const acm = new aws.ACM({apiVersion: '2015-12-08', region: 'us-east-1'});
        acm.describeCertificate({CertificateArn: certificateARN}, function(err, data) {

            if (err == undefined) {

                const resourceId = String(event.RequestId);
                const status = data.Certificate.Status;
                if (status == "ISSUED") {

                    sendResponse(event, context, "SUCCESS", resourceId, {"Message" : "Certificate " + certificateARN + " Approved!"});

                } else if (status == "INACTIVE" || status == "EXPIRED" || status == "VALIDATION_TIMED_OUT" || status == "REVOKED" || status == "FAILED") {

                    sendResponse(event, context, "FAILED", resourceId, {"Message" : "Certificate " + certificateARN + " Status is:" + status});

                } else if (status == "PENDING_VALIDATION") {

                    var remaining = context.getRemainingTimeInMillis();
                    setTimeout(function () {
                        
                        var counter = {"numberOfCalls":nextCall -1};
                        var newEvent = Object.assign(event, counter);

                        const params = {
                            FunctionName: context.functionName,
                            InvocationType: 'Event',
                            Payload: JSON.stringify(newEvent),
                            Qualifier: context.functionVersion
                        };
                
                        const lambda = new aws.Lambda();
                        lambda.invoke(params, context.done);

                      }, remaining / 2);


                } else {sendResponse(event, context, "FAILED", resourceId, {"Message" : "Invalid Certificate Status returned from ACM:" + status});}
    
            } else  {sendResponse(event, context, "FAILED", event.PhysicalResourceId, {"Message" : err});}
    
          });

    } else {sendResponse(event, context, "FAILED", event.PhysicalResourceId, {"Message":"CheckApproval reached Invoke Limit!"})}

}

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