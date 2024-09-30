import React, { useState, useEffect } from "react"
import "./MainMenu.css"
import { useNavigate } from "react-router-dom"
import ErrorPopup from "../components/ErrorPopup"
import { init } from "../Common"
import libby from "../../public/libby.png"

const MenuChild = ({ name, metadata, selected }) => {
    const className = name === "Challenging" ? "dataset-name red-text" : "dataset-name"
    return (
        <>
            <div className={className}>{name}</div>
            {selected ? <div className="description">{metadata["description"]}</div>
            : <div></div>
            }
        </>
        
    )
}

const MainMenu = () => {
    const [error, setError] = useState(false)
    const [datasets, setDatasets] = useState([])
    const [selected, setSelected] = useState(null)
    const navigate = useNavigate()

    const openLB = () => {
        navigate(`/leaderboard/${selected}`)
    }

    const openMatch = () => {
        navigate(`/match/${selected}`)
    }

    useEffect(() => {
        init()
        .then(r => setDatasets(r['benchmarks']))
        .catch(r => setError(true))
    }, [])
    
    return (
        <>
            <ErrorPopup show={error} message={"Network error encountered."} /> 

            <div className="vstack">
                <div className="pad"></div>
                <div className="vstack fade-in-top" style={{gap: "0.5em"}}>
                    <img src={libby} height={"100px"} width={"100px"}></img>
                    <div className="logo" style={{color: "#fff"}}>Libem Arena</div>
                </div>
                <div className="textbox fade-in-left">
                    Libem is an open-source compound AI toolchain for fast and accurate entity matching, powered by LLMs.
                </div>
                <div className="textbox fade-in-left">
                    Do you think you can outperform Libem? <br></br> Select a dataset, then click start to find out.
                </div>
                <div className="options fade-in-right">
                    {datasets !== null 
                        ? Object.keys(datasets).map(key => 
                            <div key={key} className={selected === key ? "dataset-box selected" : "dataset-box"} onClick={() => setSelected(key)}>
                                <MenuChild name={key} metadata={datasets[key]} selected={selected === key} />
                            </div>)
                        : <></>}
                </div>
                <div className="adaptive-stack" style={{minHeight: "8em"}}>
                    <div className={selected !== null 
                                        ? "button rect green fade-in-bottom" 
                                        : "button rect green fade-in-bottom inactive-green"} 
                            onClick={openLB}>
                        Leaderboard
                    </div>
                    <div className={selected !== null 
                                        ? "button rect fade-in-bottom" 
                                        : "button rect fade-in-bottom inactive"} 
                            onClick={openMatch}>
                        START
                    </div>
                </div>
                
                <div className="pad"></div>
            </div>
        </>
    )
}

export default MainMenu