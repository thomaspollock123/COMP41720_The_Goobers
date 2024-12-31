import React, { useEffect, useState } from 'react'
import { Card, CardContent, Typography } from '@mui/material'
import { fetchSignalAggregation } from '../services/analyticsService.js'
import { useSelector } from 'react-redux'

function HourSignalCard() {
    const [upCount, setUpCount] = useState(0)
    const [downCount, setDownCount] = useState(0)
    const ticker = useSelector((state) => state.ticker.value)

    useEffect(() => {
        // 60 => last 60 minutes
        fetchSignalAggregation(ticker, 60)
            .then((res) => {
                setUpCount(res.upCount)
                setDownCount(res.downCount)
            })
            .catch(console.error)
    }, [ticker])

    return (
        <Card>
            <CardContent>
                <Typography variant="h6">Signals in Last Hour</Typography>
                <Typography variant="h4" sx={{ mt: 1 }}>
                    <span style={{ color: 'green' }}>↑ {upCount}</span> vs{' '}
                    <span style={{ color: 'red' }}>↓ {downCount}</span>
                </Typography>
            </CardContent>
        </Card>
    )
}

export default HourSignalCard
