import React from "react"
import "./MainMenu.css"

const MenuChild = ({ name, metadata, selected }) => {
    return (
        <>
            <div className="dataset-name">{name}</div>
            {selected ? <div className="description">{metadata["description"]}</div>
            : <div></div>
            }
        </>
        
    )
}

const MainMenu = ({ datasets, selected, setSelected, setActive }) => {
    
    return (
        <div className="vstack">
            <div className="pad"></div>
            <h1>Libem Arena</h1>
            <div className="textbox">Libem is an open-source compound AI toolchain for fast and accurate entity matching, powered by LLMs. Test your judgement skills against Libem.</div>
            <div className="textbox">Select a dataset, then press start to begin.</div>
            <div className="options fade-in-left">
                {Object.keys(datasets).map(key => 
                    <div key={key} className={selected === key ? "dataset-box selected" : "dataset-box"} onClick={() => setSelected(key)}>
                        <MenuChild name={key} metadata={datasets[key]} selected={selected === key} />
                    </div>
                )}
            </div>
            <div className={selected !== null ? "button rect fade-in-right" : "button rect fade-in-right inactive"} onClick={() => setActive(selected)}>START</div>
        </div>
        
        
    )
}

export default MainMenu