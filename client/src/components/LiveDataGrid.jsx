import React, { useEffect, useState } from 'react'
import { DataGrid } from '@mui/x-data-grid'
import { Grid2, Paper, Typography } from '@mui/material'

const columns = [
    { field: 'timestamp', headerName: 'Timestamp', flex: 1 },
    { field: 'open', headerName: 'Open', flex: 1 },
    { field: 'high', headerName: 'High', flex: 1 },
    { field: 'low', headerName: 'Low', flex: 1 },
    { field: 'close', headerName: 'Close', flex: 1 },
    { field: 'prediction', headerName: 'Prediction', flex: 1 },
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
