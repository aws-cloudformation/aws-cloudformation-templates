
/**
 * Get url parameters.
 */
function getParameterByName(name, url) {
    if (!url) url = window.location.href
    // name = name.replace(/[\[\]]/g, '\\$&')
    // eslint warning.. ?
    name = name.replace(/[[]]/g, "\\$&")
    const regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)")
    const results = regex.exec(url)
    if (!results) return null
    if (!results[2]) return ""
    return decodeURIComponent(results[2].replace(/\+/g, " "))
}


/**
 * Debounce a function (wait for more input)
 */
function debounce(f, t = 1000) {
    console.log("debounce")
    let timer
    return (...args) => {
        console.log(`About to clear timeout ${timer}`)
        clearTimeout(timer)
        timer = setTimeout(() => { 
            console.log("Calling debounce timeout function")    
            f.apply(this, args) 
        }, t)
    }
}

export { getParameterByName, debounce }
