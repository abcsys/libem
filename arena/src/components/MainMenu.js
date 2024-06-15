import React from "react"
import "./MainMenu.css"

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

const MainMenu = ({ datasets, selected, setSelected, setActive, setLeaderboard }) => {
    
    return (
        <div className="vstack">
            <div className="pad"></div>
            <h1 className="logo fade-in-top">Libem Arena</h1>
            <div className="textbox fade-in-left">
                Libem is an open-source compound AI toolchain for fast and accurate entity matching, powered by LLMs.
            </div>
            <div className="textbox fade-in-left">
                Do you think you can outperform Libem? <br></br> Select a dataset, then press start to find out.
            </div>
            <div className="options fade-in-right">
                {Object.keys(datasets).map(key => 
                    <div key={key} className={selected === key ? "dataset-box selected" : "dataset-box"} onClick={() => setSelected(key)}>
                        <MenuChild name={key} metadata={datasets[key]} selected={selected === key} />
                    </div>
                )}
            </div>
            <div className="adaptive-stack">
                <div className={selected !== null 
                                    ? "button rect green fade-in-bottom" 
                                    : "button rect green fade-in-bottom inactive-green"} 
                        onClick={() => setLeaderboard(true)}>
                    Leaderboard
                </div>
                <div className={selected !== null 
                                    ? "button rect fade-in-bottom" 
                                    : "button rect fade-in-bottom inactive"} 
                        onClick={() => setActive(selected)}>
                    START
                </div>
            </div>
            
            <div className="pad"></div>
        </div>
        
        
    )
}

export default MainMenu