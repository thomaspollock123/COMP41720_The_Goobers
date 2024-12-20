package service.core;

public class Stock {
    private String APIname;
    private String ticker;
    private double open;
    private double high;
    private double low;
    private double current;
    private double timestamp;

    public Stock(String ticker, String APIname, double timestamp, double open, double high, double low, double current) {
        this.APIname = APIname;
        this.ticker = ticker;
        this.open = open;
        this.high = high;
        this.low = low;
        this.current = current;
        this.timestamp = timestamp;
    }

    public String toString() {
        return "Stock{" +
                "APIname='" + APIname + "'" +
                ", timestamp = " + timestamp +
                ", open = " + open +
                ", close = " + current +
                ", high = " + high +
                ", low = " + low +
                "}";
    }

    public String getTicker() {
        return ticker;
    }
}
