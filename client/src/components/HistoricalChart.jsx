import React, { useEffect, useState } from 'react'
import { Button, ButtonGroup, Paper, Typography } from '@mui/material'
import {
    ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip
} from 'recharts'
import { fetchHistoricalData } from '../services/analyticsService.js'
import { useSelector, useDispatch } from 'react-redux'
import { setTimeRange } from '../store/timeRangeSlice.js'
import { format } from 'date-fns'

function HistoricalChart() {
    const dispatch = useDispatch()
    const timeRange = useSelector((state) => state.timeRange.range)
    const start = useSelector((state) => state.timeRange.start)
    const end = useSelector((state) => state.timeRange.end)
    const ticker = useSelector((state) => state.ticker.value)
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [color, setColor] = useState('#8884d8')
    const [yAxisDomain, setYAxisDomain] = useState([0, 0])

    const loadData = async () => {
        if (!start || !end || !ticker) return // prevent fetch if start, end, or ticker is undefined
        setLoading(true)
        setError(null)
        try {
            const res = await fetchHistoricalData(ticker, start, end)
            const processed = res.map(item => ({
                ...item,
                timestamp: new Date(item.timestamp).getTime(), // ISO string to milliseconds for AreaChart
            })).sort((a, b) => a.timestamp - b.timestamp) // left-to-right order

            const closeValues = processed.map(item => item.close)
            const minClose = Math.min(...closeValues)
            const maxClose = Math.max(...closeValues)
            const range = maxClose - minClose
            const buffer = range * 0.5 // 50% buffer based on range
            setYAxisDomain([minClose - buffer, maxClose + buffer])

            const color = processed[processed.length - 1].close > processed[0].close ? '#4caf50' : '#f44336'
            setColor(color)

            setData(processed)
        } catch (err) {
            console.error('Failed to fetch historical data:', err)
            setError('Failed to load data')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadData()
    }, [timeRange, ticker, start, end])

    if (loading) return <Typography>Loading...</Typography>
    if (error) return <Typography color="error">{error}</Typography>
    if (!data.length) return <Typography>No data available for the selected range.</Typography>

    return (
        <Paper sx={{ p: 2, fontFamily: 'Roboto Flex, sans-serif' }}>
            <Typography variant="h6">{ticker} - Historical View</Typography>
            <ButtonGroup
                size="small"
                sx={{
                    my: 1,
                    '& .MuiButton-root': {
                        backgroundColor: '#424242',
                        color: 'white',
                        borderColor: '#b0b0b0',
                        '&.Mui-selected, &.MuiButton-contained': {
                            backgroundColor: '#b0b0b0',
                            color: 'black'
                        }
                    }
                }}
            >
                <Button
                    onClick={() => dispatch(setTimeRange({ unit: 'days', value: 1 }))}
                    variant={timeRange.unit === 'days' && timeRange.value === 1 ? 'contained' : 'outlined'}
                >
                    1D
                </Button>
                <Button
                    onClick={() => dispatch(setTimeRange({ unit: 'days', value: 3 }))}
                    variant={timeRange.unit === 'days' && timeRange.value === 3 ? 'contained' : 'outlined'}
                >
                    3D
                </Button>
                <Button
                    onClick={() => dispatch(setTimeRange({ unit: 'days', value: 5 }))}
                    variant={timeRange.unit === 'days' && timeRange.value === 5 ? 'contained' : 'outlined'}
                >
                    5D
                </Button>
            </ButtonGroup>

            <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data}>
                    <XAxis
                        dataKey="timestamp"
                        tickFormatter={(tick) => timeRange.unit === 'days' && timeRange.value === 1
                            ? format(new Date(tick), 'HH:mm')
                            : format(new Date(tick), 'MM/dd/yyyy')
                        }
                        interval={timeRange.value === 1 ? 50 : timeRange.value === 3 ? 150 : 250}
                    />
                    <YAxis
                        domain={yAxisDomain}
                        tickFormatter={(tick) => tick.toFixed(2)}
                    />
                    <Tooltip
                        labelFormatter={(label) => format(new Date(label), 'MM/dd/yyyy HH:mm')}
                        formatter={(value) => value.toFixed(2)}
                    />
                    <Area type="monotone" dataKey="close" stroke={color} fill={color} />
                </AreaChart>
            </ResponsiveContainer>
        </Paper>
    )
}

export default HistoricalChart
