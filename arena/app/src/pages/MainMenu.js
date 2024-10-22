import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import ErrorPopup from "../components/ErrorPopup"
import { deleteAuthToken, fetchURL, init } from "../Common"
import libby from "../../public/libby.png"
import MenuOptions from "../components/MenuOptions"
import TokenBox from "../components/TokenBox"
import Profile from "../components/Profile"

const MainMenu = () => {
    const [error, setError] = useState(false)
    const [loggedin, setLoggedin] = useState(false)
    const [user, setUser] = useState({})
    const [userType, setUserType] = useState()
    const [hasUserType, setHasUserType] = useState(false)
    const [userTypes, setUserTypes] = useState()
    const [datasets, setDatasets] = useState()
    const [selected, setSelected] = useState(null)
    const navigate = useNavigate()

    const login = () => {
        window.location.href = `${process.env.BACKEND_URL}/login`
    }

    const logout = () => {
        deleteAuthToken()
        navigate("/")
        location.reload()
    }

    const updateUserType = () => {
        fetchURL(`/init?type=${userType}`)
        .then(r => {
            setHasUserType(true)
        })
        .catch(r => setError(true))
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
                if (r['type']) {
                    setHasUserType(true)
                    setUserType(r['type'])
                }
                setUserTypes(r['user_types'])
                setDatasets(r['benchmarks'])
            }
        })
        .catch(r => setError(true))
    }, [])
    
    return (
        <>
            <ErrorPopup show={error} message={"Network error encountered."} />

            {loggedin
                ? <Profile name={user['name']} picture={user['avatar']} logout={logout} />
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
                    ? hasUserType 
                        ? <>
                            {userType !== "Model"
                                ? <div className="textbox fade-in-left" key="human-text">
                                    Do you think you can outperform Libem? <br></br> Select a dataset, then click start to find out.
                                </div>
                                : <TokenBox className="fade-in-left" token={user['token']} />
                            }
                            {datasets
                                ? <MenuOptions className="fade-in-right" key="datasets" options={datasets} 
                                               selected={selected} setSelected={setSelected} />
                                : <></>}
                            <div className="adaptive-stack" style={{minHeight: "8em"}}>
                                <div className={selected !== null 
                                                    ? "button rect green fade-in-bottom" 
                                                    : "button rect green fade-in-bottom inactive-green"} 
                                        onClick={openLB}>
                                    Leaderboard
                                </div>
                                {userType !== "Model"
                                    ? <div className={selected !== null 
                                                        ? "button rect fade-in-bottom" 
                                                        : "button rect fade-in-bottom inactive"} 
                                            onClick={openMatch}>
                                        START
                                    </div>
                                    : <></>
                                }
                            </div>
                        </>
                        : <>
                            <div className="textbox fade-in-left" key="account-type">
                                <h3>Hello {user['name'].split(' ')[0]}, </h3>
                                Please choose your account type:
                            </div>
                            <MenuOptions className="fade-in-right" key="account" options={userTypes} 
                                            selected={userType} setSelected={setUserType} />
                            <div className={`button rect fade-in-bottom ${userType ? "" : "inactive"}`}
                                 onClick={() => updateUserType(userType)}>
                                Submit
                            </div>
                        </>
                    : <>
                    <div className="textbox fade-in-right">
                        You are not logged in.
                    </div>
                    <div className="button rect fade-in-bottom" style={{width: '300px'}}
                         onClick={login}>Login with Google</div>
                    </>}
                
                
                <div className="pad"></div>
            </div>
        </>
    )
}

export default MainMenu