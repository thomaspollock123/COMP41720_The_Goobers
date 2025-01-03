FROM eclipse-temurin:21-jre
ENV TICKER=AAPL
COPY target/stockdata-*.jar /stockdata.jar
CMD java -jar /stockdata.jar $TICKER