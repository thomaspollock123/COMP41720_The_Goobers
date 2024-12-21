import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import service.core.Stock;
import service.stockdata.STKIngestionService;

import static org.junit.jupiter.api.Assertions.assertEquals;

class StockdataTest {

    private STKIngestionService service;

    @BeforeEach
    void setUp() throws Exception {
        String kafkaServers = "localhost:9092";
        String kafkaTopic = "stockData";
        String ticker = "AAPL";
        String APIurl = "https://example.api/quote";
        String APIname = "stockdata";
        double rate = 1.0;

        service = new STKIngestionService(kafkaServers, kafkaTopic, ticker, APIurl, APIname, rate);
    }

    @Test
    void testTransformData() {
        // Simulate raw JSON data returned from the API
        String rawData = """
            {
                "data": [
                    {
                        "last_trade_time": "2023-12-21T10:15:30.123456",
                        "day_open": 720.5,
                        "day_high": 725.0,
                        "day_low": 715.2,
                        "price": 722.8
                    }
                ]
            }
            """;

        // Call method to transform the data
        Stock stock = service.transformData("AAPL", rawData);

        // Tests to ensure valid transformation
        assertEquals("AAPL", stock.getTicker());
        assertEquals("stockdata", stock.getApiName());
        assertEquals(1703153730L, stock.getTimestamp());
        assertEquals(720.5, stock.getOpen(), 0.001);
        assertEquals(725.0, stock.getHigh(), 0.001);
        assertEquals(715.2, stock.getLow(), 0.001);
        assertEquals(722.8, stock.getCurrent(), 0.001);
    }
}
