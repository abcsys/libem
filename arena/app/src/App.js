import React, { StrictMode } from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainMenu from "./pages/MainMenu"
import "./App.css"
import Match from "./pages/Match"
import Leaderboard from "./pages/Leaderboard"

const App = () => {

    return (
        <StrictMode>
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<MainMenu />} />
                    <Route path="/match/:dataset" element={<Match />} />
                    <Route path="/leaderboard/:dataset" element={<Leaderboard />} />
                    <Route path="/leaderboard" element={<Leaderboard />} />
                </Routes>
            </BrowserRouter>
        </StrictMode>
    )
}

export default App