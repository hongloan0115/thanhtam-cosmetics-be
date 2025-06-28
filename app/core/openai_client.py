from app.core.logger import get_logger
from openai import OpenAI
from app.core.config import settings

logger = get_logger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

functions = [
    {
        "name": "search_products",
        "description": "Tìm kiếm sản phẩm theo từ khóa và khoảng giá để hiển thị danh sách cho người dùng",
        "parameters": {
            "type": "object",
            "properties": {
                "min_price": {
                    "type": "number",
                    "description": "Giá bán tối thiểu của sản phẩm"
                },
                "max_price": {
                    "type": "number",
                    "description": "Giá bán tối đa của sản phẩm"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Danh sách từ khóa để tìm trong tên sản phẩm, mô tả, và tên danh mục"
                }
            }
        },
        "required": []
    },
    {
        "name": "get_product_context",
        "description": "Lấy thông tin chi tiết sản phẩm để AI có thể tư vấn, so sánh hoặc trả lời câu hỏi cụ thể",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Từ khóa để tìm sản phẩm cần thông tin chi tiết"
                }
            }
        },
        "required": ["keywords"]
    }
]

def call_gpt(message: str, context_data: str = None, history: list = None, summary: list = None):
    logger.info(f"Calling OpenAI GPT with message: {message}")
    
    system_content = (
        "Bạn là một trợ lý AI chuyên nghiệp, đóng vai trò như một nhân viên bán hàng xuất sắc cho cửa hàng mỹ phẩm Thanh Tâm. "
        "Nhiệm vụ của bạn là tư vấn tận tâm, chủ động giới thiệu sản phẩm phù hợp (lưu ý đến số lượng sản phẩm hiện có trong cửa hàng được gửi kèm trong LƯU Ý ĐẶC BIỆT) với nhu cầu khách hàng, giải thích lợi ích, thành phần, cách sử dụng sản phẩm, "
        "và khuyến khích khách lựa chọn các sản phẩm chất lượng của cửa hàng. "
        "và luôn hướng tới mục tiêu tăng doanh số cho cửa hàng. "
        "Nếu khách hỏi về kiến thức mỹ phẩm nói chung, hãy trả lời thật ngắn gọn, chính xác và khéo léo lồng ghép giới thiệu sản phẩm/dịch vụ của cửa hàng. "
        "Khi trả lời, hãy trình bày thông tin rõ ràng, dễ đọc, chỉ cần xuống dòng hợp lý để phân tách các ý, không cần sử dụng emoji, gạch đầu dòng hoặc nhấn mạnh."
    )
    
    if summary and isinstance(summary, list) and len(summary) > 0:
        system_content += "\n\nTóm tắt hội thoại trước đó:\n"
        for idx, s in enumerate(summary, 1):
            system_content += f"- Lần {idx}: {s}\n"

    if context_data:
        system_content += f"\n\n LƯU Ý ĐẶC BIỆT: Thông tin sản phẩm liên hiện có:\n{context_data}"

    logger.info(f"System prompt content:\n{system_content}")

    messages = [{"role": "system", "content": system_content}]
    # Thêm lịch sử hội thoại nếu có
    if history and isinstance(history, list):
        for msg in history:
            # msg: {"role": "user"/"assistant", "content": "..."
            if msg.get("role") in ("user", "assistant") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    kwargs = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "max_tokens": 300
    }
    if not context_data:
        kwargs["functions"] = functions
        kwargs["function_call"] = "auto"

    response = client.chat.completions.create(**kwargs)

    message_obj = response.choices[0].message
    logger.info(f"GPT response: {message_obj}")
    return message_obj.model_dump()

