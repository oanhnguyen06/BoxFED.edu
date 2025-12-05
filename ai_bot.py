# -*- coding: utf-8 -*-
# Tên File: server_rearranged.py (Phiên bản đã sắp xếp lại)

import re
import os
from flask import Flask, request, jsonify
from flask_cors import CORS 
from openai import OpenAI
import random 

# ======================================================================
## 0. KHỞI TẠO CLIENT VÀ THIẾT LẬP FLASK (SETUP)
# ======================================================================

# Cấu hình Client để kết nối với Ollama đang chạy cục bộ
try:
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama' 
    )
except Exception as e:
    print(f"Lỗi khởi tạo OpenAI Client: {e}")
    client = None

# KHỞI TẠO ỨNG DỤNG FLASK
app = Flask(__name__)
# Cho phép truy cập chéo tên miền (CORS)
CORS(app) 

# ======================================================================
## 1. ĐỊNH NGHĨA ENDPOINT CHATBOT (MAIN LOGIC)
# ======================================================================

# Endpoint giả định cho dữ liệu giảng viên (thường dùng cho Frontend)
@app.route('/api/lecturers', methods=['GET'])
def get_lecturers_data():
    """Endpoint giả định cho dữ liệu giảng viên (hiện đang rỗng)."""
    return jsonify([]) 

# ĐỊNH NGHĨA ENDPOINT CHATBOT CHÍNH
@app.route('/chat', methods=['POST'])
def chat():
    """
    Xử lý yêu cầu Chat, dùng logic tĩnh (Python) hoặc Ollama (LLM).
    Quyết định xử lý dựa trên Intent Parsing.
    """
    
    data = request.get_json()
    user_input = data.get('message', None) 

    if not user_input:
        return jsonify({'error': 'Vui lòng gửi tin nhắn.'}), 400

    # Phân tích ý định người dùng (Hàm được định nghĩa ở phần 2)
    intent = parse_intent(user_input)
    
    # --- 1. Xử lý Ý định bằng Logic Tra cứu tĩnh (Ưu tiên) ---
    if intent["type"] == "single_query":
        # Gọi hàm xử lý tĩnh (đảm bảo độ chính xác cao)
        reply = get_program_info(intent["program"], intent["topic"])
        return jsonify({'bot_reply': reply, 'source': 'static_data'})
        
    elif intent["type"] == "compare":
        # Gọi hàm so sánh tĩnh (đảm bảo độ chính xác cao)
        reply = compare_programs(intent["topic"])
        return jsonify({'bot_reply': reply, 'source': 'static_data'})

    elif intent["type"] == "greeting":
        reply = "Xin chào! Tôi là chatbot tra cứu thông tin về Chương trình **Công nghệ Giáo dục (CNGD)** và **Quản lý Giáo dục (QLGD)**. Tôi có thể giúp bạn tìm thông tin chi tiết hoặc **so sánh** hai ngành này."
        return jsonify({'bot_reply': reply, 'source': 'greeting'})

    # --- 2. Xử lý các câu hỏi khác bằng LLM / Ollama (Fallback) ---
    elif intent["type"] == "llm_query" or intent["type"] == "ambiguous_compare":
        
        if client is None:
            reply = "Lỗi: Không thể kết nối với Ollama API. Vui lòng kiểm tra xem Ollama có đang chạy trên cổng 11434 không."
            return jsonify({'bot_reply': reply, 'source': 'error'}), 500

        try:
            # System Prompt định hướng cho Ollama
            messages = [
                {"role": "system", "content": "Bạn là một trợ lý thân thiện và hữu ích. Hãy trả lời các câu hỏi về giáo dục, công nghệ và các vấn đề chung. Luôn trả lời bằng Tiếng Việt."},
                {"role": "user", "content": user_input}
            ]
            
            # Gọi API Ollama
            response = client.chat.completions.create(
                model="gemma2:9b", 
                messages=messages,
                temperature=0.7
            )
            
            reply = response.choices[0].message.content
            
            return jsonify({'bot_reply': reply, 'source': 'ollama'})

        except Exception as e:
            print(f"Lỗi khi gọi Ollama API: {e}")
            return jsonify({'error': f'Lỗi kết nối Backend. Chi tiết lỗi: {e}'}), 500
    
    return jsonify({'bot_reply': "Tôi chưa hiểu rõ câu hỏi của bạn. Vui lòng hỏi lại rõ ràng hơn. (Chuyển cho LLM...)", 'source': 'llm_fallback'})

