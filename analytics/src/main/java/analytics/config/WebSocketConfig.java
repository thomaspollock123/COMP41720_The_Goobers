package analytics.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        // "/ws/predictions" is the endpoint the client will connect to
        registry.addHandler(PredictionHandler(), "/ws/predictions")
                .setAllowedOrigins("*");
    }

    @Bean
    public PredictionHandler PredictionHandler() {
        return new PredictionHandler();
    }
}
