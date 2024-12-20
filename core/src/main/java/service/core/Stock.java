package service.core;

public class Stock {
    private String APIname;
    private String ticker;
    private double open;
    private double high;
    private double low;
    private double close;
    private double volume;
    private double timestamp;

    public Stock(String ticker, double open, double high, double low, double close, double volume) {
        this.APIname = ticker;
        this.ticker = ticker;
        this.open = open;
        this.high = high;
        this.low = low;
        this.close = close;
        this.volume = volume;
        this.timestamp = timestamp;
    }

    public String toString() {
        return "Stock{" +
                "APIname='" + APIname + "'" +
                "timestamp = " + timestamp +
                ", open = " + open +
                ", close = " + close +
                ", high = " + high +
                ", low = " + low +
                ", volume = " + volume +
                "}";
    }

    public String getTicker() {
        return ticker;
    }
}
