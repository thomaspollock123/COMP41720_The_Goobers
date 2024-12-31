import {
    AppBar,
    Toolbar,
    Box,
    IconButton,
    FormControl,
    Select,
    MenuItem
} from '@mui/material'
import CandlestickChartIcon from '@mui/icons-material/CandlestickChart'
import { useSelector, useDispatch } from 'react-redux'
import { setTicker } from '../store/tickerSlice.js'

function NavBar() {
    const dispatch = useDispatch()
    const selectedTicker = useSelector((state) => state.ticker.value)

    const handleTickerChange = (e) => {
        dispatch(setTicker(e.target.value))
    }

    return (
        <AppBar
            position="static"
            sx={{
                backgroundColor: '#f0f1f3'
            }}
        >
            <Toolbar
                sx={{
                    justifyContent: 'space-between',
                }}
            >
                {/* Left side: application logo */}
                <Box
                    component="img"
                    src="/src/assets/TickerTrek.png"
                    alt="TickerTrek Logo"
                    sx={{
                        height: 40,
                        objectFit: 'contain',
                    }}
                />

                {/* Right side: Icon + dropdown */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <IconButton color="primary" aria-label="candlestick-chart">
                        <CandlestickChartIcon sx = {{ color: '#5A5A5A'  }}/>
                    </IconButton>

                    <FormControl variant="standard" sx={{ minWidth: 80 }}>
                        <Select
                            value={selectedTicker}
                            onChange={handleTickerChange}
                            disableUnderline
                            sx={{
                                fontSize: '0.9rem',
                            }}
                        >
                            <MenuItem value="AAPL">AAPL</MenuItem>
                            <MenuItem value="GOOGL">GOOGL</MenuItem>
                            <MenuItem value="AMZN">AMZN</MenuItem>
                        </Select>
                    </FormControl>
                </Box>
            </Toolbar>
        </AppBar>
    )
}

export default NavBar
