import React, { useEffect, useRef, useState } from "react"
import "./Selection.css"
import Timer from "./Timer"

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

const ResultScreen = ({ userAns, libemAns, label, hidden, closeResultScreen, setEndScreen }) => {

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
                    <p className="value">Click <b>Next</b> to try another pair, or <b>End</b> to compare your results.</p>
                </div>
                <div className="hstack">
                    <div className="button red" onClick={() => setEndScreen(true)}>End</div>
                    <div className="button green" onClick={closeResultScreen}>Next</div>
                </div>
            </div>
        </>
        
    )
}

const EndScreen = ({ userAns, libemAns, userTime, libemTime, labels, returnHome }) => {
    const labelsTrue = labels.filter(Boolean).length
    const userAnsTrue = userAns.filter(Boolean).length
    const userActualTrue = userAns.filter((x, i) => x && labels[i]).length
    const userCorrect = userAns.filter((x, i) => x === labels[i]).length
    const userPrecision = userAnsTrue === 0 ? 0 : userActualTrue / userAnsTrue
    const userRecall = labelsTrue === 0 ? 0 : userActualTrue / labelsTrue
    const userF1 = userPrecision + userRecall === 0
                    ? 0 
                    : 2 * userPrecision * userRecall / (userPrecision + userRecall)

    const libemAnsTrue = libemAns.filter(Boolean).length
    const libemActualTrue = libemAns.filter((x, i) => x && labels[i]).length
    const libemCorrect = libemAns.filter((x, i) => x === labels[i]).length
    const libemPrecision = libemAnsTrue === 0 ? 0 :  libemActualTrue / libemAnsTrue
    const libemRecall = labelsTrue === 0 ? 0 : libemActualTrue / labelsTrue
    const libemF1 = libemPrecision + libemRecall === 0
                    ? 0 
                    : 2 * libemPrecision * libemRecall / (libemPrecision + libemRecall)

    const userMetrics = {
        accuracy: Math.round(userCorrect / userAns.length * 100) + '%',
        precision: Math.round(userPrecision * 100) + '%',
        recall: Math.round(userRecall * 100) + '%',
        f1: Math.round(userF1 * 100) + '%',
        average_time: Math.round(userTime / userAns.length * 100) / 100 + 's',
        total_time: Math.round(userTime * 100) / 100 + 's',
    }
    const libemMetrics = {
        accuracy: Math.round(libemCorrect / libemAns.length * 100) + '%',
        precision: Math.round(libemPrecision * 100) + '%',
        recall: Math.round(libemRecall * 100) + '%',
        f1: Math.round(libemF1 * 100) + '%',
        average_time: Math.round(libemTime / libemAns.length * 100) / 100 + 's',
        total_time: Math.round(libemTime * 100) / 100 + 's',
    }

    const kvClassName = key => {
        if (key === 'accuracy' || key === 'precision' || key === 'average_time')
            return "kv_pair margin-top"
        else
            return "kv_pair"
    }

    return (
        <div className="center">
            <div className="pad"></div>
            <h1 className="fade-in-top">Final Results</h1>
            <div className="adaptive-stack">
                <div className="stats-box fade-in-left">
                    <h2>You</h2>
                    {Object.keys(userMetrics).map(key =>
                        <div key={key} className={kvClassName(key)}>
                            <div className="key">
                                {key.replaceAll("_", " ").split(' ')
                                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                                    .join(' ')}
                            </div>
                            <div className="value">{userMetrics[key]}</div>
                        </div>
                    )}
                </div>
                <div className="stats-box fade-in-right">
                <h2>Libem</h2>
                    {Object.keys(libemMetrics).map(key =>
                        <div key={key} className={kvClassName(key)}>
                            <div className="key">
                                {key.replaceAll("_", " ").split(' ')
                                    .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
                                    .join(' ')}
                            </div>
                            <div className="value">{libemMetrics[key]}</div>
                        </div>
                    )}
                </div>
            </div>
            <div className="button fade-in-bottom" onClick={returnHome}>Home</div>
        </div>
        
    )
}

const Selection = ({ dataset, size, uuid, returnHome }) => {
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
    
    const fetchNext = () => {
        fetch(`http://127.0.0.1:8000/fetch?dataset=${dataset}&index=${index}`)
        .then(r => r.json())
        .then(r => {
            setPair(r)
            setTimer(true)
        })
    }

    const closeResultScreen = () => {
        setResultScreen(false)
        setIndex(index + 1)
    }

    const match = (answer) => {
        fetch(`http://127.0.0.1:8000/submit`, {
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
            <div className="header indent select" onClick={returnHome}>Libem Arena</div>
            {endScreen
                ? <EndScreen userAns={userAns.current} libemAns={libemAns.current} userTime={timeElapsed.current / 1000}
                            libemTime={libemTime.current} labels={labels.current} returnHome={returnHome} />
                : <div className="selection">
                    {pair === null 
                        ? <div>Loading...</div>
                        : <div className="vstack-wide">
                            <div className="vstack fade-in-top">
                                <div className="title-bar">
                                    <div className="title-left">{index+1}/{size}</div>
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
                            <div className={resultScreen ? "adaptive-stack" : "adaptive-stack fade-in-bottom"}>
                                <div className="button red" onClick={() => match(false)}>No Match</div>
                                <div className="button green" onClick={() => match(true)}>Match</div>
                            </div>
                          </div>}
                    <ResultScreen userAns={userAns.current.at(-1)} libemAns={libemAns.current.at(-1)} 
                                label={labels.current.at(-1)} hidden={!resultScreen} 
                                closeResultScreen={closeResultScreen} setEndScreen={setEndScreen} />
                  </div>
            }
        </> 
    )

}

export default Selection