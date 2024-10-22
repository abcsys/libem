import React, { useEffect, useRef, useState } from "react"
import { fetchURL, init } from "../Common"
import "./Leaderboard.css"
import { useNavigate, useParams } from "react-router-dom"
import ErrorPopup from "../components/ErrorPopup"
import Select from "../components/Select"

const LBEntry = ({ name, score, time, highlight, type }) => {
    const hashStr = str => {
        let hash = 0;
        str.split('').forEach(char => {
          hash += char.charCodeAt(0)
        })
        return hash
    }

    if (highlight && type !== "Model") name = "You"
    const className = highlight ? "center-text bold" : "center-text"
    const iconLetter = name === "Users Best" || name === "Users Avg" 
                        ? name.split(' ').at(-1)[0] : name[0]

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
    const [benchmarks, setBenchmarks] = useState([])
    const { dataset } = useParams()
    const uuid = useRef()
    const type = useRef()
    const [leaderboard, setLeaderboard] = useState([])
    const [animate, setAnimate] = useState(true)
    const navigate = useNavigate()

    const fetchLB = (benchmark) => {
        fetchURL(`/leaderboard?benchmark=${benchmark}`)
        .then(r => r.json())
        .then(r => setLeaderboard(r))
        .catch(r => setError(true))
    }
    
    const returnHome = () => {
        navigate("/")
    }

    const setBenchmark = (benchmark) => {
        if (benchmarks.includes(benchmark))
            navigate(`/leaderboard/${benchmark}`)
        else
            navigate(`/leaderboard/${benchmarks[0]}`)
    }
    
    useEffect(() => {
        if (dataset) {
            // Re-trigger fade in animations
            setAnimate(false)
            setTimeout(() => {
                fetchLB(dataset)
                setAnimate(true)
            }, 200)
        }
    }, [dataset])
    
    useEffect(() => {
        init()
        .then(r => {
            uuid.current = r['id']
            type.current = r['type']
            const bm = Object.keys(r['benchmarks'])
            setBenchmarks(bm)
            if (!bm.includes(dataset))
                navigate(`/leaderboard/${bm[0]}`)
            else
                fetchLB(dataset)
        })
        .catch(r => setError(true))
    }, [])

    return (
        <>
            <ErrorPopup show={error} message={"Network error encountered."} />

            <div className="vstack">
                <div className="pad"></div>
                <h1 className="text-color fade-in-top">Leaderboard</h1>
                <Select className="fade-in-left" options={benchmarks} 
                        defaultValue={dataset} onChange={setBenchmark} />
                <div className={`lb-box ${animate ? "fade-in-right" : "hide"}`}>
                    <div className="lb-entries">
                        <div className="lb-entry sticky">
                            <div></div>
                            <div className="lb-item">Name</div>
                            <div className="center-text">F1 Score</div>
                            <div className="center-text">Avg. Time</div>
                        </div>
                        {leaderboard.map((k, i) => 
                            <LBEntry key={i} name={k['name']} score={k['score']} type={type.current}
                                     time={k['avg_time']} highlight={k['id'] === uuid.current} />
                            )}
                    </div>
                </div>
                <div className={`button rect ${animate ? "fade-in-bottom" : "hide"}`} 
                     onClick={returnHome}>Home</div>
                <div className="pad"></div>
            </div>
        </>
        
    )
}

export default Leaderboard