# ======================================================================
## 2. LOGIC XỬ LÝ DỮ LIỆU TĨNH (STATIC QUERY LOGIC)
# ======================================================================

def format_list_to_string(data_list, prefix=" - ", heading=""):
    """Định dạng danh sách các mục tiêu/cơ hội thành chuỗi có dấu đầu dòng."""
    output = f"{heading}\n" if heading else ""
    for item in data_list:
        output += f"{prefix}{item}\n"
    return output.strip()

def get_program_info(program_data, topic):
    """Lấy thông tin chung cho một chủ đề (Mục tiêu, Nghề nghiệp, Slogan, v.v.)."""
    program_name = program_data["TEN_NGANH"]
    
    if topic == "slogan":
        return f"Slogan của ngành **{program_name}** là: **{program_data['SLOGAN']}**"
    elif topic == "mục tiêu":
        heading = f"Mục tiêu của Chương trình {program_name} là trang bị các năng lực sau:"
        return format_list_to_string(program_data["MUC_TIEU"], prefix="  - ", heading=heading)
    elif topic == "nghề nghiệp":
        heading = f"Cơ hội nghề nghiệp dành cho sinh viên tốt nghiệp ngành {program_name} rất đa dạng, bao gồm:"
        return format_list_to_string(program_data["CO_HOI_NGHE_NGHIEP"], prefix="  * ", heading=heading)
    elif topic == "xét tuyển":
        output = f"Các hình thức xét tuyển và tổ hợp của ngành **{program_name}**:\n"
        output += "| Hình thức | Tổ hợp xét tuyển |\n"
        output += "|:---------|:-----------------|\n"
        for hinh_thuc, to_hop in program_data["XET_TUYEN"].items():
            output += f"| {hinh_thuc} | {to_hop} |\n"
        return output.strip()
    elif topic == "doanh nghiệp":
        heading = f"Các tổ chức, doanh nghiệp hợp tác/hỗ trợ thực tập cho ngành {program_name} bao gồm:"
        return format_list_to_string(program_data["DOANH_NGHIEP_HOP_TAC"], prefix="  * ", heading=heading)
    elif topic == "định hướng":
        heading = f"Ngành {program_name} có các định hướng chuyên sâu sau:"
        return format_list_to_string(program_data["DINH_HUONG_CHUYEN_SAU"], prefix="  - ", heading=heading)
        
    return f"Thông tin về {topic} của ngành {program_name} hiện không có trong dữ liệu tĩnh."

def compare_programs(topic):
    """So sánh thông tin giữa hai ngành học (CNGD vs QLGD)."""
    if topic == "xét tuyển":
        output = "**SO SÁNH TỔ HỢP XÉT TUYỂN (CNGD vs QLGD)**\n"
        output += "| Hình thức | Công nghệ Giáo dục | Quản lý Giáo dục |\n"
        output += "|:---------|:--------------------|:-----------------|\n"
        
        for hinh_thuc, to_hop_cngd in CNGD_DATA["XET_TUYEN"].items():
            to_hop_qlgd = QLGD_DATA["XET_TUYEN"].get(hinh_thuc, "-")
            output += f"| {hinh_thuc} | {to_hop_cngd} | {to_hop_qlgd} |\n"
        return output.strip()
    elif topic == "slogan":
        output = "**SO SÁNH SLOGAN**\n"
        output += f"**CNGD:** {CNGD_DATA['SLOGAN']}\n"
        output += f"**QLGD:** {QLGD_DATA['SLOGAN']}\n"
        return output.strip()
    elif topic == "định hướng":
        output = "**SO SÁNH ĐỊNH HƯỚNG CHUYÊN SÂU**\n"
        output += "**Công nghệ Giáo dục:**\n"
        output += format_list_to_string(CNGD_DATA["DINH_HUONG_CHUYEN_SAU"], prefix="  - ") + "\n"
        output += "\n**Quản lý Giáo dục:**\n"
        output += format_list_to_string(QLGD_DATA["DINH_HUONG_CHUYEN_SAU"], prefix="  - ") + "\n"
        return output.strip()
        
    return "Chức năng so sánh chi tiết cho mục tiêu hoặc nghề nghiệp đang được phát triển. Vui lòng xem thông tin riêng lẻ."

