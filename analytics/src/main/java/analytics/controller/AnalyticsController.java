package analytics.controller;

import analytics.model.Prediction;
import analytics.service.AnalyticsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/predictions")
@CrossOrigin(origins = "http://localhost:5173")
public class AnalyticsController {

    private final AnalyticsService analyticsService;

    @Autowired
    public AnalyticsController(AnalyticsService analyticsService) {
        this.analyticsService = analyticsService;
    }

    /**
     * Returns all predictions for a ticker
     * GET /api/predictions/{ticker}
     */
    @GetMapping("/{ticker}")
    public List<Prediction> getAllPredictionsForTicker(@PathVariable("ticker") String ticker) {
        return analyticsService.getPredictionsForTicker(ticker);
    }

    /**
     * Returns the latest prediction for a ticker.
     * GET /api/predictions/{ticker}/latest
     */
    @GetMapping("/{ticker}/latest")
    public Prediction getLatestPrediction(@PathVariable("ticker") String ticker) {
        return analyticsService.getLatestPrediction(ticker);
    }

    /**
     * Returns predictions in a time range, sorted by timestamp desc
     * GET /api/predictions/{ticker}/history?start=2024-10-03T04:00:00.000Z&end=2024-10-03T08:00:00.000Z
     */
    @GetMapping("/{ticker}/history")
    public List<Prediction> getHistoricalPredictions(
            @PathVariable("ticker") String ticker,
            @RequestParam("start") String start,
            @RequestParam("end") String end
    ) {
        Instant startTime = Instant.parse(start);
        Instant endTime = Instant.parse(end);
        return analyticsService.getPredictionsForTickerInRange(ticker, startTime, endTime);
    }

    /**
     * Returns aggregation of predictions in a given time range or over the last x minutes.
     * GET /api/predictions/{ticker}/aggregations?start=2024-10-03T04:00:00.000Z&end=2024-10-03T08:00:00.000Z
     * GET /api/predictions/{ticker}/aggregations?minutes=60
     */
    @GetMapping("/{ticker}/aggregations")
    public Map<String, Object> getAggregations(
            @PathVariable("ticker") String ticker,
            @RequestParam(value = "start", required = false) String start,
            @RequestParam(value = "end", required = false) String end,
            @RequestParam(value = "minutes", required = false) Integer minutes
    ) {
        if (minutes != null) {
            return analyticsService.getAggregationsByMinutes(ticker, minutes);
        } else if (start != null && end != null) {
            Instant startTime = Instant.parse(start);
            Instant endTime = Instant.parse(end);
            return analyticsService.getAggregations(ticker, startTime, endTime);
        } else {
            throw new IllegalArgumentException("Invalid query parameters. Provide either 'minutes' or 'start' and 'end'.");
        }
    }

}
