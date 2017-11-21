'use strict';
console.log('Loading function');

const createResponse = (statusCode, body) => {
  return {
    "statusCode": statusCode,
    "body": body || ""
  }
};

exports.handler = (event, context, callback) => {
  const response = createResponse(200, "Hello SAM.");
  callback(null, response);
};
