import React, { useEffect, useRef, useState } from "react"
import EndScreen from "../components/EndScreen"
import Timer from "../components/Timer"
import { fetchURL, init } from "../Common"
import "./Match.css"
import { useNavigate, useParams } from "react-router-dom"
import ErrorPopup from "../components/ErrorPopup"

const EntityBox = ({ entity, className }) => {
    return (
        <div className={className}>
            <div className="vstack-left">
                {Object.keys(entity).map(key =>
                    <div key={key} className="kv-pair-tight">
                        <div className="key">
                            {key.replaceAll("_", " ").split(' ')
                                .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                                .join(' ')}:
                        </div>
                        <div className="value indent">{entity[key].length > 0 ? entity[key] : "--"}</div>
                    </div>
                )}
            </div>
        </div>
    )
}

const BackToHome = ({ show, message, returnHome, openLB }) => {
    if (show) {
        return (
            <>
                <div className={"background"}></div>
                <div className={"popup zoom-fade"}>
                    <h2>Finished</h2>
                    <p>{message}</p>
                    <p className="value">Click <b>Home</b> to try something else or <b>Leaderboard</b> to see your results.</p>
                    <div className="adaptive-stack">
                        <div className="button rect red" onClick={() => returnHome()}>Home</div>
                        <div className="button rect green" onClick={() => openLB()}>Leaderboard</div>
                    </div>
                </div>
            </>
        )
    }
    return (<></>)
}

const ResultScreen = ({ userAns, libemAns, label, index, final, inactive, closeResultScreen, setEndScreen }) => {

    const [hide, setHide] = useState(false)
    const resultDiv = useRef(null)

    const collapse = () => {
        resultDiv.current.className = "popup to-bottom select"
        setHide(true)
    }
    const expand = () => {
        resultDiv.current.className = "popup"
        setHide(false)
    }

    const resultClasses = inactive 
                            ? "popup hidden" 
                            : userAns === label 
                                ? "popup zoom-fade"
                                : "popup shake-fade"

    return (
        <>
            <div className={inactive || hide ? "background hidden" : "background"} onClick={collapse}></div>
            
            <div className={resultClasses} ref={resultDiv} onClick={expand}>
                { !hide && !inactive 
                    ? <div>
                        {userAns === label
                            ? <>
                                <h2>Correct!</h2>
                                <div>You chose <b>{userAns ? "Match" : "No Match"}</b>, which was correct.</div>
                            </>
                            : <>
                                <h2>Not Quite!</h2>
                                <div>You chose <b>{userAns ? "Match" : "No Match"}</b>, which was wrong.</div>
                            </>
                        }
                        <div>Libem chose <b>{libemAns ? "Match" : "No Match"}</b>.</div>
                        
                        {!final
                            ? index < 5
                                ? <p className="value">Click <b>Next</b> to try another pair, you may end any time after 5 pairs.</p>
                                : <p className="value">Click <b>Next</b> to try another pair, 
                                    or <b>End</b> to see your final results.</p>
                            : <p className="value">You have finished matching all pairs. Click <b>End</b> to see your final results.</p>
                        }
                    </div>
                    : <></>
                }
                
                <div className="hstack">
                    {index >= 4 || final
                        ? <div className="button rect red" onClick={() => setEndScreen(true)}>End</div>
                        : <></>
                    }
                    {
                        final
                        ? <></>
                        : <div className="button rect green" onClick={closeResultScreen}>Next</div>
                    }
                </div>
            </div>
        </>
        
    )
}

