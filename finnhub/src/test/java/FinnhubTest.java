import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import service.core.Stock;
import service.finnhub.FINIngestionService;

import static org.junit.jupiter.api.Assertions.assertEquals;

class FinnhubTest {

    private FINIngestionService service;

    @BeforeEach
    void setUp() throws Exception {
        String kafkaServers = "localhost:9092";
        String kafkaTopic = "stockData";
        String ticker = "AAPL";
        String APIurl = "https://example.api/quote";
        String APIname = "finnhub";
        double rate = 1.0;

        service = new FINIngestionService(kafkaServers, kafkaTopic, ticker, APIurl, APIname, rate);
    }

    @Test
    void testTransformData() {
        // Simulate raw JSON data returned from the API
        String rawData = "{ \"t\": 1672531200, \"o\": 150.0, \"h\": 155.0, \"l\": 148.0, \"c\": 153.0 }";

        // Call method to transform the data
        Stock stock = service.transformData("AAPL", rawData);

        // Tests to ensure valid transformation
        assertEquals("AAPL", stock.getTicker());
        assertEquals("finnhub", stock.getApiName());
        assertEquals(1672531200L, stock.getTimestamp());
        assertEquals(150.0, stock.getOpen(), 0.001);
        assertEquals(155.0, stock.getHigh(), 0.001);
        assertEquals(148.0, stock.getLow(), 0.001);
        assertEquals(153.0, stock.getCurrent(), 0.001);
    }
}
