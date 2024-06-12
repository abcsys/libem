import React, { useEffect, useRef, useState } from "react"
import { v4 as uuidv4 } from 'uuid'
import MainMenu from "./components/MainMenu"
import "./App.css"
import Selection from "./components/Selection"

const App = () => {
    const uuid = useRef(0)
    const [datasets, setDatasets] = useState(null)
    const [selected, setSelected] = useState(null)
    const [activeDS, setActiveDS] = useState(null)


    useEffect(() => {
        uuid.current = uuidv4()

        fetch("http://127.0.0.1:8000/init")
        .then(r => r.json())
        .then(r => setDatasets(r))
    }, [])

    const returnHome = () => {
        setActiveDS(null)
        setSelected(null)
    }

    return (
        <>
            {activeDS === null 
                ? datasets !== null 
                    ? <MainMenu datasets={datasets} selected={selected} 
                            setSelected={setSelected} setActive={setActiveDS} /> 
                    : <></>
                : <Selection dataset={activeDS} size={datasets[activeDS]['size']} 
                                uuid={uuid.current} returnHome={returnHome} />
            }   
        </>
        
    )
}

export default App