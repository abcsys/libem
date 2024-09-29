import React, { useEffect, useRef, useState } from "react"
import { baseURL, init } from "../Common"
import "./Leaderboard.css"
import { useNavigate, useParams } from "react-router-dom"
import ErrorPopup from "../components/ErrorPopup"

const LBEntry = ({ uuid, name, score, time, highlight }) => {
    const hashStr = str => {
        let hash = 0;
        str.split('').forEach(char => {
          hash += char.charCodeAt(0)
        })
        return hash
    }

    if (highlight) name = "You"
    const className = highlight ? "center-text bold" : "center-text"
    const iconLetter = uuid === '1' || uuid === '2' ? name.split(' ').at(-1)[0] : name[0]

    return (
        <div className="lb-entry">
            <div className="avatar" 
                  style={{backgroundColor: `hsl(${hashStr(name)}, 60%, 70%)`}}>
                {iconLetter}
            </div>
            <div className={highlight ? "bold lb-item" : "lb-item"}>{name}</div>
            <div className={className}>{Math.round(score)}%</div>
            <div className={className}>{Math.round(time * 100) / 100}s</div>
        </div>
    )
}

const Leaderboard = () => {
    const [error, setError] = useState(false)
    const { dataset } = useParams()
    const uuid = useRef()
    const [leaderboard, setLeaderboard] = useState([])
    const navigate = useNavigate()
    
    const returnHome = () => {
        navigate("/")
    }
    

    useEffect(() => {
        init()
        .then(r => {
            uuid.current = r['uuid']
            return fetch(`${baseURL}/leaderboard?benchmark=${dataset}&uuid=${uuid.current}`)
        })
        .then(r => r.json())
        .then(r => setLeaderboard(r))
        .catch(r => setError(true))
    }, [])

    return (
        <>
            <ErrorPopup show={error} message={"Network error encountered."} />

            <div className="vstack">
                <div className="pad"></div>
                <h1 className="text-color fade-in-top">Leaderboard</h1>
                <div className="textbox fade-in-left">{dataset}</div>
                <div className="lb-box fade-in-right">
                    <div className="lb-entries">
                        <div className="lb-entry sticky">
                            <div></div>
                            <div className="lb-item">Name</div>
                            <div className="center-text">F1 Score</div>
                            <div className="center-text">Avg. Time</div>
                        </div>
                        {leaderboard.map((k, i) => 
                            <LBEntry uuid={k['uuid']} key={i} name={k['name']} score={k['score']} 
                                     time={k['avg_time']} highlight={k['uuid'] === uuid.current} />
                            )}
                    </div>
                </div>
                <div className="button rect fade-in-bottom" onClick={returnHome}>Home</div>
                <div className="pad"></div>
            </div>
        </>
        
    )
}

export default Leaderboard