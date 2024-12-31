package analytics.controller;

import analytics.model.Prediction;
import analytics.service.AnalyticsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
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
     * Returns predictions in a time range, sorted by timestamp desc
     * GET /api/predictions/{ticker}/history?start=1672531200&end=1672617600
     */
    @GetMapping("/{ticker}/history")
    public List<Prediction> getHistoricalPredictions(
            @PathVariable("ticker") String ticker,
            @RequestParam("start") long start,
            @RequestParam("end") long end
    ) {
        return analyticsService.getPredictionsForTickerInRange(ticker, start, end);
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
     * Returns aggregation of predictions over the last x minutes.
     * GET /api/predictions/{ticker}/aggregation?minutes=10
     */
    @GetMapping("/{ticker}/aggregation")
    public Map<String, Object> getAggregations(
            @PathVariable("ticker") String ticker,
            @RequestParam("minutes") int minutes
    ) {
        // time window conversion
        long now = System.currentTimeMillis();
        long startTimestamp = now - (minutes * 60000L);

        List<Prediction> predictions = analyticsService.getPredictionsForTickerInRange(ticker, startTimestamp, now);

        long upCount = predictions.stream().filter(p -> p.getPrediction() == 1).count();
        long downCount = predictions.size() - upCount;

        Map<String, Object> result = new HashMap<>();
        result.put("upCount", upCount);
        result.put("downCount", downCount);
        return result;
    }


}
