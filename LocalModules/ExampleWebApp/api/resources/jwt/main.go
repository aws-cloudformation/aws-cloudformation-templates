package main

import (
	"context"
	"fmt"
	"log"

	"encoding/json"
	"errors"
	"net/http"
	"net/url"
	"os"
	"strings"

	"example/api"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/lestrrat-go/jwx/v2/jwk"
	"github.com/lestrrat-go/jwx/v2/jwt"
)

func HandleRequest(ctx context.Context,
	request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {

	fmt.Printf("request: %+v\n", request)
	message := fmt.Sprintf("{\"message\": \"Request Resource: %s, Path: %s, HTTPMethod: %s\"}", request.Resource, request.Path, request.HTTPMethod)
	fmt.Printf("message: %s\n", message)

	headers := make(map[string]string)
	code := request.QueryStringParameters["code"]
	refresh := request.QueryStringParameters["refresh"]

	response := events.APIGatewayProxyResponse{
		StatusCode: 200,
		Headers:    headers,
		Body:       "{\"message\": \"Success\"}",
	}

	api.AddCORSHeaders(response)

	switch request.HTTPMethod {
	case "GET":
		jsonData, err := handleAuth(code, refresh)
		if err != nil {
			fmt.Printf("handleAuth: %v", err)
			return api.Fail(401, "Auth Failure"), nil
		}
		response.Body = jsonData
		return response, nil
	case "OPTIONS":
		response.StatusCode = 204
		response.Body = "{}"
		return response, nil
	default:
		return api.Fail(400, fmt.Sprintf("Unexpected HttpMethod: %s", request.HTTPMethod)), nil
	}

}

func main() {
	lambda.Start(HandleRequest)
}

// getCognitoIssuer returns the Cognito issuer URL.
func getCognitoIssuer() (string, error) {
	region := os.Getenv("COGNITO_REGION")
	if region == "" {
		return "", errors.New("missing COGNITO_REGION")
	}

	cognitoPoolID := os.Getenv("COGNITO_POOL_ID")
	if cognitoPoolID == "" {
		return "", errors.New("missing COGNITO_POOL_ID")
	}

	return fmt.Sprintf("https://cognito-idp.%s.amazonaws.com/%s", region, cognitoPoolID), nil
}

// getPublicKeys retrieves the public keys from the Cognito issuer.
func getPublicKeys() (jwk.Set, error) {

	cognitoIssuer, err := getCognitoIssuer()
	if err != nil {
		return nil, err
	}

	url := cognitoIssuer + "/.well-known/jwks.json"
	fmt.Printf("JWK URL: %s\n", url)

	set, err := jwk.Fetch(context.Background(), url)
	if err != nil {
		fmt.Printf("failed to fetch JWK: %s\n", err)
		return nil, err
	}

	{
		jsonbuf, err := json.Marshal(set)
		if err != nil {
			log.Printf("failed to marshal key set into JSON: %s\n", err)
			return nil, err
		}
		fmt.Printf("json jwk: %s\n", jsonbuf)
	}

	return set, nil
}

func handleAuth(code string, refresh string) (string, error) {

	redirectURI := os.Getenv("COGNITO_REDIRECT_URI")
	cognitoDomainPrefix := os.Getenv("COGNITO_DOMAIN_PREFIX")
	cognitoDomainPrefix = strings.ReplaceAll(cognitoDomainPrefix, ".", "-")
	cognitoClientID := os.Getenv("COGNITO_APP_CLIENT_ID")
	cognitoRegion := os.Getenv("COGNITO_REGION")

	tokenEndpoint := fmt.Sprintf("https://%s.auth.%s.amazoncognito.com/oauth2/token",
		cognitoDomainPrefix, cognitoRegion)

	var postData url.Values

	if code != "" {
		postData = url.Values{
			"grant_type":   {"authorization_code"},
			"client_id":    {cognitoClientID},
			"code":         {code},
			"redirect_uri": {redirectURI},
		}
	} else {
		if refresh == "" {
			return "", errors.New("no refresh token")
		}

		postData = url.Values{
			"grant_type":    {"refresh_token"},
			"client_id":     {cognitoClientID},
			"refresh_token": {refresh},
		}
	}

	fmt.Printf("About to post to %s: %+v\n", tokenEndpoint, postData)

	resp, err := http.PostForm(tokenEndpoint, postData)
	if err != nil {
		fmt.Printf("PostForm error from %s: %v\n", tokenEndpoint, err)
		return "", errors.New("token endpoint failed")
	}
	defer resp.Body.Close()

	fmt.Printf("resp: %+v\n", resp)

	if resp.StatusCode >= 400 {
		return "", fmt.Errorf("request to %s failed with Status %d",
			tokenEndpoint, resp.StatusCode)
	}

	var token struct {
		AccessToken  string `json:"access_token"`
		IDToken      string `json:"id_token"`
		RefreshToken string `json:"refresh_token"`
		ExpiresIn    int64  `json:"expires_in"`
	}
	err = json.NewDecoder(resp.Body).Decode(&token)
	if err != nil {
		fmt.Printf("json token response error: %v\n", err)
		return "", errors.New("failed to decode token response")
	}

	fmt.Printf("Got token: %+v\n", token)

	keys, err := getPublicKeys()
	if err != nil {
		return "", err
	}
	fmt.Printf("keys: %+v\n", keys)

	parsed, err := jwt.Parse([]byte(token.AccessToken), jwt.WithKeySet(keys))
	if err != nil {
		fmt.Printf("failed to verify: %s\n", err)
		return "", errors.New("failed to verify token")
	}

	fmt.Printf("parsed: %+v", parsed)

	userName, ok := parsed.Get("username")
	if !ok {
		return "", errors.New("missing username")
	}

	retval := struct {
		IDToken      string `json:"idToken"`
		RefreshToken string `json:"refreshToken"`
		Username     string `json:"username"`
		ExpiresIn    int64  `json:"expiresIn"`
	}{
		IDToken:      token.IDToken,
		RefreshToken: token.RefreshToken,
		Username:     strings.TrimPrefix(userName.(string), "AmazonFederate_"),
		ExpiresIn:    token.ExpiresIn,
	}

	jsonData, err := json.Marshal(retval)
	if err != nil {
		return "", errors.New("failed to encode response")
	}

	return string(jsonData), nil

}
