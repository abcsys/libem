import React, { useEffect } from "react"
import "./EndScreen.css"

const EndScreen = ({ uuid, dataset, userAns, libemAns, userTime, 
                        libemTime, labels, returnHome, openLB }) => {
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

    useEffect(() => {
        // scroll to top
        window.scrollTo(0, 0)
        
        fetch(`http://127.0.0.1:8000/leaderboard/`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                uuid: uuid,
                name: "A",
                dataset: dataset,
                pairs: userAns.length,
                score: userCorrect / userAns.length * 100,
                avg_time: userTime
            })
        })}
    , [])

    return (
        <div className="vstack">
            <div className="pad"></div>
            <h1 className="text-color fade-in-top">Final Results</h1>
            <div className="textbox fade-in-top">
                You attempted {userAns.length} pair{userAns.length === 1 ? "" : "s"}.
            </div>
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
            <div className="adaptive-stack">
                <div className="button rect green fade-in-bottom" onClick={() => openLB(dataset)}>Leaderboard</div>
                <div className="button rect fade-in-bottom" onClick={returnHome}>Home</div>
            </div>
            
            <div className="pad"></div>
        </div>
        
    )
}

export default EndScreen