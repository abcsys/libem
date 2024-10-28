import React from "react"
import "./Select.css"

const Select = ({ className, options, defaultValue, onChange }) => {
    return (
        <select className={`custom-select ${className}`}
                value={defaultValue}
                onChange={e => onChange(e.target.value)}>
            {options.map((o, i) => 
                <option key={i} value={o}>{o}</option>
            )}
        </select>
    )
}

export default Select