package service.stockdata;

import org.json.JSONArray;
import org.json.JSONObject;
import service.core.AbstractAPIScraper;
import service.core.Stock;

import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

public class STKIngestionService extends AbstractAPIScraper {

    public STKIngestionService(String kafkaServers, String kafkaTopic, String ticker, String APIurl, String APIname, double rate) throws URISyntaxException, MalformedURLException {
        super(kafkaServers, kafkaTopic, ticker, APIurl, APIname, rate);
    }

    @Override
    public Stock transformData(String ticker, String rawData) {
        JSONObject jsonobj = new JSONObject(rawData);

        // Access the data array
        JSONArray dataArray = jsonobj.getJSONArray("data");

        // Access the 0th element of the array
        JSONObject json = dataArray.getJSONObject(0);

        // Define the formatter to match the date-time format
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS");

        // Parse the date-time string to a LocalDateTime object
        LocalDateTime dateTime = LocalDateTime.parse(json.getString("last_trade_time"), formatter);

        // Convert to Unix timestamp (seconds since epoch)
        long unixTimestamp = dateTime.toEpochSecond(ZoneOffset.UTC);

        return new Stock(
                ticker,
                APIname,
                unixTimestamp,
                json.getDouble("day_open"),
                json.getDouble("day_high"),
                json.getDouble("day_low"),
                json.getDouble("price")
        );
    }
}
