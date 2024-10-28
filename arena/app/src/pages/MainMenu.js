import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import ErrorPopup from "../components/ErrorPopup"
import { deleteTokens, init } from "../Common"
import libby from "../../public/libby.png"
import MenuOptions from "../components/MenuOptions"
import Profile from "../components/Profile"

const MainMenu = () => {
    const [error, setError] = useState(false)
    const [loggedin, setLoggedin] = useState(false)
    const [user, setUser] = useState({})
    const [datasets, setDatasets] = useState()
    const [selected, setSelected] = useState(null)
    const navigate = useNavigate()

    const login = () => {
        window.location.href = `${process.env.BACKEND_URL}/login`
    }

    const logout = () => {
        deleteTokens()
        navigate("/")
        location.reload()
    }

    const openLB = () => {
        if (selected)
            navigate(`/leaderboard/${selected}`)
    }

    const openMatch = () => {
        if (selected)
            navigate(`/match/${selected}`)
    }

    useEffect(() => {
        init()
        .then(r => {
            if (r['auth']) {
                setLoggedin(true)
                setUser(r)
                setDatasets(r['benchmarks'])
            }
            else
                setSelected("0")
        })
        .catch(r => setError(true))
    }, [])
    
    return (
        <>
            <ErrorPopup show={error} message={"Network error encountered."} />

            {loggedin
                ? <Profile name={user['name']} picture={user['avatar']} 
                           token={user['token']} logout={logout} />
                : <></>
            }

            <div className="vstack">
                <div className="pad"></div>
                <div className="vstack fade-in-top" style={{gap: "0.5em"}}>
                    <img src={libby} height={"100px"} width={"100px"}></img>
                    <div className="logo" style={{color: "#fff"}}>Libem Arena</div>
                </div>
                <div className="textbox fade-in-left">
                    A benchmarking tool for humans and models on entity matching.
                </div>
                {loggedin 
                    ? <>
                        <div className="textbox fade-in-left" key="human-text">
                            Do you think you can outperform Libem? <br></br> Select a dataset, then click start to find out.
                        </div>
                        {datasets
                            ? <MenuOptions className="fade-in-right" key="datasets" options={datasets} 
                                            selected={selected} setSelected={setSelected} />
                            : <></>}
                    </>
                    : <div className="textbox fade-in-right">
                        You are not logged in.
                    </div>}
                
                <div className="adaptive-stack" style={{minHeight: "8em"}}>
                    <div className={selected !== null 
                                        ? "button rect green fade-in-bottom" 
                                        : "button rect green fade-in-bottom inactive-green"} 
                            onClick={openLB}>
                        Leaderboard
                    </div>
                    {loggedin
                        ? <div className={selected !== null 
                                            ? "button rect fade-in-bottom" 
                                            : "button rect fade-in-bottom inactive"} 
                                onClick={openMatch}>
                            START
                        </div>
                        : <div className="button rect fade-in-bottom" style={{width: '300px'}}
                         onClick={login}>Login with Google
                        </div>}
                </div>
                
                <div className="pad"></div>
            </div>
        </>
    )
}

export default MainMenu