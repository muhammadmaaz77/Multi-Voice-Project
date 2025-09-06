"""
WebSocket streaming routes for Phase 5A - Simplified for testing
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Simple WebSocket endpoint for testing"""
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass

@router.get("/ws-test")
async def websocket_test_page():
    """Test page for WebSocket connection"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Type a message">
        <button onclick="sendMessage()">Send</button>
        
        <script>
            const ws = new WebSocket('ws://localhost:8000/api/v1/ws/test_session');
            
            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                const div = document.createElement('div');
                div.textContent = event.data;
                messages.appendChild(div);
            };
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                ws.send(input.value);
                input.value = '';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