const Match = () => {
    const [error, setError] = useState(false)
    const { dataset } = useParams()
    const uuid = useRef()
    const [pair, setPair] = useState(null)
    const [numPairs, setnumPairs] = useState(null)
    const [index, setIndex] = useState(0)
    const [resultScreen, setResultScreen] = useState(false)
    const [endScreen, setEndScreen] = useState(false)
    const [noContent, setNoContent] = useState(false)

    const userAns = useRef([])
    const libemAns = useRef([])
    const libemTime = useRef(0)
    const labels = useRef([])

    const [timer, setTimer] = useState(false)
    const timeElapsed = useRef(0)
    const startTime = useRef(0)
    const navigate = useNavigate()

    const ex =  <svg viewBox='0 0 50 50' className={'icon'}>
                    <path d="M 12 12 L 38 38"/>
                    <path d="M 12 38 L 38 12"/>
                </svg>
    const check = <svg viewBox='0 0 50 50' className={'icon'}>
                    <path d="M 22 38 L 40 12"/>
                    <path d="M 10 25 L 22 38"/>
                 </svg>
    
    const returnHome = () => {
        navigate("/")
    }

    const openLB = () => {
        navigate(`/leaderboard/${dataset}`)
    }

    const fetchNext = () => {
        if (index >= 0) {
            fetchURL(`/matchone?benchmark=${dataset}`)
            .then(r => {
                if (r.status === 204)
                    throw Error("No content")
                else if (r.status === 401)
                    throw Error("Not authorized")
                return r.json()
            })
            .then(r => {
                // scroll to top
                window.scrollTo(0, 0)

                startTime.current = Date.now()
                setIndex(r['index'])
                setPair({left: r['left'], right: r['right']})
                setTimer(true)
            })
            .catch(r => {
                if (r.message === "No content")
                    setNoContent(true)
                else if (r.message === "Not authorized")
                    returnHome()
                else
                    setError(true)
            })
        }
    }

    const closeResultScreen = () => {
        fetchNext()
        setResultScreen(false)
    }

    const match = (answer) => {
        fetchURL('/submitone',
            "POST",
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            JSON.stringify({
                benchmark: dataset,
                answer: answer,
                time: (Date.now() - startTime.current) / 1000
            }))
        .then(r => r.json())
        .then(r => {
            userAns.current.push(answer)
            libemAns.current.push(r['libem_pred'])
            libemTime.current += r['libem_time']
            labels.current.push(r['label'] === 1)
            setTimer(false)
            setResultScreen(true)
        })
        .catch(r => setError(true))
    }

    useEffect(() => {
        init()
        .then(r => {
            uuid.current = r['id']
            setnumPairs(r['benchmarks'][dataset]['size'])
            fetchNext()
        })
        .catch(r => setError(true))
    }, [])

    return (
        <>
            <ErrorPopup show={error} message={"Network error encountered."} />
            <BackToHome show={noContent} message={`You have already matched all the pairs in the ${dataset} dataset.`} 
                        returnHome={returnHome} openLB={openLB} />

            {endScreen
                ? <EndScreen uuid={uuid.current} dataset={dataset} userAns={userAns.current} libemAns={libemAns.current} 
                             userTime={timeElapsed.current / 1000} libemTime={libemTime.current} 
                             labels={labels.current} returnHome={returnHome} openLB={openLB} />
                : <div className="selection">
                    {pair === null 
                        ? <></>
                        : <div className="vstack-wide">
                            <div className="vstack fade-in-top">
                                <div className="title-bar">
                                    <div className="title-left">Pair: {index+1}</div>
                                    <div>{dataset}</div>
                                    <div className="title-right">
                                        <Timer active={timer} timeElapsed={timeElapsed} />
                                    </div>
                                </div>
                                <div className="textbox">
                                    Use your best judgement to determine whether the following two entities 
                                    are referring to the same real-world entity.
                                </div>
                            </div>
                            <div className="adaptive-stack">
                                <EntityBox entity={pair['left']} className={resultScreen ? "entity-box" : "entity-box fade-in-left"} />
                                <EntityBox entity={pair['right']} className={resultScreen ? "entity-box" : "entity-box fade-in-right"} />
                            </div>
                            <div className={resultScreen ? "hstack" : "hstack fade-in-bottom"}>
                                <div className={`button circle red ${resultScreen ? "inactive-red" : ""}`} 
                                     onClick={() => match(false)}>{ex}</div>
                                <div className={`button circle green ${resultScreen ? "inactive-green" : ""}`} 
                                     onClick={() => match(true)}>{check}</div>
                            </div>
                            <div className="pad"></div>
                          </div>}
                    <ResultScreen userAns={userAns.current.at(-1)} libemAns={libemAns.current.at(-1)} 
                                label={labels.current.at(-1)} index={index} final={index+1 >= numPairs} 
                                inactive={!resultScreen} closeResultScreen={closeResultScreen} setEndScreen={setEndScreen} />
                  </div>
            }
        </> 
    )

}

export default Match