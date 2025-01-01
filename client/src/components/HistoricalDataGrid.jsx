import React, { useEffect, useState } from 'react'
import { Paper, Typography } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import { fetchHistoricalData } from '../services/analyticsService.js'
import { useSelector } from 'react-redux'
import { format } from 'date-fns'

const columns = [
    {
        field: 'timestamp',
        headerName: 'Timestamp',
        flex: 1,
        renderCell: (params) => {
            const value = params.value
            return value
                ? format(new Date(value), 'MMM dd, yyyy HH:mm:ss')
                : '--'
        }
    },
    { field: 'open', headerName: 'Open', flex: 1 },
    { field: 'high', headerName: 'High', flex: 1 },
    { field: 'low', headerName: 'Low', flex: 1 },
    { field: 'close', headerName: 'Close', flex: 1 },
    {
        field: 'prediction',
        headerName: 'Prediction',
        flex: 1,
        renderCell: (params) => (
            <span style={{ color: params.value === 1 ? 'green' : 'red' }}>
                {params.value === 1 ? 'UP' : 'DOWN'}
            </span>
        )
    }
]

function HistoricalDataGrid() {
    const [rows, setRows] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const ticker = useSelector((state) => state.ticker.value)
    const start = useSelector((state) => state.timeRange.start)
    const end = useSelector((state) => state.timeRange.end)

    const loadData = async () => {
        if (!start || !end || !ticker ) return // Prevent fetch if start, end, or ticker  is undefined
        setLoading(true)
        setError(null)
        try {
            const res = await fetchHistoricalData(ticker, start, end)
            const processed = res.filter(item => item.timestamp) // Ensure valid timestamps
                .map((item) => ({ id: item.id, ...item, }))
            setRows(processed)
        } catch (err) {
            console.error('Failed to fetch data:', err)
            setError('Failed to load data')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadData()
    }, [ticker, start, end])

    if (loading) return <Typography>Loading...</Typography>
    if (error) return <Typography color="error">{error}</Typography>


    return (
        <Paper
            sx={{
                p: 2,
                height: "100%",
                boxSizing: "border-box",
                display: 'grid',
                gridTemplateRows: 'auto 1fr'
            }}
        >
            <Typography variant="h6" sx={{ mb: 1 }}>
                {ticker} - Historical Data
            </Typography>
            <DataGrid
                rows={rows}
                columns={columns}
                initialState={{
                    pagination: {
                        paginationModel: {
                            pageSize: 5,
                        },
                    },
                }}
                disableRowSelectionOnClick
                autoHeight={false}
                sx={{ height: "100%"}}
            />
        </Paper>
    )
}

export default HistoricalDataGrid
