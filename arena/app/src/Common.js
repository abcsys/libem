const baseURL = `${process.env.BACKEND_URL}`

const getAuthToken = () => {
    const name = "auth="
    let authToken = ""

    // check if auth token is in url
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.has('auth')) {
        // add auth token to cookies, set to expire in 30 days
        authToken = urlParams.get('auth')
        const d = new Date()
        d.setTime(d.getTime() + 30*24*60*60*1000)
        const expires = "Expires=" + d.toUTCString()
        document.cookie = name + authToken + ";" + expires + ";Path=/;SameSite=Strict;"
    }
    else {
        // check if auth token is in cookies
        const decodedCookie = decodeURIComponent(document.cookie)
        const ca = decodedCookie.split(';')
        for(let i = 0; i <ca.length; i++) {
            let c = ca[i]
            while (c.charAt(0) == ' ') {
                c = c.substring(1)
            }
            if (c.indexOf(name) == 0) {
                authToken = c.substring(name.length, c.length)
            }
        }
    }

    return authToken
}

const getAccessToken = () => {
    const name = "token="
    let accessToken = ""

    // check if access token is in url
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.has('token')) {
        // add access token to cookies, set to expire in 30 days
        accessToken = urlParams.get('token')
        const d = new Date()
        d.setTime(d.getTime() + 30*24*60*60*1000)
        const expires = "Expires=" + d.toUTCString()
        document.cookie = name + accessToken + ";" + expires + ";Path=/;SameSite=Strict;"
    }
    else {
        // check if auth token is in cookies
        const decodedCookie = decodeURIComponent(document.cookie)
        const ca = decodedCookie.split(';')
        for(let i = 0; i <ca.length; i++) {
            let c = ca[i]
            while (c.charAt(0) == ' ') {
                c = c.substring(1)
            }
            if (c.indexOf(name) == 0) {
                accessToken = c.substring(name.length, c.length)
            }
        }
    }

    return accessToken
}

const deleteTokens = () => {
    const expires = "Expires=Thu, 01 Jan 1970 00:00:00 GMT"
    document.cookie = "auth=;" + expires + ";Path=/;SameSite=Strict;"
    document.cookie = "token=;" + expires + ";Path=/;SameSite=Strict;"
}

const init = async () => {
    const authToken = getAuthToken()
    const accessToken = getAccessToken()

    // fetch
    const res = await fetch(baseURL + `/info`, {
        headers: { "Authorization": "Bearer " + authToken }
    })
    if (res.ok) {
        const body = await res.json()
        return {token: accessToken, ...body}
    }

    return {auth: false, benchmarks: []}
}

const fetchURL = async (url, method='GET', headers={}, body=null) => {
    const authToken = getAuthToken()

    return await fetch(baseURL + url, {
        method: method,
        headers: { Authorization: "Bearer " + authToken, ...headers },
        body: body
    })
}

export { init, fetchURL, deleteTokens }