def classify_question_with_ai(message: str, history: list = None, summary: list = None):
    """Sử dụng OpenAI để phân loại câu hỏi của người dùng, có xét lịch sử hội thoại và tóm tắt nếu có"""
    logger.info(f"Classifying question with AI: {message}")

    system_prompt = "Bạn là một hệ thống phân loại câu hỏi cho cửa hàng mỹ phẩm. Hãy phân loại chính xác và chỉ trả về từ khóa phân loại."
    if summary and isinstance(summary, list) and len(summary) > 0:
        system_prompt += "\n\nTóm tắt hội thoại trước đó:\n"
        for idx, s in enumerate(summary, 1):
            system_prompt += f"- Lần {idx}: {s}\n"

    classification_prompt = """
    Phân loại câu hỏi sau đây vào một trong 6 loại:
    1. "search_products" - Câu hỏi tìm kiếm sản phẩm cụ thể (tìm sản phẩm, giá bao nhiêu, có sản phẩm nào...)
    2. "product_advice" - Câu hỏi tư vấn, so sánh sản phẩm (nên dùng gì, sản phẩm nào tốt, phù hợp với...)
    3. "general_info" - Câu hỏi về thông tin cửa hàng (địa chỉ, giờ mở cửa, dịch vụ, liên hệ...)
    4. "unrelated" - Câu hỏi không liên quan đến cửa hàng mỹ phẩm
    5. "possibly_related" - Câu hỏi có thể liên quan đến cửa hàng nhưng chưa rõ ràng, cần hỏi lại người dùng để làm rõ
    6. "cosmetic_knowledge" - Câu hỏi về kiến thức mỹ phẩm nói chung (cách dùng, thành phần, tác dụng, phân biệt mỹ phẩm...)

    Nếu câu hỏi liên quan đến kiến thức mỹ phẩm (cách dùng, thành phần, tác dụng, phân biệt mỹ phẩm...), hãy phân loại là "cosmetic_knowledge".

    Chỉ trả về một từ khóa: search_products, product_advice, general_info, unrelated, possibly_related, hoặc cosmetic_knowledge

    Dưới đây là lịch sử hội thoại (nếu có):
    {history_str}

    Câu hỏi mới nhất: {message}

    Phân loại:
    """

    # Xây dựng chuỗi lịch sử hội thoại nếu có
    history_str = ""
    if history and isinstance(history, list):
        for msg in history:
            role = msg.get("role")
            content = msg.get("content")
            if role and content:
                history_str += f"{role}: {content}\n"

    user_content = classification_prompt.format(
        message=message,
        history_str=history_str.strip()
    )
    logger.info(f"================================================")
    logger.info(f"Classification prompt content:\n{user_content}")
    logger.info(f"Classification prompt system:\n{system_prompt}")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            max_tokens=10,
            temperature=0
        )

        classification = response.choices[0].message.content.strip().lower()
        logger.info(f"AI classification result: {classification}")
        return classification

    except Exception as e:
        logger.error(f"Error in AI classification: {e}")
        return "general_info"  # Default fallback

def summarize_messages(messages: list, prev_summary: str = None):
    """
    Tóm tắt một đoạn hội thoại (messages: [{"role": ..., "content": ...}, ...]) thành 1-2 câu ngắn gọn.
    Nếu có prev_summary thì gộp prev_summary + messages để tóm tắt lại.
    """
    logger.info(f"Summarizing {len(messages)} messages, prev_summary: {bool(prev_summary)}")
    if not messages or not isinstance(messages, list):
        return ""

    prompt = ""
    if prev_summary:
        prompt += (
            "Đây là tóm tắt hội thoại trước đó:\n"
            f"{prev_summary}\n\n"
            "Dưới đây là các đoạn hội thoại mới tiếp theo:\n"
        )
    else:
        prompt += (
            "Hãy tóm tắt ngắn gọn (1-2 câu, tối đa 50 từ) nội dung chính của đoạn hội thoại dưới đây giữa người dùng và trợ lý AI. "
            "Chỉ nêu ý chính, không cần xưng hô, không cần liệt kê từng câu hỏi/trả lời.\n\n"
            "Đoạn hội thoại:\n"
        )
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role and content:
            prompt += f"{role}: {content}\n"

    prompt += "\nHãy tóm tắt lại toàn bộ nội dung hội thoại (bao gồm tóm tắt trước đó và các đoạn mới) thành 1-2 câu ngắn gọn nhất, chỉ nêu ý chính."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là một AI chuyên tóm tắt hội thoại ngắn gọn, súc tích, chỉ nêu ý chính."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.2,
        )
        summary = response.choices[0].message.content.strip()
        logger.info(f"Summary result: {summary}")
        return summary
    except Exception as e:
        logger.error(f"Error in summarize_messages: {e}")
        return ""
