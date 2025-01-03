package analytics.service;

import analytics.model.Prediction;
import analytics.repository.PredictionRepository;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class AnalyticsService {

    private final PredictionRepository predictionRepository;

    public AnalyticsService(PredictionRepository predictionRepository) {
        this.predictionRepository = predictionRepository;
    }

    public List<Prediction> getPredictionsForTicker(String ticker) {
        return predictionRepository.findByTickerOrderByTimestampDesc(ticker);
    }

    public List<Prediction> getPredictionsForTickerInRange(String ticker, Instant start, Instant end) {
        return predictionRepository.findByTickerAndTimestampBetweenOrderByTimestampDesc(ticker, start, end);
    }

    public Prediction getLatestPrediction(String ticker) {
        return predictionRepository.findTopByTickerOrderByTimestampDesc(ticker);
    }

    public Map<String, Object> getAggregations(String ticker, Instant start, Instant end) {
        List<Prediction> predictions = getPredictionsForTickerInRange(ticker, start, end);
        long upCount = predictions.stream().filter(p -> p.getPrediction() == 1).count();
        long downCount = predictions.size() - upCount;

        Map<String, Object> result = new HashMap<>();
        result.put("upCount", upCount);
        result.put("downCount", downCount);
        return result;
    }

    public Map<String, Object> getAggregationsByMinutes(String ticker, int minutes) {
        Instant end = Instant.now();
        Instant start = end.minusSeconds(minutes * 60L);
        return getAggregations(ticker, start, end);
    }

}
