import React, { useEffect, useState } from 'react'
import { DataGrid } from '@mui/x-data-grid'
import { Grid2, Paper, Typography } from '@mui/material'
import {format} from "date-fns";

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

export default function LiveDataGrid() {
    const [rows, setRows] = useState([])

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8080/ws/predictions')

        ws.onmessage = (event) => {
            try {
                const newPoint = JSON.parse(event.data)
                const id = `${newPoint.timestamp}-${Math.random()}`

                // Insert new row at the top
                setRows((prev) => [{ id, ...newPoint }, ...prev])
            } catch (err) {
                console.error('Failed to parse WebSocket message:', err)
            }
        }

        ws.onopen = () => {
            console.log('LiveDataGrid WebSocket open')
        }
        ws.onerror = (err) => console.error('LiveDataGrid WebSocket error:', err)
        ws.onclose = () => console.log('LiveDataGrid WebSocket closed')

        // Cleanup
        return () => {
            ws.close()
        }
    }, [])

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
                Live Data Grid
            </Typography>
            <DataGrid
                rows={rows}
                columns={columns}
                initialState={{
                    pagination: {
                        paginationModel: {
                            pageSize: 15,
                        },
                    },
                }}
                disableRowSelectionOnClick
                autoHeight={false}
                sx={{ height: "100%%"}}
            />
        </Paper>
    )
}
