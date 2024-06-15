import React, { useEffect, useRef, useState } from "react"
import EndScreen from "./EndScreen"
import Timer from "./Timer"
import baseURL from "../Constants"
import "./Selection.css"

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

const ResultScreen = ({ userAns, libemAns, label, index, final, hidden, closeResultScreen, setEndScreen }) => {

    const resultClasses = hidden 
                            ? "result hidden" 
                            : userAns === label 
                                ? "result zoom-fade" 
                                : "result shake-fade"

    return (
        <>
            <div className={hidden ? "background hidden" : "background"} onClick={closeResultScreen}></div>
            <div className={resultClasses}>
                <div className="result-message">
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
                    {index >= 4
                        ? final
                            ? <p className="value">That was the final pair. Click <b>End</b> to see your final results.</p>
                            : <p className="value">Click <b>Next</b> to try another pair, 
                                or <b>End</b> to see your final results.</p>
                        : <p className="value">Click <b>Next</b> to try another pair, you may end any time after 5 pairs.</p>
                    }
                    
                </div>
                <div className="hstack">
                    {index >= 4
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

const Selection = ({ dataset, order, uuid, returnHome, openLB }) => {
    const [pair, setPair] = useState(null)
    const [index, setIndex] = useState(0)
    const [resultScreen, setResultScreen] = useState(false)
    const [endScreen, setEndScreen] = useState(false)

    const userAns = useRef([])
    const libemAns = useRef([])
    const libemTime = useRef(0)
    const labels = useRef([])

    const [timer, setTimer] = useState(false)
    const timeElapsed = useRef(0)

    const ex =  <svg viewBox='0 0 50 50' className={'icon'}>
                    <path d="M 12 12 L 38 38"/>
                    <path d="M 12 38 L 38 12"/>
                </svg>
    const check = <svg viewBox='0 0 50 50' className={'icon'}>
                    <path d="M 22 38 L 40 12"/>
                    <path d="M 10 25 L 22 38"/>
                 </svg>
    
    const fetchNext = () => {
        fetch(`${baseURL}/fetch?dataset=${dataset}&index=${order[index]}`)
        .then(r => r.json())
        .then(r => {
            // scroll to top
            window.scrollTo(0, 0)
            setPair(r)
            setTimer(true)
        })
    }

    const closeResultScreen = () => {
        setResultScreen(false)
        setIndex(index + 1)
    }

    const match = (answer) => {
        fetch(`${baseURL}/submit/`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                uuid: uuid,
                dataset: dataset,
                index: index,
                answer: answer
            })
        })
        .then(r => r.json())
        .then(r => {
            userAns.current.push(answer)
            libemAns.current.push(r['libem_pred'])
            libemTime.current += pair['libem_time']
            labels.current.push(r['label'] === 1)
            setTimer(false)
            setResultScreen(true)
        })
    }

    useEffect(fetchNext, [index])

    return (
        <>
            {endScreen
                ? <EndScreen uuid={uuid} dataset={dataset} userAns={userAns.current} libemAns={libemAns.current} 
                             userTime={timeElapsed.current / 1000} libemTime={libemTime.current} 
                             labels={labels.current} returnHome={returnHome} openLB={openLB} />
                : <div className="selection">
                    {pair === null 
                        ? <div>Loading...</div>
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
                                <div className="button circle red" onClick={() => match(false)}>{ex}</div>
                                <div className="button circle green" onClick={() => match(true)}>{check}</div>
                            </div>
                            <div className="pad"></div>
                          </div>}
                    <ResultScreen userAns={userAns.current.at(-1)} libemAns={libemAns.current.at(-1)} 
                                label={labels.current.at(-1)} index={index} final={index+1 === order.length} 
                                hidden={!resultScreen} closeResultScreen={closeResultScreen} setEndScreen={setEndScreen} />
                  </div>
            }
        </> 
    )

}

export default Selection