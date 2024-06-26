import React, { useEffect, useRef, useState } from "react"
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import MainMenu from "./pages/MainMenu"
import "./App.css"
import Match from "./pages/Match"
import Leaderboard from "./pages/Leaderboard"
import { baseURL } from "./Common"

const App = () => {
    const [datasets, setDatasets] = useState(null)

    useEffect(() => {
        fetch(baseURL + "/init/")
        .then(r => r.json())
        .then(r => setDatasets(r))
        .catch(e => setDatasets([]))
    }, [])

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<MainMenu datasets={datasets} />} />
                <Route path="/match/:dataset" element={<Match datasets={datasets} />} />
                <Route path="/leaderboard/:dataset" element={<Leaderboard />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App