import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'

function App() {
    return (
        <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="test" element={<h2>Test route!</h2>} />
        </Routes>
    )
}

export default App