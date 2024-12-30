package service.twelvedata;

import org.json.JSONException;
import org.json.JSONObject;
import service.core.AbstractAPIScraper;
import service.core.Stock;

import java.net.MalformedURLException;
import java.net.URISyntaxException;

public class TWVIngestionService extends AbstractAPIScraper {

    public TWVIngestionService(String kafkaServers, String kafkaTopic, String ticker, String APIurl, String APIname, double rate) throws URISyntaxException, MalformedURLException {
        super(kafkaServers, kafkaTopic, ticker, APIurl, APIname, rate);
    }

    @Override
    public Stock transformData(String ticker, String rawData) {
        try {
            JSONObject json = new JSONObject(rawData);
            return new Stock(
                    ticker,
                    APIname,
                    json.getLong("timestamp"),
                    json.getDouble("open"),
                    json.getDouble("high"),
                    json.getDouble("low"),
                    json.getDouble("close")
            );
        } catch (JSONException e) {
            System.err.println("Failed to transform data: " + rawData);
            e.printStackTrace();
            return null;
        }
    }
}
