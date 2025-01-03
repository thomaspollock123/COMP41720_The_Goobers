FROM eclipse-temurin:21-jre
ENV TICKER=AAPL
COPY target/twelvedata-*.jar /twelvedata.jar
CMD java -jar /twelvedata.jar $TICKER