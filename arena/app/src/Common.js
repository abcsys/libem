const baseURL = `${process.env.BACKEND_URL}`

const getAuthToken = () => {
    const name = "auth="
    let auth_token = ""

    // check if auth token is in url
    const urlParams = new URLSearchParams(window.location.search)
    if (urlParams.has('auth')) {
        // add auth token to cookies, set to expire in 30 days
        auth_token = urlParams.get('auth')
        const d = new Date()
        d.setTime(d.getTime() + 30*24*60*60*1000)
        const expires = "Expires=" + d.toUTCString()
        document.cookie = name + auth_token + ";" + expires + ";Path=/;SameSite=Strict;"
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
                auth_token = c.substring(name.length, c.length)
            }
        }
    }

    return auth_token
}

const deleteAuthToken = () => {
    const name = "auth="
    const expires = "Expires=Thu, 01 Jan 1970 00:00:00 GMT"
    document.cookie = name + ";" + expires + ";Path=/;SameSite=Strict;"
}

const init = async () => {
    const auth_token = getAuthToken()

    // fetch
    const res = await fetch(baseURL + `/init`, {
        headers: { "Authorization": "Bearer " + auth_token }
    })
    if (res.ok) {
        const body = await res.json()
        return {token: auth_token, ...body}
    }

    return {auth: false, benchmarks: []}
}

const fetchURL = async (url, method='GET', headers={}, body=null) => {
    const auth_token = getAuthToken()

    return await fetch(baseURL + url, {
        method: method,
        headers: { Authorization: "Bearer " + auth_token, ...headers },
        body: body
    })
}

export { init, fetchURL, deleteAuthToken }