def parse_intent(user_input):
    """
    Phân tích đầu vào người dùng (Intent Routing) để xác định:
    Ngành nào, chủ đề gì, và nên dùng Logic tĩnh hay LLM.
    """
    input_lower = user_input.lower().strip()
    
    # 1. Xác định Ngành học
    program_match = None
    if re.search(r'công nghệ giáo dục|cngd', input_lower):
        program_match = CNGD_DATA
    elif re.search(r'quản lý giáo dục|qlgd|quản lí giáo dục', input_lower):
        program_match = QLGD_DATA
        
    # 2. Xác định Ý định So sánh
    if re.search(r'so sánh|so sanh|khác nhau|điểm chung', input_lower):
        topic = None
        if re.search(r'xét tuyển|tổ hợp|khối', input_lower):
            topic = "xét tuyển"
        elif re.search(r'slogan|khẩu hiệu', input_lower):
            topic = "slogan"
        elif re.search(r'định hướng|chuyên sâu', input_lower):
            topic = "định hướng"
        
        if topic:
            return {"type": "compare", "topic": topic}
        return {"type": "ambiguous_compare"} # Chuyển cho LLM

    # 3. Xác định Chủ đề chi tiết (Topic)
    topic_match = None
    if re.search(r'slogan|khẩu hiệu', input_lower):
        topic_match = "slogan"
    elif re.search(r'mục tiêu|học được gì|trang bị', input_lower):
        topic_match = "mục tiêu"
    elif re.search(r'nghề nghiệp|cơ hội|làm việc|vị trí', input_lower):
        topic_match = "nghề nghiệp"
    elif re.search(r'xét tuyển|tổ hợp|khối', input_lower):
        topic_match = "xét tuyển"
    elif re.search(r'doanh nghiệp|công ty|đối tác|thực tập', input_lower):
        topic_match = "doanh nghiệp"
    elif re.search(r'định hướng|chuyên sâu', input_lower):
        topic_match = "định hướng"
        
    # 4. Trả về kết quả phân tích
    if program_match and topic_match: 
        return {"type": "single_query", "program": program_match, "topic": topic_match}
    elif re.search(r'chào|xin chào|start', input_lower):
        return {"type": "greeting"}
    else:
        return {"type": "llm_query"} # Chuyển cho LLM xử lý (fallback)


# ======================================================================
## 3. DỮ LIỆU CHƯƠNG TRÌNH ĐÀO TẠO (STATIC DATA)
# ======================================================================

