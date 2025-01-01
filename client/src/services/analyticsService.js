import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

/**
 * Fetch historical data for given ticker and time range
 */
export async function fetchHistoricalData(ticker, start, end) {
    try {
        const url = `${baseURL}/predictions/${ticker}/history`
        const response = await axios.get(url, {
            params: {
                start: new Date(start).toISOString(),
                end: new Date(end).toISOString()
            }
        })
        return response.data
    } catch (error) {
        console.error('Failed to fetch historical data:', error)
        throw error
    }
}

/**
 * Fetch aggregated signals over last x minutes
 */
export async function fetchSignalAggregation(ticker, minutes) {
    try {
        const url = `${baseURL}/predictions/${ticker}/aggregations`
        const response = await axios.get(url, { params: { minutes } })
        return response.data
    } catch (error) {
        console.error('Failed to fetch signal aggregations:', error)
        throw error
    }
}
