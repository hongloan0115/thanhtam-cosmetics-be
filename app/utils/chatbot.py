from app.core.logger import get_logger
import json
from enum import Enum
from app.core.openai_client import call_gpt, classify_question_with_ai
from app.crud.product import search_products, get_products_for_context, get_products_with_details

logger = get_logger(__name__)

class QuestionType(Enum):
    SEARCH_PRODUCTS = "search_products"  # Tìm kiếm sản phẩm để hiển thị danh sách
    PRODUCT_ADVICE = "product_advice"    # Tư vấn sản phẩm cần context từ DB
    GENERAL_INFO = "general_info"        # Thông tin chung về cửa hàng
    UNRELATED = "unrelated"              # Câu hỏi không liên quan

def classify_question(message: str) -> QuestionType:
    """Sử dụng AI để phân loại câu hỏi thay vì từ khóa"""
    try:
        ai_classification = classify_question_with_ai(message)
        
        # Map AI response to enum
        classification_map = {
            "search_products": QuestionType.SEARCH_PRODUCTS,
            "product_advice": QuestionType.PRODUCT_ADVICE,
            "general_info": QuestionType.GENERAL_INFO,
            "unrelated": QuestionType.UNRELATED
        }
        
        return classification_map.get(ai_classification, QuestionType.GENERAL_INFO)
        
    except Exception as e:
        logger.error(f"Error in question classification: {e}")
        return QuestionType.GENERAL_INFO  # Default fallback

def format_product_response(product):
    """Format product information for user display"""
    response = f"📦 {product['tenSanPham']}\n💰 Giá: {product['giaBan']:,}đ"
    
    if product['hinhAnh']:
        response += f"\n🖼️ Hình ảnh: {product['hinhAnh']}"
    
    response += f"\n🔗 Xem chi tiết: {product['link']}"
    return response

def handle_search_products(message: str, db):
    """Xử lý câu hỏi tìm kiếm sản phẩm"""
    logger.info("Handling search products question")
    gpt_response = call_gpt(message)
    
    func_call = gpt_response.get("function_call")
    if func_call:
        func_name = func_call.get("name")
        
        try:
            args = json.loads(func_call.get("arguments", "{}"))
            
            if func_name == "search_products":
                products = get_products_with_details(db, daXoa=False, **args)
                
                if not products:
                    return [
                        "Để tôi tìm kiếm sản phẩm cho bạn...",
                        "Rất tiếc, không tìm thấy sản phẩm phù hợp với yêu cầu của bạn."
                    ]
                
                # Phản hồi tự nhiên trước kết quả
                natural_response = "Để tôi tìm kiếm sản phẩm cho bạn..."
                result = [natural_response, f"Tôi tìm thấy {len(products)} sản phẩm phù hợp:"]
                result.extend([format_product_response(p) for p in products])
                return result
                
            elif func_name == "check_product_existence":
                from app.crud.product import check_products_exist, get_basic_products_info
                keywords = args.get("keywords", [])
                
                # Phản hồi tự nhiên đầu tiên
                checking_response = "Để tôi kiểm tra xem cửa hàng có sản phẩm này không..."
                
                existence_info = check_products_exist(db, keywords=keywords, daXoa=False)
                
                if existence_info["has_products"]:
                    products = get_basic_products_info(db, keywords=keywords, limit=5, daXoa=False)
                    
                    from app.core.openai_client import call_gpt_with_product_info
                    ai_response = call_gpt_with_product_info(
                        message, 
                        existence_info["count"], 
                        existence_info["has_products"]
                    )
                    
                    result = [
                        checking_response,
                        ai_response.get("content", "Có, cửa hàng có những sản phẩm này:")
                    ]
                    result.extend([format_product_response(p) for p in products])
                    return result
                else:
                    from app.core.openai_client import call_gpt_with_product_info
                    ai_response = call_gpt_with_product_info(message, 0, False)
                    return [
                        checking_response,
                        ai_response.get("content", "Rất tiếc, hiện tại cửa hàng chưa có sản phẩm này.")
                    ]
                    
        except Exception as e:
            logger.error(f"Error processing search: {e}")
            return [
                "Để tôi tìm kiếm cho bạn...",
                "Có lỗi xảy ra khi tìm kiếm sản phẩm. Vui lòng thử lại."
            ]
    
    return [gpt_response.get("content", "Tôi có thể giúp bạn tìm kiếm sản phẩm. Hãy cho tôi biết bạn đang tìm gì?")]

def handle_product_advice(message: str, db):
    """Xử lý câu hỏi tư vấn sản phẩm"""
    logger.info("Handling product advice question")
    gpt_response = call_gpt(message)
    
    func_call = gpt_response.get("function_call")
    if func_call and func_call.get("name") == "get_product_context":
        try:
            args = json.loads(func_call.get("arguments", "{}"))
            keywords = args.get("keywords", [])
            
            # Phản hồi tự nhiên đầu tiên
            thinking_response = "Để tôi tìm hiểu và tư vấn sản phẩm phù hợp cho bạn..."
            
            context_data = get_products_for_context(db, keywords, daXoa=False)
            
            if context_data:
                advice_response = call_gpt(message, context_data)
                
                # Lấy một vài sản phẩm để hiển thị kèm theo lời tư vấn
                from app.crud.product import get_basic_products_info
                products = get_basic_products_info(db, keywords=keywords, limit=3, daXoa=False)
                result = [
                    thinking_response,
                    advice_response.get("content", "Dựa trên thông tin sản phẩm, tôi khuyên bạn nên...")
                ]
                
                if products:
                    result.append("Một số sản phẩm tôi gợi ý:")
                    result.extend([format_product_response(p) for p in products])
                
                return result
            else:
                return [
                    thinking_response,
                    "Tôi không tìm thấy thông tin về sản phẩm bạn quan tâm. Bạn có thể cung cấp thêm chi tiết không?"
                ]
        except Exception as e:
            logger.error(f"Error processing advice: {e}")
            return [
                "Để tôi tư vấn cho bạn...",
                "Có lỗi xảy ra khi xử lý tư vấn. Vui lòng thử lại."
            ]
    
    return [gpt_response.get("content", "Tôi có thể tư vấn sản phẩm cho bạn. Hãy cho tôi biết bạn cần tư vấn gì?")]

def handle_general_info(message: str):
    """Xử lý câu hỏi thông tin chung"""
    logger.info("Handling general info question")
    gpt_response = call_gpt(message)
    return [gpt_response.get("content", "Cảm ơn bạn đã quan tâm đến cửa hàng Thanh Tâm.")]

def process_chat(message: str, db):
    logger.info(f"Processing chat message: {message}")
    
    question_type = classify_question(message)
    logger.info(f"Question classified as: {question_type.value}")
    
    try:
        if question_type == QuestionType.SEARCH_PRODUCTS:
            return handle_search_products(message, db)
        elif question_type == QuestionType.PRODUCT_ADVICE:
            return handle_product_advice(message, db)
        elif question_type == QuestionType.GENERAL_INFO:
            return handle_general_info(message)
        else:
            return ["Tôi chỉ hỗ trợ các câu hỏi liên quan đến cửa hàng mỹ phẩm Thanh Tâm. Bạn có thể hỏi về sản phẩm, giá cả, hoặc dịch vụ của chúng tôi."]
    except Exception as e:
        logger.error(f"Error in process_chat: {e}")
        return ["Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau."]
