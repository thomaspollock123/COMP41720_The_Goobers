import service.finnhub.FINIngestionService;

import java.net.MalformedURLException;
import java.net.URISyntaxException;

public class Main {
    public static void main(String[] args) throws MalformedURLException, URISyntaxException {
        // Ingestion service for ticker
        String ticker = "AAPL";

        // Define the API url to poll
        String APIkey = "KEY";
        String APIname = "finnhub";
        String APIurl = "https://finnhub.io/api/v1/quote?symbol=" + ticker + "&token=" + APIkey;

        // Define the number of polls per minute
        int rate = 60;

        // Define kafka details
        String kafkaServers = "kafka:9092"; //CHANGE
        String kafkaTopic = "stockData";

        FINIngestionService service = new FINIngestionService(kafkaServers,kafkaTopic,ticker,APIurl,APIname,rate);
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        service.poll();
    }
}
