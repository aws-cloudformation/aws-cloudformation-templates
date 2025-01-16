package api

import "github.com/aws/aws-lambda-go/events"

// Fail returns a failure response
func Fail(code int, msg string) events.APIGatewayProxyResponse {
	response := events.APIGatewayProxyResponse{
		StatusCode: code,
		Body:       "{\"message\": \"" + msg + "\"}",
	}
	response.Headers = make(map[string]string)
	AddCORSHeaders(response)
	response.Headers["X-Rain-Webapp-Error"] = msg
	return response
}

// AddCORSHeaders adds the necessary headers to a response to enable cross site requests
func AddCORSHeaders(response events.APIGatewayProxyResponse) {
	response.Headers["Access-Control-Allow-Headers"] = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent,X-KG-Partition"
	response.Headers["Access-Control-Allow-Origin"] = "*"
	response.Headers["Access-Control-Allow-Methods"] = "OPTIONS, GET, PUT, POST, DELETE, PATCH, HEAD"
}