# Dữ liệu Ngành Công nghệ Giáo dục (CNGD)
CNGD_DATA = {
    "TEN_NGANH": "Công nghệ Giáo dục",
    "SLOGAN": "CÔNG NGHỆ GIÁO DỤC - KIẾN TẠO TƯƠNG LAI SỐ", 
    "MUC_TIEU": [
        "Thiết kế, phát triển đa phương tiện và thiết bị dạy học hiện đại.", 
        "Thiết kế, phát triển các phần mềm giáo dục có tính tương tác ảo (game, mô phỏng, VR-AR).", 
        "Thiết kế, phát triển các nội dung dạy học số (bài giảng e-learning, trắc nghiệm hình ảnh…) cho các khoá học trực tuyến.", 
        "Thiết kế, phát triển các cổng đào tạo trực tuyến; vận hành, quản trị các hệ thống dạy học trực tuyến.", 
        "Thiết kế, phát triển các môi trường học tập số.", 
        "Nghiên cứu, thiết kế và phát triển các giải pháp chuyển đổi số trong giáo dục, dạy học và đào tạo.", 
        "Tư duy phản biện, kỹ năng làm việc nhóm và năng lực giải quyết vấn đề.", 
        "Khả năng tham gia giảng dạy trong lĩnh vực giáo dục truyền thông đa phương tiện.", 
        "Năng lực tự học, nghiên cứu trong lĩnh vực Khoa học giáo dục và truyền thông.", 
    ],
    "CO_HOI_NGHE_NGHIEP": [
        "Chuyên viên phân tích nghiệp vụ (Business Analyst) của các tổ chức, các sản phẩm, dịch vụ giáo dục.", 
        "Chuyên viên quản trị hệ thống quản lý học tập (LMS), nội dung học tập (LCMS).", 
        "Chuyên viên thiết kế và sáng tạo nội dung học tập đa phương tiện (videos, mô phỏng, VR, AR, trò chơi giáo dục…).", 
        "Chuyên viên thiết kế và sáng tạo khoá học số (MOOCs, e-learning, blended learning…).", 
        "Chuyên viên thiết kế học liệu theo hướng tiếp cận STEAM/STEM, giáo viên dạy theo mô hình STEAM/STEM.", 
        "Chuyên viên phát triển nội dung tại các chương trình khoa học – giáo dục của các đài truyền hình, truyền thông và mạng xã hội.", 
        "Kỹ thuật viên quản trị hệ thống dạy học trực tuyến, chuyên viên thiết kế phát triển các cổng đào tạo trực tuyến.", 
        "Phụ trách công tác đào tạo trong doanh nghiệp, trường học và các tổ chức.", 
        "Học tiếp lên Thạc sĩ/Nghiên cứu sinh lĩnh vực Khoa học giáo dục (định hướng Công nghệ giáo dục).", 
    ],
    "XET_TUYEN": {
        "Tài năng": "Giải thưởng HSG QG-QT/Chứng chỉ Quốc tế/HSNL", 
        "Đánh giá tư duy": "K00", 
        "Tốt nghiệp THPT 2024": "A00, A01, D01, K01", 
    },
    "DOANH_NGHIEP_HOP_TAC": [
        "Dự án EDUNEXT – Tập đoàn FPT", 
        "Học viện Viettel – Tập đoàn Viễn thông Quân đội Viettel", 
        "Công ty Công nghệ thông tin VNPT (VNPT-IT)", 
        "Công ty Cổ phần Edulive", 
        "Học viện TEKY", 
        "Công ty Cổ phần Giáo dục KDI", 
        "Công ty e-Việt Learning (Công ty TNHH Khoa Trí)", 
        "Công ty công nghệ Liberal", 
        "Công Ty Cp Công Nghệ Giáo Dục Thiên Hà Xanh", 
        "Công ty cổ phần Công nghệ giáo dục eJoy", 
        "Nền tảng Edvin.ai", 
        "Nền tảng Moddie.ai", 
        "Nền tảng ClassIn Việt Nam", 
        "Công ty CP Doanh nghiệp xã hội HR Companion", 
        "Công ty CP Deha Việt Nam", 
        "Và nhiều doanh nghiệp công nghệ giáo dục trong và ngoài nước.", 
    ],
    "DINH_HUONG_CHUYEN_SAU": [
        "Phát triển đa phương tiện giáo dục: Tạo hình 2D/3D, Đồ hoạ hình động, Trí tuệ nhân tạo, AR/VR/Gamification…", 
        "Môi trường học tập số: E-learning, B-learning, giáo dục STEAM/STEM, Xuất bản ấn phẩm truyền thông, học liệu số…", 
        "Đào tạo số phục vụ phát triển, bồi dưỡng nhân sự tại doanh nghiệp thích ứng với công nghiệp 4.0.", 
    ]
}

