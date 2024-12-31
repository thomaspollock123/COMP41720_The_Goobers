package analytics.repository;

import analytics.model.Prediction;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PredictionRepository extends MongoRepository<Prediction, String> {

    // get predictions for a given ticker, sorted by timestamp desc
    List<Prediction> findByTickerOrderByTimestampDesc(String ticker);

    // get predictions for date/time range
    List<Prediction> findByTickerAndTimestampBetweenOrderByTimestampDesc(
            String ticker, long start, long end
    );

    // get latest prediction
    Prediction findTopByTickerOrderByTimestampDesc(String ticker);

}
