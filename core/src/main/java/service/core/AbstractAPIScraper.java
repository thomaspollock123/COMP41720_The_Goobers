package service.core;

import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Properties;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

public abstract class AbstractAPIScraper {
    private final HttpClient httpClient;
    private final HttpRequest request;
    private final KafkaProducer<String, String> kafkaProducer;
    private final String kafkaTopic;
    private final int rate;
    protected final String APIname;
    private final String ticker;

    public AbstractAPIScraper(String kafkaServers, String kafkaTopic, String ticker, String APIurl, String APIname, int rate) throws URISyntaxException {
        // Initialise the number of API polls per minute
        this.rate = rate;
        this.APIname = APIname;
        this.ticker = ticker;

        // Setup Kafka properties
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaServers); // Can set multiple kafka nodes for scalability
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        this.kafkaProducer = new KafkaProducer<>(props);
        this.kafkaTopic = kafkaTopic;

        // Initialise HTTP GET request to API
        this.httpClient = HttpClient.newBuilder().build();
        this.request = HttpRequest.newBuilder().uri(new URI(APIurl)).build();
    }

    public void poll() {
        while (true) {
                // Fetch raw stock data from API
                String rawData = fetchRawData();

                // Transform the data to Stock object
                Stock stock = transformData(ticker, rawData);

                // Publish stock object to Kafka topic
                publishToKafka(stock);

                // Wait until next poll
                waitForPoll();
        }
    }

    private void waitForPoll() {
        try {
            Thread.sleep(60000/rate);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    public String fetchRawData() {
            try {
                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                return response.body();
            } catch (Exception e) {
                System.out.println("Error fetching raw data: " + e.getMessage());
                return null;
            }
    }

    public abstract Stock transformData(String ticker, String rawData);

    public void publishToKafka(Stock stock) {
        String stockData = stock.toString();
        String stockTicker = stock.getTicker();

        kafkaProducer.send(new ProducerRecord<>(kafkaTopic, stockTicker, stockData), (metadata, exception) -> {
            if (exception != null) {
                System.out.println("Error sending data: " + exception);
            } else {
                System.out.println("Sent data: " + stockData);
            }
        });
    }
}
