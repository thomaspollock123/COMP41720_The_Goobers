import { configureStore } from '@reduxjs/toolkit'
import tickerReducer from './tickerSlice.js'
import timeRangeReducer from './timeRangeSlice.js'

export const store = configureStore({
    reducer: {
        ticker: tickerReducer,
        timeRange: timeRangeReducer,
    },
})