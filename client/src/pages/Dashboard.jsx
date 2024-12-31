import React from 'react'
import { Grid2, Paper } from '@mui/material'

import NavBar from '../components/NavBar.jsx'
import LatestSignalCard from '../components/LatestSignalCard.jsx'
import TenMinSignalCard from '../components/TenMinSignalCard.jsx'
import HourSignalCard from '../components/HourSignalCard.jsx'
import LiveDataGrid from '../components/LiveDataGrid.jsx'
import HistoricalChart from '../components/HistoricalChart.jsx'
import HistoricalDataGrid from '../components/HistoricalDataGrid.jsx'

export default function Dashboard() {
    return (
        <Grid2
            container
            spacing={1}
            sx={{ width:'99vw', height:'99vh'}}
            direction="column"
        >
            <Grid2 size={12} >
                <NavBar />
            </Grid2>
            <Grid2 container size={12} sx={{ flex: 1 }}>
                <Grid2 container size={{ xs:12, lg:5 }} direction="column">
                    <Grid2 container size={{ xs:12 }} >
                        <Grid2 size={{ xs:12, lg:3 }}>
                            <LatestSignalCard />
                        </Grid2>
                        <Grid2 size={{ xs:12, lg:4 }}>
                            <TenMinSignalCard />
                        </Grid2>
                        <Grid2 size={{ xs:12, lg:5 }}>
                            <HourSignalCard />
                        </Grid2>
                    </Grid2>
                    <Grid2 container size={12} sx={{ flex: 1 }}>
                        <Grid2 size={12}>
                            <LiveDataGrid />
                        </Grid2>
                    </Grid2>
                </Grid2>
                <Grid2 container size={{ xs:12, lg:7 }} direction="column">
                    <Grid2 container size={12}>
                        <Grid2 size={12}>
                            <HistoricalChart />
                        </Grid2>
                    </Grid2>
                    <Grid2 container size={12} sx={{ flex: 1 }}>
                        <Grid2 size={12}>
                            <HistoricalDataGrid />
                        </Grid2>
                    </Grid2>
                </Grid2>
            </Grid2>

        </Grid2>
    )
}
