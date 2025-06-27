from app.core.logger import get_logger
from fastapi import APIRouter, WebSocket, Depends
import asyncio
from app.db.database import get_db
from app.utils.chatbot import process_chat

logger = get_logger(__name__)

router = APIRouter()

@router.websocket("/chat")
async def chat(ws: WebSocket, db=Depends(get_db)):
    await ws.accept()
    logger.info("WebSocket connection accepted")
    try:
        while True:
            data = await ws.receive_text()
            # Nếu client gửi dạng JSON chứa cả message và history
            import json
            try:
                payload = json.loads(data)
                msg = payload["message"]
                history = payload.get("history")
                # Chỉ lấy 2 tin gần nhất nếu có
                if history and isinstance(history, list):
                    history = history[-15:]
            except Exception:
                msg = data
                history = None

            logger.info(f"Received message: {msg}")
            responses = process_chat(msg, db, history=history)
            
            # Gửi từng phản hồi với delay tự nhiên
            for i, response in enumerate(responses):
                # Đảm bảo response là str
                if not isinstance(response, str):
                    import json
                    response = json.dumps(response, ensure_ascii=False)
                await ws.send_text(response)
                logger.info(f"Sent response {i+1}: {response}")
                
                # Thêm delay giữa các phản hồi để tự nhiên hơn
                if i < len(responses) - 1:  # Không delay sau phản hồi cuối
                    if i == 0:  # Delay ngắn sau phản hồi đầu tiên
                        await asyncio.sleep(1)
                    else:  # Delay rất ngắn giữa các kết quả
                        await asyncio.sleep(0.3)
                        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws.close()
