package service.finnhub;

import org.json.JSONObject;
import service.core.AbstractAPIScraper;
import service.core.Stock;

import java.net.MalformedURLException;
import java.net.URISyntaxException;

public class FINIngestionService extends AbstractAPIScraper {

    public FINIngestionService(String kafkaServers, String kafkaTopic, String ticker, String APIurl, String APIname, double rate) throws URISyntaxException, MalformedURLException {
        super(kafkaServers, kafkaTopic, ticker, APIurl, APIname, rate);
    }

    @Override
    public Stock transformData(String ticker, String rawData) {
        JSONObject json = new JSONObject(rawData);
        return new Stock(
                ticker,
                APIname,
                json.getDouble("t"),
                json.getDouble("o"),
                json.getDouble("h"),
                json.getDouble("l"),
                json.getDouble("c")
        );
    }
}
