var aws = require("aws-sdk");
 
exports.handler = function(event, context) {

    const cfOperation = String(event.RequestType);
    if (cfOperation == "Create") {createResource(event, context);
    } else if (cfOperation == "Update") {updateResource(event, context);
    } else if (cfOperation == "Delete") {deleteResource(event, context);
    } else {sendResponse(event, context, "FAILED", '', {"Message":"Unrecognized Cloud Formation RequestType!"});}

};

function getCertificateInfo(certificateARN, resultHandler) {

    var acm = new aws.ACM({apiVersion: '2015-12-08', region: 'us-east-1'});
    acm.describeCertificate({CertificateArn: certificateARN}, function(err, data) {

        if (err == undefined) {
            
            const result = {
                "domainName": data.Certificate.DomainName,
                "resourceRecords": data.Certificate.DomainValidationOptions
            }

            resultHandler(undefined, result);

        } else  {resultHandler(err, undefined);}

      });

}

function createResource(event, context) {

    console.log("Approve Public Certificate. Event =>" + JSON.stringify(event))

    const certificateARN = event.ResourceProperties.certificateARN;
    if (certificateARN == undefined) {
        sendResponse(event, context, "FAILED", 'NOTCREATED', {"Message" : "Invalid Certificate ARN!"});
        return;
    }

    getCertificateInfo(certificateARN, function(err, data) {

        if (err == undefined) {

            var hostedZoneId = event.ResourceProperties.hostedZoneId;
            var domainName = data.domainName;
            var resourceRecords = JSON.stringify(data.resourceRecords);

            var operationInfo = {
                "hostedZoneId":hostedZoneId,
                "domainName": domainName,
                "resourceRecords": resourceRecords
            };

            createRoute53Records(event, context, operationInfo);

        } else  {sendResponse(event, context, "FAILURE", "NOTCREATED", {"Message" : err});}

    });

}

function createRoute53Records(event, context, info) {

    var createBatch = {Changes: [], Comment: "Insert AWS ACM Validation endpoint for " + info.domainName};
    var records = JSON.parse(info.resourceRecords);
    var arraySize = records.length;

    if (arraySize > 0) {

        for (var i = 0; i < arraySize; i++) {
            
            var record = records[i];
            var change = {"Action": "CREATE", "ResourceRecordSet": {"Name": record.ResourceRecord.Name, "ResourceRecords": [{"Value": record.ResourceRecord.Value}], "TTL": 60, "Type": record.ResourceRecord.Type}};
            createBatch.Changes.push(change);

        }
        
        const operation = {
            "HostedZoneId": info.hostedZoneId,
            "ChangeBatch": createBatch
        };

        var resourceId = info.domainName;
        var route53 = new aws.Route53({apiVersion: '2013-04-01'});
        route53.changeResourceRecordSets(operation, function(err, data) {
        
            if (err == undefined) {sendResponse(event, context, "SUCCESS", resourceId, {"Message" : "RecordSet created in Route53"});
            } else  {sendResponse(event, context, "FAILED", resourceId, {"Message" : err});}
    
        });

    } else {sendResponse(event, context, "FAILED", "NOTCREATED", {"Message" : "Public Certificate does not support DNS Validation!"});}

}

function updateResource(event, context) {

    console.log("Update Certificate Validation URL. Event =>" + JSON.stringify(event));

    const resourceId = JSON.parse(event.PhysicalResourceId);
    if (resourceId.length > 0) {

        sendResponse(event, context, "SUCCESS", resourceId, {"Message":"Resource update not implemented!"});

    } else {sendResponse(event, context, "SUCCESS", '', {"Message":"Resource update not implemented!"});}

}

function deleteResource(event, context) {

    console.log("Delete Certificate Validation URL. Event =>" + JSON.stringify(event));

    const certificateARN = event.ResourceProperties.certificateARN;
    const resourceId = event.PhysicalResourceId;

    if (resourceId != undefined && resourceId != "NOTCREATED") {

        getCertificateInfo(certificateARN, function(err, data) {

            if (err == undefined) {
    
                var hostedZoneId = event.ResourceProperties.hostedZoneId;
                var domainName = data.domainName;
                var resourceRecords = JSON.stringify(data.resourceRecords);
    
                var operationInfo = {
                    "resourceId": resourceId,
                    "hostedZoneId":hostedZoneId,
                    "domainName": domainName,
                    "resourceRecords": resourceRecords
                };
    
                deleteRoute53Records(event, context, operationInfo);
    
            } else  {sendResponse(event, context, "FAILURE", resourceId, {"Message" : err});}
    
        });

    } else {sendResponse(event, context, "SUCCESS", resourceId, {"Message":"Resource was not created, so it doesn't need to be removed!"});}

}

function deleteRoute53Records(event, context, info) {

    var resourceId = info.resourceId;
    var removeBatch = {Changes: [], Comment: "Remove AWS ACM Validation endpoint for " + event.domainName};
    var records = JSON.parse(info.resourceRecords);
    var arraySize = records.length;

    if (arraySize > 0) {

        for (var i = 0; i < arraySize; i++) {
            
            var record = records[i];
            var change = {"Action": "DELETE", "ResourceRecordSet": {"Name": record.ResourceRecord.Name, "ResourceRecords": [{"Value": record.ResourceRecord.Value}], "TTL": 60, "Type": record.ResourceRecord.Type}};
            removeBatch.Changes.push(change);

        }
        
        const operation = {
            "HostedZoneId": info.hostedZoneId,
            "ChangeBatch": removeBatch
        };

        var route53 = new aws.Route53({apiVersion: '2013-04-01'});
        route53.changeResourceRecordSets(operation, function(err, data) {
        
            if (err == undefined) {sendResponse(event, context, "SUCCESS", resourceId, {"Message" : "RecordSet created in Route53"});
            } else  {sendResponse(event, context, "FAILED", resourceId, {"Message" : err});}
    
        });

    } else {sendResponse(event, context, "FAILED", resourceId, {"Message" : "Public Certificate does not support DNS Validation!"});}

}

function sendResponse(event, context, responseStatus, resourceId, responseData) {

    var responseBody = JSON.stringify({
        Status: responseStatus,
        Reason: "See the details in CloudWatch Log Stream: " + context.logStreamName,
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