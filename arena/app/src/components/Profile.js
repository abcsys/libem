import React, { useState } from "react"
import "./Profile.css"

const Profile = ({ name, picture, logout }) => {
    const [open, setOpen] = useState(false)

    return (
        <>
            {open
                ? <div className="invis-background" 
                       onClick={() => setOpen(false)}></div>
                : <></>
            }
            <div className="profile" onClick={() => setOpen(!open)}>
                <img src={picture} />
            </div>
            <div className={`profile-dropdown ${open ? "" : "tiny"}`}>
                <div className="profile-grid">
                    <div className="profile-name">{name}</div>
                    <div></div>
                </div>
                <div className="button rect small" onClick={logout}>Logout</div>
            </div>
        </>
    )
}

export default Profile