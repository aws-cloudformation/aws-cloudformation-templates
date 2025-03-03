// This is a minimal example of how to handle the auth flow with Cognito and 
// then interact with DynamoDB once the user is logged in.

import { checkAuthCode } from "./auth"
import { LOGIN_URL, LOGOUT_URL } from "./config"
import * as restApi from "./rest-api"

(async function main() {

    const loginBtn = get("login-btn")
    loginBtn.onclick = function() {
        location.href = LOGIN_URL;
    }

    const logoutBtn = get("logout-btn")
    logoutBtn.onclick = function() {
        location.href = LOGOUT_URL
    }

    const testBtn = get("test-btn")
    testBtn.onclick = async function() {
        hide("about")
        show("test-data")
        show("loading")
        const data = await restApi.get("test", null, null, true)
        console.log("test data: " + JSON.stringify(data, null, 0))
        hide("loading")
        /*
         * [
         *   {
         *     "foo": {
         *       "Value":"1"
         *     },
         *     "id": {
         *       "Value":"abc"
         *     }
         *   },
         *   {
         *     "foo": {
         *       "Value":"2"
         *     },
         *     "id": {
         *       "Value":"def"
         *     }
         *   }
         * ]
         */
        const tbl = get("test-table")
        // Clear prior data
        for (let i = tbl.rows.length - 1; i > 0; i--) {
            tbl.deleteRow(i)
        }
        for (let i = 0; i < data.length; i++) {
            const d = data[i]
            const id = d.id.Value
            let foo = ""
            if (d.Foo) {
                foo = d.Foo.Value
            }
            let bar = ""
            if (d.Bar) {
                bar = d.Bar.Value
            }
            // Create a new table row
            const row = tbl.insertRow()
            const idCell = row.insertCell(0)
            idCell.innerHTML = id
            const fooCell = row.insertCell(1)
            fooCell.innerHTML = foo
            const barCell = row.insertCell(2)
            barCell.innerHTML = bar
        }
    }

    // Check to see if we're logged in
    const isCognitoRedirect = await checkAuthCode()
    if (isCognitoRedirect) {
        console.log("Cognito redirect")
        return // checkAuthCode does a redirect to /
    } else {
        console.log("Not a Cognito redirect")

    }

})()

function get(id) {
    return document.getElementById(id)
}

function show(id) {
    const elem = get(id)
    if (elem) {
        elem.style.display = "block";
    }
}

function hide(id) {
    const elem = get(id)
    if (elem) {
        elem.style.display = "none";
    }
}
