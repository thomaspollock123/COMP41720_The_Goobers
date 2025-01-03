FROM eclipse-temurin:21-jre
ENV TICKER=AAPL
COPY target/finnhub-*.jar /finnhub.jar
CMD java -jar /finnhub.jar $TICKER