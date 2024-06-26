import React, { useEffect, useRef, useState } from "react"
import { baseURL, getUUID } from "../Common"
import "./Leaderboard.css"
import { useNavigate, useParams } from "react-router-dom"

const LBEntry = ({ name, score, time, highlight }) => {
    const hashStr = str => {
        let hash = 0;
        str.split('').forEach(char => {
          hash += char.charCodeAt(0)
        })
        return hash
    }

    if (highlight) name = "You"
    const className = highlight ? "center-text bold" : "center-text"
    const lastname = name.split(' ').at(-1)

    return (
        <div className="lb-entry">
            <div className="avatar" 
                  style={{backgroundColor: `hsl(${hashStr(lastname)}, 90%, 65%)`}}>
                {lastname[0]}
            </div>
            <div className={highlight ? "bold lb-item" : "lb-item"}>{name}</div>
            <div className={className}>{Math.round(score)}%</div>
            <div className={className}>{Math.round(time * 100) / 100}s</div>
        </div>
    )
}

const Leaderboard = () => {
    const { dataset } = useParams()
    const uuid = useRef()
    const [leaderboard, setLeaderboard] = useState([])
    const navigate = useNavigate()
    
    const returnHome = () => {
        navigate("/")
    }

    useEffect(() => {
        uuid.current = getUUID()

        fetch(`${baseURL}/leaderboard/?dataset=${dataset}&uuid=${uuid.current}`)
        .then(r => r.json())
        .then(r => setLeaderboard(r))
    }, [])

    return (
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
                        <LBEntry key={i} name={k['name']} score={k['score']} time={k['avg_time']} highlight={k['uuid'] === uuid.current} />
                        )}
                </div>
            </div>
            <div className="button rect fade-in-bottom" onClick={returnHome}>Home</div>
            <div className="pad"></div>
        </div>
    )
}

export default Leaderboard