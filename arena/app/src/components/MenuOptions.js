import React from "react"
import "./MenuOptions.css"

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

const MenuOptions = ({ className, options, selected, setSelected }) => {
    return (
        <div className={`options ${className}`}>
            {Object.keys(options).map(key => 
                <div key={key} className={selected === key ? "option-box selected" : "option-box"} 
                     onClick={() => setSelected(key)}>
                    <MenuChild name={key} metadata={options[key]} selected={selected === key} />
                </div>
            )}
        </div>
    )
}

export default MenuOptions