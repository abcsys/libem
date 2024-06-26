import { v4 as uuidv4 } from 'uuid'

const baseURL = "http://127.0.0.1:8000"

const getUUID = () => {
    const name = "uuid="
    let uuid = ""

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

    if (uuid === "") {
        uuid = uuidv4()
    }

    const d = new Date()
    d.setTime(d.getTime() + 40*24*60*60*1000)
    const expires = "expires=" + d.toUTCString()
    document.cookie = name + uuid + ";" + expires + ";path=/"

    return uuid
}

export { baseURL, getUUID }