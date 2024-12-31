import React, { useEffect } from 'react'
import { Button, ButtonGroup, Paper, Typography } from '@mui/material'
import {
    ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, Legend
} from 'recharts'
import { fetchHistoricalData } from '../services/analyticsService.js'
import { useSelector, useDispatch } from 'react-redux'
import { setTimeRange } from '../store/timeRangeSlice.js'

function HistoricalChart() {
    const dispatch = useDispatch()
    const timeRange = useSelector((state) => state.timeRange.value)
    const ticker = useSelector((state) => state.ticker.value)
    const [data, setData] = React.useState([])

    const loadData = (timeRange) => {
        const now = Math.floor(Date.now() / 1000)
        let startTime

        switch (timeRange) {
            case '1D':
                startTime = now - 24 * 60 * 60
                break
            case '5D':
                startTime = now - 5 * 24 * 60 * 60
                break
            case '1M':
                startTime = now - 30 * 24 * 60 * 60
                break
            default:
                startTime = now - 90 * 24 * 60 * 60
                break
        }

        fetchHistoricalData(ticker, startTime, now)
            .then((res) => setData(res))
            .catch(console.error)
    }

    useEffect(() => {
        loadData(timeRange)
    }, [timeRange, ticker]) // refetch if user changes ticker or time range

    return (
        <Paper sx={{ p: 2 }}>
            <Typography variant="h6">{ticker} - Historical View</Typography>
            <ButtonGroup size="small" sx={{ my: 1 }}>
                <Button
                    onClick={() => dispatch(setTimeRange('1D'))}
                    variant={timeRange === '1D' ? 'contained' : 'outlined'}
                >
                    1D
                </Button>
                <Button
                    onClick={() => dispatch(setTimeRange('5D'))}
                    variant={timeRange === '5D' ? 'contained' : 'outlined'}
                >
                    5D
                </Button>
                <Button
                    onClick={() => dispatch(setTimeRange('1M'))}
                    variant={timeRange === '1M' ? 'contained' : 'outlined'}
                >
                    1M
                </Button>
                <Button
                    onClick={() => dispatch(setTimeRange('3M'))}
                    variant={timeRange === '3M' ? 'contained' : 'outlined'}
                >
                    3M
                </Button>
            </ButtonGroup>

            <ResponsiveContainer width="100%" height="400px">
                <AreaChart data={data}>
                    <XAxis dataKey="timestamp" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="close" stroke="#8884d8" fill="#8884d8" />
                </AreaChart>
            </ResponsiveContainer>
        </Paper>
    )
}

export default HistoricalChart
