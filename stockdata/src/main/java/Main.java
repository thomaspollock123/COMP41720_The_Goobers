import service.stockdata.STKIngestionService;

import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.util.Properties;

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
        String APIkey = prop.getProperty("stockdata.api.key");
        if (APIkey == null) {
            throw new RuntimeException("API key is missing in the configuration file.");
        }
        String APIname = "stockdata";
        String APIurl = "https://api.stockdata.org/v1/data/quote?symbols=" + ticker + "&api_token=" + APIkey;

        // Define the number of polls per minute
        double rate = 100.0/(24.0 * 60.0); // 100 polls per day divided by 24*60 minutes => polls per minute

        // Define kafka details
        String kafkaServers = "kafka:9092"; //CHANGE
        String kafkaTopic = "stockData";

        STKIngestionService service = new STKIngestionService(kafkaServers,kafkaTopic,ticker,APIurl,APIname,rate);
        try {
            Thread.sleep(5000);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        service.poll();
    }
}
