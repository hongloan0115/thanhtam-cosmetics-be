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

def call_gpt(message: str, context_data: str = None, history: list = None):
    logger.info(f"Calling OpenAI GPT with message: {message}")
    
    system_content = (
        "Bạn là một trợ lý AI chuyên nghiệp cho cửa hàng mỹ phẩm Thanh Tâm. "
        "Chỉ trả lời các câu hỏi liên quan đến sản phẩm, dịch vụ, chương trình khuyến mãi, "
        "hoặc thông tin về cửa hàng Thanh Tâm. Nếu người dùng hỏi về chủ đề không liên quan, "
        "hãy lịch sự từ chối và thông báo rằng bạn chỉ hỗ trợ các vấn đề liên quan đến cửa hàng."
    )
    
    if context_data:
        system_content += f"\n\nThông tin sản phẩm hiện có:\n{context_data}"

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

def classify_question_with_ai(message: str, history: list = None):
    """Sử dụng OpenAI để phân loại câu hỏi của người dùng, có xét lịch sử hội thoại"""
    logger.info(f"Classifying question with AI: {message}")

    classification_prompt = """
    Phân loại câu hỏi sau đây vào một trong 5 loại:
    1. "search_products" - Câu hỏi tìm kiếm sản phẩm cụ thể (tìm sản phẩm, giá bao nhiêu, có sản phẩm nào...)
    2. "product_advice" - Câu hỏi tư vấn, so sánh sản phẩm (nên dùng gì, sản phẩm nào tốt, phù hợp với...)
    3. "general_info" - Câu hỏi về thông tin cửa hàng (địa chỉ, giờ mở cửa, dịch vụ, liên hệ...)
    4. "unrelated" - Câu hỏi không liên quan đến cửa hàng mỹ phẩm
    5. "possibly_related" - Câu hỏi có thể liên quan đến cửa hàng nhưng chưa rõ ràng, cần hỏi lại người dùng để làm rõ

    Nếu câu hỏi liên quan đến cửa hàng nhưng chưa đủ thông tin để trả lời, hãy phân loại là "possibly_related" để trợ lý có thể hỏi lại người dùng cho rõ hơn.

    Chỉ trả về một từ khóa: search_products, product_advice, general_info, unrelated, hoặc possibly_related

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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là một hệ thống phân loại câu hỏi cho cửa hàng mỹ phẩm. Hãy phân loại chính xác và chỉ trả về từ khóa phân loại."
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
