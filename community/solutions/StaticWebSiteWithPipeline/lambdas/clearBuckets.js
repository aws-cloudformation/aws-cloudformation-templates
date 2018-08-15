var aws = require("aws-sdk");
var resourceName = "emptyBucketToken";

exports.handler = function(event, context) {

    if (event.RequestType == "Update" || event.RequestType == "Create") {
        sendResponse(event, context, "SUCCESS", resourceName, {"Message" : "ClearBuckets not need to run when Stack is Created or Updated!"});
        return;
    }

    console.log("clearBuckets for =>" + JSON.stringify(event));
    var bucketName = event.ResourceProperties.bucketName;

    getBucketObjects(bucketName, function(err, data) {

        if (err == null) {
            
            clearBucket(data, function(err, data) {

                if (err == null) {sendResponse(event, context, "SUCCESS", resourceName, {"Message" : "Buckets Cleared!"});
                } else {sendResponse(event, context, "FAILED", resourceName, {"Message" : err});}

            });

        } else {sendResponse(event, context, "FAILED", resourceName, {"Message" : err});}

    });

};

function getBucketObjects(bucketName, getHandler) {

    var s3 = new aws.S3();
    var listParam = {"Bucket": bucketName};
    
    s3.listObjects(listParam, function (err, data) {

        if (err == null) {

            var items = data.Contents;
            var keys = items.map(item => {return {"Key": item.Key}});
            var param = {
                "Bucket": bucketName,
                "Delete": {"Objects": keys, "Quiet": true}
            };

            getHandler(null, param);

        } else { getHandler(err, null); }

    });
}

function clearBucket(objectList, clearHandler) {
    
    var s3 = new aws.S3();
    s3.deleteObjects(objectList, function(err, data) {
                
        if (err == null) {
            clearHandler(null, data);
        } else {clearHandler(err, null);}

    });
    
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