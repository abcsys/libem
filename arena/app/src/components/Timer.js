import React,{ useState, useEffect, useRef } from 'react'

const Timer = ({ active, timeElapsed }) => {
    const [minutes, setMinutes] = useState(0)
    const [seconds, setSeconds] = useState(0)
    const start = useRef(0)

    const getTime = () => {
        timeElapsed.current += Date.now() - start.current
        start.current = Date.now()

        setMinutes(Math.floor((timeElapsed.current / 1000 / 60) % 60))
        setSeconds(Math.floor((timeElapsed.current / 1000) % 60))
    }

    const format = time => {
        return time < 10 ? '0' + time : time
    }

    useEffect(() => {
        if (active) {
            start.current = Date.now()
            const interval = setInterval(() => {
                getTime()
            }, 1000)

            return () => clearInterval(interval)
        }
        else {
            if (start.current > 0)
                getTime()
        }
    }, [active])

    return (
        <div className="timer">
            {format(minutes)}:{format(seconds)}
        </div>
    )
}

export default Timer