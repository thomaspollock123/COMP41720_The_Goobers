package analytics.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "predictions") // TODO: change to 'stock_data'
public class Prediction {

    @Id
    private String id;
    private String ticker;
    private long timestamp;
    private double open;
    private double high;
    private double low;
    private double close;
    private int month;
    private int day;
    private int hour;
    private int minute;
    private int year_2022;
    private int year_2023;
    private int year_2024;
    private double close_diff;
    private double close_previous_diff;
    private double rolling_average_log;
    private double rolling_average_3;
    private double rolling_average_5;
    private double rolling_average_10;
    private int year;
    private String APIname;
    private int prediction;            // 1 => Up, 0 => Down

    public Prediction() { }

    public Prediction(
            String ticker,
            long timestamp,
            double open,
            double high,
            double low,
            double close,
            int month,
            int day,
            int hour,
            int minute,
            int year_2022,
            int year_2023,
            int year_2024,
            double close_diff,
            double close_previous_diff,
            double rolling_average_log,
            double rolling_average_3,
            double rolling_average_5,
            double rolling_average_10,
            int year,
            String APIname,
            int prediction
    ) {
        this.ticker = ticker;
        this.timestamp = timestamp;
        this.open = open;
        this.high = high;
        this.low = low;
        this.close = close;
        this.month = month;
        this.day = day;
        this.hour = hour;
        this.minute = minute;
        this.year_2022 = year_2022;
        this.year_2023 = year_2023;
        this.year_2024 = year_2024;
        this.close_diff = close_diff;
        this.close_previous_diff = close_previous_diff;
        this.rolling_average_log = rolling_average_log;
        this.rolling_average_3 = rolling_average_3;
        this.rolling_average_5 = rolling_average_5;
        this.rolling_average_10 = rolling_average_10;
        this.year = year;
        this.APIname = APIname;
        this.prediction = prediction;
    }

    // getters and setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTicker() {
        return ticker;
    }

    public void setTicker(String ticker) {
        this.ticker = ticker;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    public double getOpen() {
        return open;
    }
    public void setOpen(double open) {
        this.open = open;
    }

    public double getHigh() {
        return high;
    }
    public void setHigh(double high) {
        this.high = high;
    }

    public double getLow() {
        return low;
    }
    public void setLow(double low) {
        this.low = low;
    }

    public double getClose() {
        return close;
    }
    public void setClose(double close) {
        this.close = close;
    }

    public int getMonth() {
        return month;
    }
    public void setMonth(int month) {
        this.month = month;
    }

    public int getDay() {
        return day;
    }
    public void setDay(int day) {
        this.day = day;
    }

    public int getHour() {
        return hour;
    }
    public void setHour(int hour) {
        this.hour = hour;
    }

    public int getMinute() {
        return minute;
    }
    public void setMinute(int minute) {
        this.minute = minute;
    }

    public int getYear_2022() {
        return year_2022;
    }
    public void setYear_2022(int year_2022) {
        this.year_2022 = year_2022;
    }

    public int getYear_2023() {
        return year_2023;
    }
    public void setYear_2023(int year_2023) {
        this.year_2023 = year_2023;
    }

    public int getYear_2024() {
        return year_2024;
    }
    public void setYear_2024(int year_2024) {
        this.year_2024 = year_2024;
    }

    public double getClose_diff() {
        return close_diff;
    }
    public void setClose_diff(double close_diff) {
        this.close_diff = close_diff;
    }

    public double getClose_previous_diff() {
        return close_previous_diff;
    }
    public void setClose_previous_diff(double close_previous_diff) {
        this.close_previous_diff = close_previous_diff;
    }

    public double getRolling_average_log() {
        return rolling_average_log;
    }
    public void setRolling_average_log(double rolling_average_log) {
        this.rolling_average_log = rolling_average_log;
    }

    public double getRolling_average_3() {
        return rolling_average_3;
    }
    public void setRolling_average_3(double rolling_average_3) {
        this.rolling_average_3 = rolling_average_3;
    }

    public double getRolling_average_5() {
        return rolling_average_5;
    }
    public void setRolling_average_5(double rolling_average_5) {
        this.rolling_average_5 = rolling_average_5;
    }

    public double getRolling_average_10() {
        return rolling_average_10;
    }
    public void setRolling_average_10(double rolling_average_10) {
        this.rolling_average_10 = rolling_average_10;
    }

    public int getYear() {
        return year;
    }
    public void setYear(int year) {
        this.year = year;
    }

    public String getAPIname() {
        return APIname;
    }
    public void setAPIname(String APIname) {
        this.APIname = APIname;
    }

    public int getPrediction() {
        return prediction;
    }

    public void setPrediction(int prediction) {
        this.prediction = prediction;
    }

    @Override
    public String toString() {
        return "Prediction{" +
                "id='" + id + '\'' +
                ", ticker=" + ticker +
                ", timestamp=" + timestamp +
                ", open=" + open +
                ", high=" + high +
                ", low=" + low +
                ", close=" + close +
                ", month=" + month +
                ", day=" + day +
                ", hour=" + hour +
                ", minute=" + minute +
                ", year_2022=" + year_2022 +
                ", year_2023=" + year_2023 +
                ", year_2024=" + year_2024 +
                ", close_diff=" + close_diff +
                ", close_previous_diff=" + close_previous_diff +
                ", rolling_average_log=" + rolling_average_log +
                ", rolling_average_3=" + rolling_average_3 +
                ", rolling_average_5=" + rolling_average_5 +
                ", rolling_average_10=" + rolling_average_10 +
                ", year=" + year +
                ", APIname='" + APIname + '\'' +
                ", prediction=" + prediction +
                '}';
    }
}
