package analytics.config;

import org.springframework.web.socket.handler.AbstractWebSocketHandler;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import java.io.IOException;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;


public class PredictionHandler extends AbstractWebSocketHandler {

    private final Set<WebSocketSession> sessions = ConcurrentHashMap.newKeySet();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        sessions.add(session);
        System.out.println("New WebSocket connection: " + session.getId());
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        sessions.remove(session);
        System.out.println("WebSocket connection closed: " + session.getId()
                + ", CloseStatus: " + status);
    }

    public void broadcast(String text) {
        for (WebSocketSession ws : sessions) {
            if (ws.isOpen()) {
                try {
                    ws.sendMessage(new TextMessage(text));
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
