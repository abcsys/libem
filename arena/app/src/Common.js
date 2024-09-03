const baseURL = "http://127.0.0.1:8000"

const init = async () => {
    const name = "uuid="
    let uuid = ""

    // get saved uuid from cookies
    const decodedCookie = decodeURIComponent(document.cookie)
    const ca = decodedCookie.split(';')
    for(let i = 0; i <ca.length; i++) {
        let c = ca[i]
        while (c.charAt(0) == ' ') {
            c = c.substring(1)
        }
        if (c.indexOf(name) == 0) {
            uuid = c.substring(name.length, c.length)
        }
    }

    const res = await fetch(baseURL + `/init/?token=user&uuid=${uuid}`)
    if (res.ok) {
        const body = await res.json()

        // add uuid to cookies, set to expire in 40 days
        const d = new Date()
        d.setTime(d.getTime() + 40*24*60*60*1000)
        const expires = "expires=" + d.toUTCString()
        document.cookie = name + body['uuid'] + ";" + expires + ";path=/"

        return body
    }

    return {uuid: 0, benchmarks: []}
}

export { baseURL, init }