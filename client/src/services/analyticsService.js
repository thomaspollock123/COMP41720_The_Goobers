import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

/**
 * Fetch historical data for given ticker and time range
 */
export async function fetchHistoricalData(ticker, start, end) {
    const url = `${baseURL}/predictions/${ticker}/history?start=${start}&end=${end}`
    const response = await axios.get(url)
    return response.data
}

/**
 * Fetch aggregated signals over last x minutes
 */
export async function fetchSignalAggregation(ticker, minutes) {
    // e.g. /api/analytics/predictions/{ticker}/aggregation?duration=1h
    const url = `${baseURL}/predictions/${ticker}/aggregation?minutes=${minutes}`
    const response = await axios.get(url)
    return response.data
}
