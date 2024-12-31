import React, { useEffect, useState } from 'react'
import { Card, CardContent, Typography } from '@mui/material'

export default function LatestSignalCard() {
    const [signal, setSignal] = useState('—')

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8080/ws/predictions')

        ws.onmessage = (event) => {
            try {
                const newPoint = JSON.parse(event.data)
                // newPoint.prediction is 0 or 1 => convert to "UP" / "DOWN"
                const direction = newPoint.prediction === 1 ? 'UP' : 'DOWN'
                setSignal(direction)
            } catch (err) {
                console.error('LatestSignalCard parse error:', err)
            }
        }

        ws.onopen = () => console.log('LatestSignalCard WS open')
        ws.onerror = (e) => console.error('LatestSignalCard WS error:', e)
        ws.onclose = () => console.log('LatestSignalCard WS closed')

        return () => {
            ws.close()
        }
    }, [])

    return (
        <Card>
            <CardContent>
                <Typography variant="h6">Current Signal</Typography>
                <Typography
                    variant="h4"
                    sx={{ mt: 1 }}
                    color={signal === 'UP ↑' ? 'green' : (signal === 'DOWN ↓' ? 'red' : 'inherit')}
                >
                    {signal}
                </Typography>
            </CardContent>
        </Card>
    )
}
