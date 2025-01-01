import React, { useEffect, useState } from 'react'
import { Card, CardContent, Typography } from '@mui/material'
import { fetchSignalAggregation } from '../services/analyticsService.js'
import { useSelector } from 'react-redux'

function HourSignalCard() {
    const [upCount, setUpCount] = useState(0)
    const [downCount, setDownCount] = useState(0)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const ticker = useSelector((state) => state.ticker.value)

    useEffect(() => {
        setLoading(true)
        fetchSignalAggregation(ticker, 1440)
            .then((res) => {
                setUpCount(res.upCount)
                setDownCount(res.downCount)
                setLoading(false)
            })
            .catch((err) => {
                console.error(err)
                setError('Failed to load data')
                setLoading(false)
            })
    }, [ticker])

    if (loading) return <Typography>Loading...</Typography>
    if (error) return <Typography color="error">{error}</Typography>

    return (
        <Card>
            <CardContent>
                <Typography variant="h6">Signals in Last 24h</Typography>
                <Typography variant="h4" sx={{ mt: 1 }}>
                    <span style={{ color: 'green' }}>↑ {upCount}</span> vs{' '}
                    <span style={{ color: 'red' }}>↓ {downCount}</span>
                </Typography>
            </CardContent>
        </Card>
    )
}

export default HourSignalCard