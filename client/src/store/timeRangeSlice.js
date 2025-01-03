import { createSlice } from '@reduxjs/toolkit'

const computeRange = (unit, value) => {
    const end = new Date()
    let start

    switch (unit) {
        case 'months':
            start = new Date(end)
            start.setMonth(end.getMonth() - value)
            break
        case 'days':
            start = new Date(end)
            start.setDate(end.getDate() - value)
            break
        case 'hours':
            start = new Date(end)
            start.setHours(end.getHours() - value)
            break
        default:
            start = end
    }
    return { start: start.toISOString(), end: end.toISOString() }
}

const initialState = {
    range: { unit: 'days', value: 1 },
    ...computeRange('days', 1)
}

const timeRangeSlice = createSlice({
    name: 'timeRange',
    initialState,
    reducers: {
        setTimeRange: (state, action) => {
            const { unit, value } = action.payload
            const { start, end } = computeRange(unit, value)
            state.range = { unit, value }
            state.start = start
            state.end = end
        }
    }
})

export const { setTimeRange } = timeRangeSlice.actions
export default timeRangeSlice.reducer