package service.finnhub;

import service.core.AbstractAPIScraper;
import service.core.Stock;

import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.net.URL;

public class FINIngestionService extends AbstractAPIScraper {

    private String APIkey = "KEY";
    private String ticker = "AAPL";
    private String APIname = "finnhub";
    private URL APIurl = new URL("https://finnhub.io/api/v1/quote?symbol=" + ticker + "&token=" + APIkey);
    private int rate = 60;
    private String kafkaServers = "localhost:9092"; //CHANGE
    private String kafkaTopic = "stockData";

    public FINIngestionService(String kafkaServers, String kafkaTopic, String APIurl, String APIname, int rate) throws URISyntaxException, MalformedURLException {
        super(kafkaServers, kafkaTopic, APIurl, APIname, rate);
    }

    @Override
    public Stock transformData(String rawData) {
        return null;
    }
}
