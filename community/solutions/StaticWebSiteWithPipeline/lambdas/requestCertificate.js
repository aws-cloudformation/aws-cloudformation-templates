var aws = require("aws-sdk");
 
exports.handler = function(event, context) {

    const cfOperation = String(event.RequestType);
    if (cfOperation == "Create") {createResource(event, context);
    } else if (cfOperation == "Update") {updateResource(event, context);
    } else if (cfOperation == "Delete") {deleteResource(event, context);
    } else {sendResponse(event, context, "FAILED", '', {"Message":"Unrecognized Cloud Formation RequestType!"});}

};

function createResource(event, context) {

    console.log("Request Public Certificate. Event =>" + JSON.stringify(event))

    var hostedZoneId = event.ResourceProperties.hostedZoneId;
    var hostName = event.ResourceProperties.hostName;
    var extraDomains = event.ResourceProperties.extraDomains;

    var route53 = new aws.Route53({apiVersion: '2013-04-01'});
    route53.getHostedZone({Id: hostedZoneId}, function(err, data) {

        if (err == undefined) {

            var zoneName = data.HostedZone.Name;
            var domainName =  hostName + "." + zoneName.substring(0, zoneName.length-1);

            var executionInfo = {
                HostedZoneName:zoneName,
                DomainName: domainName,
                AlternativeDomains: extraDomains
            };

            requestCertificate(event, context, executionInfo);

        } else {sendResponse(event, context, "FAILED", '', {"Message" : err});}

    });

}

function requestCertificate(event, context, info) {

    const token = String(info.DomainName).split('.').join('').substr(0, 30);

    var acm_params = {
        DomainName: info.DomainName,
        ValidationMethod: 'DNS',
        IdempotencyToken: token,
        Options: {CertificateTransparencyLoggingPreference: 'ENABLED'},
    };
    
    if (Array.isArray(info.AlternativeDomains) && info.AlternativeDomains.length > 0) {
        acm_params.SubjectAlternativeNames = info.AlternativeDomains;
    }
    
    var acm = new aws.ACM({apiVersion: '2015-12-08', region: 'us-east-1'});
    acm.requestCertificate(acm_params, function(err, data) {
      
      if (err) {
        sendResponse(event, context,"FAILED", "NOTCREATED", {"Message" : err.stack});
      } else {
        var arn = data.CertificateArn;
        var zoneName = info.HostedZoneName.substring(0, info.HostedZoneName.length - 1)
        sendResponse(event, context, "SUCCESS", arn, {"Message" : "Resource creation successful!", "ResourceId":arn});
      }
      
    });

}

function updateResource(event, context) {

    console.log("Update Public Certificate. Event =>" + JSON.stringify(event));

    const resourceId = event.PhysicalResourceId;
    if (resourceId != undefined) {

        sendResponse(event, context, "SUCCESS", resourceId, {"Message":"Resource update not implemented!"});

    } else {sendResponse(event, context, "SUCCESS", '', {"Message":"Resource update not implemented!"});}

}

function deleteResource(event, context) {

    console.log("Delete Public Certificate. Event =>" + JSON.stringify(event));

    const resourceId = event.PhysicalResourceId;
    if (resourceId != undefined && String(resourceId) != "" && String(resourceId) != "NOTCREATED") {

        var acm = new aws.ACM({apiVersion: '2015-12-08', region: 'us-east-1'});
        acm.deleteCertificate({CertificateArn: resourceId}, function(err, data) {
          
            if (err) {sendResponse(event, context,"FAILED", resourceId, {"Message" : err});
            } else {sendResponse(event, context, "SUCCESS", resourceId, {"Message" : "Resource deletion successfull!"});}
            
          });

    } else {sendResponse(event, context, "SUCCESS", 'NOTCREATED', {"Message":"Resource was not created, so it doesn't need to be removed!"});}
    
}

function sendResponse(event, context, responseStatus, resourceId, responseData) {
    
    const responseMessage = responseStatus == "SUCCESS" ? "See the details in CloudWatch Log Stream: " + context.logStreamName : JSON.stringify(responseData.Message)

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