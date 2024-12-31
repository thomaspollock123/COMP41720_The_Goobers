import React, { useEffect, useState } from 'react'
import { Paper, Typography } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import { fetchHistoricalData } from '../services/analyticsService.js'
import { useSelector } from 'react-redux'

const columns = [
    { field: 'timestamp', headerName: 'Timestamp', flex: 1 },
    { field: 'open', headerName: 'Open', flex: 1 },
    { field: 'high', headerName: 'High', flex: 1 },
    { field: 'low', headerName: 'Low', flex: 1 },
    { field: 'close', headerName: 'Close', flex: 1 },
    { field: 'prediction', headerName: 'Prediction', flex: 1 },
]

function HistoricalDataGrid() {
    const [rows, setRows] = useState([])
    const ticker = useSelector((state) => state.ticker.value)
    const timeRange = useSelector((state) => state.timeRange.value)

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
            .then((res) => {
                const processed = res.map((item, idx) => ({ id: idx, ...item }))
                setRows(processed)
            })
            .catch(console.error)
    }

    useEffect(() => {
        loadData()
    }, [ticker, timeRange])

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
                            pageSize: 10,
                        },
                    },
                }}
                pageSizeOptions={[5, 10, 25]}
                disableRowSelectionOnClick
                autoHeight={false}
                sx={{ height: "100%%"}}
            />
        </Paper>
    )
}

export default HistoricalDataGrid
