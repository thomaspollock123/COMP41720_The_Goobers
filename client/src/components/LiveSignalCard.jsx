import React, { useEffect, useState } from 'react'
import { Card, CardContent, Typography } from '@mui/material'
import { useSelector } from 'react-redux'

function LiveSignalCard() {
    const [upCount, setUpCount] = useState(0)
    const [downCount, setDownCount] = useState(0)
    const ticker = useSelector((state) => state.ticker.value)

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8080/ws/predictions')

        ws.onmessage = (event) => {
            try {
                const newPoint = JSON.parse(event.data)
                if (newPoint.prediction === 1) {
                    setUpCount(prev => prev + 1)
                } else {
                    setDownCount(prev => prev + 1)
                }
            } catch (err) {
                console.error('LiveSignalCard parse error:', err)
            }
        }

        ws.onopen = () => console.log('LiveSignalCard WS open')
        ws.onerror = (e) => console.error('LiveSignalCard WS error:', e)
        ws.onclose = () => console.log('LiveSignalCard WS closed')

        return () => {
            ws.close()
        }
    }, [ticker])

    return (
        <Card>
            <CardContent>
                <Typography variant="h6">Live Signal Counter</Typography>
                <Typography variant="h4" sx={{ mt: 1 }}>
                    <span style={{ color: 'green' }}>↑ {upCount}</span> vs{' '}
                    <span style={{ color: 'red' }}>↓ {downCount}</span>
                </Typography>
            </CardContent>
        </Card>
    )
}

export default LiveSignalCard