import { createSlice } from '@reduxjs/toolkit'

const initialState = {
    value: 'AAPL', // default ticker
}

const tickerSlice = createSlice({
    name: 'ticker',
    initialState,
    reducers: {
        setTicker: (state, action) => {
            state.value = action.payload
        },
    },
})

export const { setTicker } = tickerSlice.actions

export default tickerSlice.reducer