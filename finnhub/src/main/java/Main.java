import service.finnhub.FINIngestionService;

import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.util.Properties;
import java.io.InputStream;

public class Main {
    public static void main(String[] args) throws MalformedURLException, URISyntaxException {
        // Ingestion service for ticker
        String ticker = "AAPL";

        // Load properties from the config.properties file in resources
        Properties prop = new Properties();
        try (InputStream input = Main.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input == null) {
                System.out.println("Unable to find config.properties");
                return;
            }

            // Load the properties from the file
            prop.load(input);
        } catch (Exception e) {
            e.printStackTrace();
            return;
        }

        // Fetch API key from properties file
        String APIkey = prop.getProperty("finnhub.api.key");
        if (APIkey == null) {
            throw new RuntimeException("API key is missing in the configuration file.");
        }
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
