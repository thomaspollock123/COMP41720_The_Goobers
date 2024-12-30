package service.core;

public class Stock {
    private String APIname;
    private String ticker;
    private double open;
    private double high;
    private double low;
    private double current;
    private long timestamp;

    public Stock(String ticker, String APIname, long timestamp, double open, double high, double low, double current) {
        this.APIname = APIname;
        this.ticker = ticker;
        this.open = open;
        this.high = high;
        this.low = low;
        this.current = current;
        this.timestamp = timestamp;
    }

    public String toString() {
        return "{" +
                "\"APIname\": \"" + APIname + "\"" +
                ", \"ticker\": \"" + ticker + "\"" +
                ", \"timestamp\": " + timestamp +
                ", \"open\": " + open +
                ", \"close\": " + current +
                ", \"high\": " + high +
                ", \"low\": " + low +
                "}";
    }

    public String getTicker() {
        return ticker;
    }

    public String getApiName() { return APIname; }

    public double getOpen() { return open; }

    public double getHigh() { return high; }

    public double getLow() { return low; }

    public double getCurrent() { return current; }

    public long getTimestamp() { return timestamp; }
}
