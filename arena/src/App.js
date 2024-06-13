import React, { useEffect, useRef, useState } from "react"
import { v4 as uuidv4 } from 'uuid'
import MainMenu from "./components/MainMenu"
import "./App.css"
import Selection from "./components/Selection"
import Leaderboard from "./components/Leaderboard"

const App = () => {
    const uuid = useRef(0)
    const [datasets, setDatasets] = useState(null)
    const [selected, setSelected] = useState(null)
    const [activeDS, setActiveDS] = useState(null)
    const [leaderboard, setLeaderboard] = useState(false)
    const order = useRef([])


    useEffect(() => {
        uuid.current = uuidv4()

        fetch("http://127.0.0.1:8000/init/")
        .then(r => r.json())
        .then(r => setDatasets(r))
        .catch(e => setDatasets([]))
    }, [])

    const returnHome = () => {
        // scroll to top
        window.scrollTo(0, 0)
        setActiveDS(null)
        setSelected(null)
        setLeaderboard(false)
    }

    const openLB = (dataset) => {
        // scroll to top
        window.scrollTo(0, 0)
        setActiveDS(null)
        setSelected(dataset)
        setLeaderboard(true)
    }

    const setActive = (v) => {
        const newOrder = [...Array(datasets[v]['size']).keys()]
        order.current = newOrder.sort((a, b) => 0.5 - Math.random())
        setActiveDS(v)
    }

    return (
        <>
            {activeDS === null 
                ? datasets !== null 
                    ? selected && leaderboard
                        ? <Leaderboard dataset={selected} uuid={uuid.current} returnHome={returnHome} />
                        : <MainMenu datasets={datasets} selected={selected} 
                                setSelected={setSelected} setActive={setActive}
                                setLeaderboard={setLeaderboard} /> 
                    : <></>
                : <Selection dataset={activeDS} order={order.current} size={datasets[activeDS]['size']} 
                                uuid={uuid.current} returnHome={returnHome} openLB={openLB} />
            }   
        </>
    )
}

export default App