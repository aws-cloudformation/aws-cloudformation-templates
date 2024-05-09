var response = require('cfn-response');
var aws = require('aws-sdk');
var elasticache = new aws.ElastiCache({ apiVersion: '2015-02-02' });

exports.handler = function (event, context) {
    console.log('REQUEST RECEIVED:\\n', JSON.stringify(event));
    if (event.RequestType == 'Delete') {
        response.send(event, context, response.SUCCESS);
        return;
    }
    var ssClusterId = event.ResourceProperties.SSClusterId;
    var ssWindow = event.ResourceProperties.SSWindow;
    var ssRetentionLimit = event.ResourceProperties.SSRetentionLimit;
    var responseData = {};
    var params = {
        ReplicationGroupId: ssClusterId,
        SnapshottingClusterId: ssClusterId + '-002',
        SnapshotWindow: ssWindow,
        SnapshotRetentionLimit: ssRetentionLimit
    };
    if (ssClusterId && ssWindow && ssRetentionLimit) {
        elasticache.modifyReplicationGroup(params, function (err, data) {
            if (err) {
                responseData = { Error: 'Issue with creating backup' };
                console.log(responseData.Error + ':\\n', err);
                response.send(event, context, response.FAILED, responseData);
            }
            else {
                console.log('backup:', JSON.stringify(data, null, 2));
                responseData = data;
                console.log(data);
                response.send(event, context, response.SUCCESS, responseData);
            };
        });
    } else {
        responseData = { Error: 'Not all parameters specified' };
        console.log(responseData.Error);
        response.send(event, context, response.FAILED, responseData);
    }
};
