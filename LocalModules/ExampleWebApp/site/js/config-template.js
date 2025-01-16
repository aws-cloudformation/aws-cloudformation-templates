// Template variables will be replaced by buildsite.sh
const APIGATEWAY_URL = "__APIGW__"
const REDIRECT_URI = "__REDIRECT__"
const COGNITO_DOMAIN = "__DOMAIN__" 
const APP_CLIENT_ID = "__APPCLIENT__" 

const REGION = "us-east-1"
const COGNITO_URL = `https://${COGNITO_DOMAIN}.auth.${REGION}.amazoncognito.com`
const PARAMS = `?response_type=code&client_id=${APP_CLIENT_ID}&redirect_uri=${REDIRECT_URI}`
const LOGIN_URL = `${COGNITO_URL}/login${PARAMS}`
const LOGOUT_URL = `${COGNITO_URL}/logout${PARAMS}`

const LOCAL_JWT = ""

export { APIGATEWAY_URL, LOGIN_URL, LOGOUT_URL, LOCAL_JWT }
