package analytics.service;

import analytics.model.Prediction;
import analytics.repository.PredictionRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AnalyticsService {

    private final PredictionRepository predictionRepository;

    public AnalyticsService(PredictionRepository predictionRepository) {
        this.predictionRepository = predictionRepository;
    }

    public List<Prediction> getPredictionsForTicker(String ticker) {
        return predictionRepository.findByTickerOrderByTimestampDesc(ticker);
    }

    public List<Prediction> getPredictionsForTickerInRange(String ticker, long start, long end) {
        return predictionRepository.findByTickerAndTimestampBetweenOrderByTimestampDesc(ticker, start, end);
    }

    public Prediction getLatestPrediction(String ticker) {
        return predictionRepository.findTopByTickerOrderByTimestampDesc(ticker);
    }

}
