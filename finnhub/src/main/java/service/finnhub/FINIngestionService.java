package service.finnhub;

import org.json.JSONObject;
import service.core.AbstractAPIScraper;
import service.core.Stock;

import java.net.MalformedURLException;
import java.net.URISyntaxException;

public class FINIngestionService extends AbstractAPIScraper {

    // Ingestion service for ticker
    private static String ticker = "AAPL";

    // Define the API url to poll
    private static String APIkey = "KEY";
    private static String APIname = "finnhub";
    private static String APIurl = "https://finnhub.io/api/v1/quote?symbol=" + ticker + "&token=" + APIkey;

    // Define the number of polls per minute
    private static int rate = 60;

    // Define kafka details
    private static String kafkaServers = "localhost:9092"; //CHANGE
    private static String kafkaTopic = "stockData";

    public FINIngestionService(String kafkaServers, String kafkaTopic, String APIurl, String APIname, int rate) throws URISyntaxException, MalformedURLException {
        super(kafkaServers, kafkaTopic, APIurl, APIname, rate);
    }

    @Override
    public Stock transformData(String rawData) {
        JSONObject json = new JSONObject(rawData);
        return new Stock(
                ticker,
                json.getDouble("t"),
                json.getDouble("o"),
                json.getDouble("h"),
                json.getDouble("l"),
                json.getDouble("c")
        );
    }

    public static void main(String[] args) throws URISyntaxException, MalformedURLException {
        FINIngestionService service = new FINIngestionService(kafkaServers,kafkaTopic,APIurl,APIname,rate);
        service.poll();
    }
}
