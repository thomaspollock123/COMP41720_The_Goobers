package service.finnhub;

import org.json.JSONException;
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
        try {
            JSONObject json = new JSONObject(rawData);
            return new Stock(
                    ticker,
                    APIname,
                    json.getLong("t"),
                    json.getDouble("o"),
                    json.getDouble("h"),
                    json.getDouble("l"),
                    json.getDouble("c")
            );
        } catch (JSONException e) {
            System.err.println("Failed to transform data: " + rawData);
            e.printStackTrace();
            return null;
        }
    }
}