# Dữ liệu Ngành Quản lý Giáo dục (QLGD)
QLGD_DATA = {
    "TEN_NGANH": "Quản lý Giáo dục",
    "SLOGAN": "Đổi mới giáo dục - Kết nối Chất lượng và Chuyển đổi số", 
    "MUC_TIEU": [
        "Kiến thức nền tảng và chuyên môn vững chắc về quản lý giáo dục và quản lý chất lượng giáo dục và đào tạo.", 
        "Kỹ năng nghề nghiệp và phẩm chất cá nhân cần thiết để thành công trong các vị trí việc làm.", 
        "Kỹ năng xã hội cần thiết để làm việc hiệu quả trong nhóm liên ngành và trong môi trường quốc tế.", 
        "Năng lực hình thành ý tưởng, thiết kế, triển khai và vận hành các dự án, đề tài nghiên cứu trong lĩnh vực quản lý giáo dục, quản lý chất lượng giáo dục và đào tạo.", 
        "Khả năng tự đào tạo, vận dụng kiến thức, cập nhật kiến thức mới để giải quyết vấn đề cụ thể trong thực tế.", 
        "Năng lực hình thành ý tưởng thiết kế, triển khai và vận hành khóa học giàu công nghệ hoặc sản phẩm đa phương tiện.", 
        "Năng lực dạy học và quản lý các khóa đào tạo tại doanh nghiệp, cơ sở giáo dục.", 
        "Phẩm chất chính trị, đạo đức nghề nghiệp, có ý thức phục vụ nhân dân, có sức khỏe.", 
    ],
    "CO_HOI_NGHE_NGHIEP": [
        "Chuyên viên quản lý hành chính giáo dục tại các cơ quan quản lý giáo dục (Bộ/Sở GD&ĐT, Tổng Cục GDNN, v.v.).", 
        "Chuyên viên phụ trách công tác văn hóa, giáo dục tại cơ quan chính quyền các cấp (UBND, trung tâm bồi dưỡng).", 
        "Chuyên viên/Nghiên cứu viên tại các trung tâm, viện nghiên cứu giáo dục.", 
        "Chuyên viên các bộ phận hành chính, tài chính, quản trị cơ sở vật chất, tuyển sinh, truyền thông, chuyển đổi số tại cơ sở giáo dục.", 
        "Chuyên viên khảo thí, kiểm định chất lượng, thanh tra giáo dục, quản lý nhân sự tại các cơ sở giáo dục trong và ngoài công lập.", 
        "Chuyên viên phát triển chương trình đào tạo, phương pháp giảng dạy, phương pháp đánh giá.", 
        "Chuyên viên xây dựng hệ thống thông tin, cơ sở dữ liệu đảm bảo chất lượng, kiểm định chất lượng.", 
        "Chuyên viên xây dựng cơ sở dữ liệu về xếp hạng, so chuẩn đối sánh và gắn sao đại học, đánh giá chất lượng cơ sở giáo dục.", 
        "Chuyên viên triển khai các chương trình, dự án xúc tiến thương mại, đầu tư phát triển giáo dục.", 
        "Khởi nghiệp nhằm cung ứng các dịch vụ giáo dục.", 
        "Học tiếp lên Thạc sĩ Quản lý giáo dục để trở thành giảng viên.", 
    ],
    "XET_TUYEN": {
        "Tài năng": "Giải thưởng HSG QG-QT/Chứng chỉ Quốc tế/HSNL", 
        "Đánh giá tư duy": "K00", 
        "Tốt nghiệp THPT": "A00, A01, D01, K01", 
    },
    "DOANH_NGHIEP_HOP_TAC": [
        "Đại học Bách khoa Hà Nội", 
        "Trường Cao đẳng nghề Bách khoa Hà Nội", 
        "Trường THCS&THPT Tạ Quang Bửu", 
        "Bộ Giáo dục và Đào tạo", 
        "Sở Giáo dục và Đào tạo Hà Nội và các sở Giáo dục tại các địa phương khác", 
        "Phòng giáo dục quận Hai Bà Trưng, Hoàng Mai, Cầu Giấy…", 
        "Cao đẳng nghề Việt – Hàn Hà Nội", 
        "Công ty TNHH Khoa Trí", 
        "Trường học Công nghệ Teky", 
        "Công ty Cổ phần Edulive Toàn Cầu", 
        "Công ty Công nghệ Liberal", 
        "Công ty Cổ phần Doanh nghiệp Xã hội HR Companion", 
        "Datality Lab Limited", 
        "Và nhiều doanh nghiệp công nghệ giáo dục trong và ngoài nước…", 
    ],
    "DINH_HUONG_CHUYEN_SAU": [
        "Quản lý giáo dục số: Marketing và Truyền thông trong giáo dục số, Quản lý chiến lược giáo dục trong kỷ nguyên số, Quản lý chất lượng giáo dục trực tuyến…", 
        "Quản lý chất lượng giáo dục: Kiểm định chất lượng giáo dục, Nhập môn xếp hạng cơ sở giáo dục đại học, Lập kế hoạch và Thiết kế Đo lường đánh giá...", 
    ]
}


# ====================================================================
# CHẠY ỨNG DỤNG FLASK (MAIN EXECUTION)
# ====================================================================
if __name__ == '__main__':
    print("=================================================================")
    print("Hệ thống Chatbot/API đã khởi động (Đã sắp xếp lại code)...")
    print("Truy cập http://localhost:5000/chat (POST) để dùng Chatbot.")
    print("Đảm bảo Ollama đang chạy trên cổng 11434 và mô hình gemma2:9b đã được tải.")
    print("=================================================================")
    
    # Khởi chạy máy chủ Flask
    app.run(host='0.0.0.0', port=5000, debug=True)
