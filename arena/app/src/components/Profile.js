import React, { useState } from "react"
import "./Profile.css"

const Profile = ({ name, picture, token, logout }) => {
    const [open, setOpen] = useState(false)
    const [helpWindow, setHelpWindow] = useState(false)
    const [copying, setCopying] = useState(false)

    const copy = () => {
        navigator.clipboard.writeText(token)
        setCopying(true)
        setTimeout(() => setCopying(false), 2000)
    }

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
                <div className="pad"></div>
                <div className={'hstack'} style={{width: "90%"}}>
                    <div className={`tokenbox ${copying ? "center-align" : ""}`}>
                        {copying ? "Copied" : <><b>Access token:</b> {token}</>}
                    </div>
                    <button className="svg-btn" title="Copy" onClick={copy}>
                        <svg className="copy-svg" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="-9.6 -9.6 83.20 83.20"><path d="M53.9791489,9.1429005H50.010849c-0.0826988,0-0.1562004,0.0283995-0.2331009,0.0469999V5.0228 C49.7777481,2.253,47.4731483,0,44.6398468,0h-34.422596C7.3839517,0,5.0793519,2.253,5.0793519,5.0228v46.8432999 c0,2.7697983,2.3045998,5.0228004,5.1378999,5.0228004h6.0367002v2.2678986C16.253952,61.8274002,18.4702511,64,21.1954517,64 h32.783699c2.7252007,0,4.9414978-2.1725998,4.9414978-4.8432007V13.9861002 C58.9206467,11.3155003,56.7043495,9.1429005,53.9791489,9.1429005z M7.1110516,51.8661003V5.0228 c0-1.6487999,1.3938999-2.9909999,3.1062002-2.9909999h34.422596c1.7123032,0,3.1062012,1.3422,3.1062012,2.9909999v46.8432999 c0,1.6487999-1.393898,2.9911003-3.1062012,2.9911003h-34.422596C8.5049515,54.8572006,7.1110516,53.5149002,7.1110516,51.8661003z M56.8888474,59.1567993c0,1.550602-1.3055,2.8115005-2.9096985,2.8115005h-32.783699 c-1.6042004,0-2.9097996-1.2608986-2.9097996-2.8115005v-2.2678986h26.3541946 c2.8333015,0,5.1379013-2.2530022,5.1379013-5.0228004V11.1275997c0.0769005,0.0186005,0.1504021,0.0469999,0.2331009,0.0469999 h3.9682999c1.6041985,0,2.9096985,1.2609005,2.9096985,2.8115005V59.1567993z"></path></svg>
                        </button>
                    <button className="svg-btn" title="Help" onClick={() => setHelpWindow(true)}>
                        <svg className="help-svg" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 93.936 93.936"><path d="M80.179,13.758c-18.342-18.342-48.08-18.342-66.422,0c-18.342,18.341-18.342,48.08,0,66.421 c18.342,18.342,48.08,18.342,66.422,0C98.521,61.837,98.521,32.099,80.179,13.758z M44.144,83.117 c-4.057,0-7.001-3.071-7.001-7.305c0-4.291,2.987-7.404,7.102-7.404c4.123,0,7.001,3.044,7.001,7.404 C51.246,80.113,48.326,83.117,44.144,83.117z M54.73,44.921c-4.15,4.905-5.796,9.117-5.503,14.088l0.097,2.495 c0.011,0.062,0.017,0.125,0.017,0.188c0,0.58-0.47,1.051-1.05,1.051c-0.004-0.001-0.008-0.001-0.012,0h-7.867 c-0.549,0-1.005-0.423-1.047-0.97l-0.202-2.623c-0.676-6.082,1.508-12.218,6.494-18.202c4.319-5.087,6.816-8.865,6.816-13.145 c0-4.829-3.036-7.536-8.548-7.624c-3.403,0-7.242,1.171-9.534,2.913c-0.264,0.201-0.607,0.264-0.925,0.173 s-0.575-0.327-0.693-0.636l-2.42-6.354c-0.169-0.442-0.02-0.943,0.364-1.224c3.538-2.573,9.441-4.235,15.041-4.235 c12.36,0,17.894,7.975,17.894,15.877C63.652,33.765,59.785,38.919,54.73,44.921z"></path></svg>
                    </button>
                </div>
                <div className="button rect small" onClick={logout}>Logout</div>
            </div>
            { helpWindow
                ? <>
                    <div className="background" onClick={() => setHelpWindow(false)}></div>
                    <div className="popup">
                        <div className="vstack left-align">
                            <div className="title-grid">
                                <h2 style={{margin: "5px", justifySelf: "start"}}>Access Token</h2>
                                <div style={{width: "100%"}}></div>
                                <button className="svg-btn" style={{justifySelf: "end", alignSelf: "start"}} 
                                        onClick={() => setHelpWindow(false)}>
                                    <svg className="close-svg" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460.775 460.775"><path d="M285.08,230.397L456.218,59.27c6.076-6.077,6.076-15.911,0-21.986L423.511,4.565c-2.913-2.911-6.866-4.55-10.992-4.55 c-4.127,0-8.08,1.639-10.993,4.55l-171.138,171.14L59.25,4.565c-2.913-2.911-6.866-4.55-10.993-4.55 c-4.126,0-8.08,1.639-10.992,4.55L4.558,37.284c-6.077,6.075-6.077,15.909,0,21.986l171.138,171.128L4.575,401.505 c-6.074,6.077-6.074,15.911,0,21.986l32.709,32.719c2.911,2.911,6.865,4.55,10.992,4.55c4.127,0,8.08-1.639,10.994-4.55 l171.117-171.12l171.118,171.12c2.913,2.911,6.866,4.55,10.993,4.55c4.128,0,8.081-1.639,10.992-4.55l32.709-32.719 c6.074-6.075,6.074-15.909,0-21.986L285.08,230.397z"></path></svg>
                                </button>
                            </div>
                            <div className="left-align">Include the access token as part of the authorization request header:</div>
                            <div className="tokenbox code">
                                {"Authorization: Bearer <ACCESS TOKEN>"}
                            </div>
                            <div className="left-align">Python example:</div>
                            <div className="tokenbox code">
                                requests.get("https://arena.libem.org/info", <br></br>
                                &emsp;&emsp;headers=&#123;<br></br>&emsp;&emsp;&emsp;&emsp;
                                "Authorization": "Bearer &lt;ACCESS TOKEN&gt;"<br></br>&emsp;&emsp;&#125;<br></br>
                                )
                            </div>
                            <div className="left-align">Curl example:</div>
                            <div className="tokenbox code">
                                curl https://arena.libem.org/info -H "Authorization: Bearer &lt;ACCESS TOKEN&gt;"
                            </div>
                        </div>
                    </div>
                </>
                : <></>
            }
        </>
    )
}

export default Profile