import { createSlice } from '@reduxjs/toolkit'

const initialState = {
    value: '3M',
}

const timeRangeSlice = createSlice({
    name: 'timeRange',
    initialState,
    reducers: {
        setTimeRange: (state, action) => {
            state.value = action.payload
        },
    },
})

export const { setTimeRange } = timeRangeSlice.actions

export default timeRangeSlice.reducer