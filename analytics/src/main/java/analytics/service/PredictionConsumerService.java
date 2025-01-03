package analytics.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import analytics.config.PredictionHandler;

@Service
public class PredictionConsumerService {

    private final PredictionHandler predictionHandler;

    @Autowired
    public PredictionConsumerService(PredictionHandler handler) {
        this.predictionHandler = handler;
    }

    @KafkaListener(topics = "predictions", groupId = "analytics-service-group")
    public void handleNewPrediction(String message) {
        System.out.println("Consumed from Kafka: " + message);
        predictionHandler.broadcast(message);
    }
}
