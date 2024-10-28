import React from 'react'

const ErrorPopup = ({ show, message }) => {
    if (show) {
        return (
            <>
                <div className={"background"}></div>
                <div className={"popup"} >
                    <h2>Error</h2>
                    <p>{message}</p>
                    <p style={{color: '#666'}}>Please try again later.</p>
                </div>
            </>
        )
    }
    return (<></>)
}

export default ErrorPopup