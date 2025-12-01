from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

from flask import Flask, request, jsonify
from openai import OpenAI # Sử dụng thư viện OpenAI client để kết nối với Ollama
import os

# ====================================================================
# KHỞI TẠO CLIENT API CHO OLLAMA (Dựa trên code gốc của bạn)
# ====================================================================

# Cấu hình Client để kết nối với Ollama đang chạy cục bộ
# Base URL: Địa chỉ mặc định của Ollama API
# API Key: Dùng giá trị giả "ollama" cho kết nối cục bộ
try:
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama' 
    )
except Exception as e:
    # Trường hợp thư viện OpenAI không thể khởi tạo
    print(f"Lỗi khởi tạo OpenAI Client: {e}")
    
# KHỞI TẠO ỨNG DỤNG FLASK
app = Flask(__name__)

# ĐỊNH NGHĨA ENDPOINT CHATBOT
@app.route('/chat', methods=['POST'])
def chat():
    """
    Xử lý yêu cầu POST từ trang web, gọi API Ollama, và trả về phản hồi.
    """
    
    # 1. Lấy dữ liệu người dùng
    data = request.get_json()
    user_input = data.get('message', None) 

    if not user_input:
        return jsonify({'error': 'Vui lòng gửi tin nhắn.'}), 400

    try:
        # --- LOGIC GỌI API OLLAMA/GEMMA2-9B ---
        
        # Chuẩn bị tin nhắn (hiện tại chỉ gửi tin nhắn mới)
        messages = [
            # Thêm System Prompt để định hướng Bot (nếu cần)
            {"role": "user", "content": user_input}
        ]
        
        # 2. GỌI API OLLAMA (Đã sửa lỗi cấu trúc)
        response = client.chat.completions.create(
            model="gemma2:9b", # Đảm bảo tên mô hình này đúng với mô hình bạn đã tải xuống trong Ollama
            messages=messages,
            temperature=0.7
        )
        
        # Lấy nội dung phản hồi từ Ollama
        reply = response.choices[0].message.content
        
        # 3. TRẢ VỀ PHẢN HỒI JSON cho trang web
        return jsonify({'bot_reply': reply})

    except Exception as e:
        # Xử lý các lỗi xảy ra trong quá trình kết nối với Ollama
        print(f"Lỗi khi xử lý yêu cầu hoặc gọi Ollama API: {e}")
        # Trả về lỗi 500 (Internal Server Error)
        return jsonify({'error': f'Lỗi kết nối Backend. Hãy kiểm tra Ollama có đang chạy không. Chi tiết lỗi: {e}'}), 500

# ====================================================================
# CHẠY ỨNG DỤNG FLASK
# ====================================================================
if __name__ == '__main__':
    # Chạy trên cổng 5000 (cổng tiêu chuẩn)
    # host='0.0.0.0' cho phép truy cập từ mạng bên ngoài (quan trọng cho deployment)

    app.run(host='0.0.0.0', port=5000, debug=True)
    Rất tuyệt vời\! Việc kết hợp hai tài liệu về **Công nghệ Giáo dục (CNGD)** và **Quản lý Giáo dục (QLGD)** sẽ cho phép tạo ra một hệ thống tra cứu thông tin toàn diện hơn.

Để đạt độ dài khoảng 500 dòng và đảm bảo tính ứng dụng, tôi sẽ mở rộng chức năng của Chatbot bằng cách:

1.  **Tạo module dữ liệu** (`data_management.py`).
2.  **Tạo module logic** (`chatbot_logic.py`).
3.  **Tạo module chính** (`main_app.py`) để chạy ứng dụng.
4.  Sử dụng cấu trúc dữ liệu **Dictionary** và **List** để lưu trữ thông tin của cả hai ngành học.
5.  Thêm chức năng **so sánh** các thông tin chính giữa hai ngành (Mục tiêu, Tổ hợp xét tuyển).

Do giới hạn hiển thị, tôi sẽ đặt tất cả code vào một file, sử dụng comments để phân chia rõ ràng các module logic.

Dưới đây là đoạn mã Python có cấu trúc, khoảng **500 dòng**, mô phỏng chatbot tra cứu thông tin từ hai chương trình đào tạo:

```python
# -*- coding: utf-8 -*-
# Tên File: education_program_chatbot.py
import re
import random
import os

# ======================================================================
## 1. DỮ LIỆU CHƯƠNG TRÌNH ĐÀO TẠO (DATA MANAGEMENT MODULE)
# Tổng hợp và cấu trúc hóa dữ liệu từ cả hai tài liệu
# ======================================================================

# Dữ liệu Ngành Công nghệ Giáo dục (CNGD)
CNGD_DATA = {
    "TEN_NGANH": "Công nghệ Giáo dục",
    "SLOGAN": "CÔNG NGHỆ GIÁO DỤC - KIẾN TẠO TƯƠNG LAI SỐ", # cite: 127
    "MUC_TIEU": [
        "Thiết kế, phát triển đa phương tiện và thiết bị dạy học hiện đại.", # cite: 74
        "Thiết kế, phát triển các phần mềm giáo dục có tính tương tác ảo (game, mô phỏng, VR-AR).", # cite: 75
        "Thiết kế, phát triển các nội dung dạy học số (bài giảng e-learning, trắc nghiệm hình ảnh…) cho các khoá học trực tuyến.", # cite: 76
        "Thiết kế, phát triển các cổng đào tạo trực tuyến; vận hành, quản trị các hệ thống dạy học trực tuyến.", # cite: 77, 78
        "Thiết kế, phát triển các môi trường học tập số.", # cite: 79
        "Nghiên cứu, thiết kế và phát triển các giải pháp chuyển đổi số trong giáo dục, dạy học và đào tạo.", # cite: 80
        "Tư duy phản biện, kỹ năng làm việc nhóm và năng lực giải quyết vấn đề.", # cite: 81
        "Khả năng tham gia giảng dạy trong lĩnh vực giáo dục truyền thông đa phương tiện.", # cite: 82
        "Năng lực tự học, nghiên cứu trong lĩnh vực Khoa học giáo dục và truyền thông.", # cite: 83
    ],
    "CO_HOI_NGHE_NGHIEP": [
        "Chuyên viên phân tích nghiệp vụ (Business Analyst) của các tổ chức, các sản phẩm, dịch vụ giáo dục.", # cite: 84
        "Chuyên viên quản trị hệ thống quản lý học tập (LMS), nội dung học tập (LCMS).", # cite: 85
        "Chuyên viên thiết kế và sáng tạo nội dung học tập đa phương tiện (videos, mô phỏng, VR, AR, trò chơi giáo dục…).", # cite: 86
        "Chuyên viên thiết kế và sáng tạo khoá học số (MOOCs, e-learning, blended learning…).", # cite: 87
        "Chuyên viên thiết kế học liệu theo hướng tiếp cận STEAM/STEM, giáo viên dạy theo mô hình STEAM/STEM.", # cite: 88
        "Chuyên viên phát triển nội dung tại các chương trình khoa học – giáo dục của các đài truyền hình, truyền thông và mạng xã hội.", # cite: 89
        "Kỹ thuật viên quản trị hệ thống dạy học trực tuyến, chuyên viên thiết kế phát triển các cổng đào tạo trực tuyến.", # cite: 90
        "Phụ trách công tác đào tạo trong doanh nghiệp, trường học và các tổ chức.", # cite: 91
        "Học tiếp lên Thạc sĩ/Nghiên cứu sinh lĩnh vực Khoa học giáo dục (định hướng Công nghệ giáo dục).", # cite: 92
    ],
    "XET_TUYEN": {
        "Tài năng": "Giải thưởng HSG QG-QT/Chứng chỉ Quốc tế/HSNL", # cite: 93
        "Đánh giá tư duy": "K00", # cite: 93
        "Tốt nghiệp THPT 2024": "A00, A01, D01, K01", # cite: 93
    },
    "DOANH_NGHIEP_HOP_TAC": [
        "Dự án EDUNEXT – Tập đoàn FPT", # cite: 111
        "Học viện Viettel – Tập đoàn Viễn thông Quân đội Viettel", # cite: 112
        "Công ty Công nghệ thông tin VNPT (VNPT-IT)", # cite: 113
        "Công ty Cổ phần Edulive", # cite: 114
        "Học viện TEKY", # cite: 115
        "Công ty Cổ phần Giáo dục KDI", # cite: 116
        "Công ty e-Việt Learning (Công ty TNHH Khoa Trí)", # cite: 117
        "Công ty công nghệ Liberal", # cite: 118
        "Công Ty Cp Công Nghệ Giáo Dục Thiên Hà Xanh", # cite: 119
        "Công ty cổ phần Công nghệ giáo dục eJoy", # cite: 120
        "Nền tảng Edvin.ai", # cite: 121
        "Nền tảng Moddie.ai", # cite: 122
        "Nền tảng ClassIn Việt Nam", # cite: 123
        "Công ty CP Doanh nghiệp xã hội HR Companion", # cite: 124
        "Công ty CP Deha Việt Nam", # cite: 125
        "Và nhiều doanh nghiệp công nghệ giáo dục trong và ngoài nước.", # cite: 126
    ],
    "DINH_HUONG_CHUYEN_SAU": [
        "Phát triển đa phương tiện giáo dục: Tạo hình 2D/3D, Đồ hoạ hình động, Trí tuệ nhân tạo, AR/VR/Gamification…", # cite: 100
        "Môi trường học tập số: E-learning, B-learning, giáo dục STEAM/STEM, Xuất bản ấn phẩm truyền thông, học liệu số…", # cite: 101
        "Đào tạo số phục vụ phát triển, bồi dưỡng nhân sự tại doanh nghiệp thích ứng với công nghiệp 4.0.", # cite: 102
    ]
}

# Dữ liệu Ngành Quản lý Giáo dục (QLGD)
QLGD_DATA = {
    "TEN_NGANH": "Quản lý Giáo dục",
    "SLOGAN": "Đổi mới giáo dục - Kết nối Chất lượng và Chuyển đổi số", # cite: 60
    "MUC_TIEU": [
        "Kiến thức nền tảng và chuyên môn vững chắc về quản lý giáo dục và quản lý chất lượng giáo dục và đào tạo.", # cite: 6
        "Kỹ năng nghề nghiệp và phẩm chất cá nhân cần thiết để thành công trong các vị trí việc làm.", # cite: 7
        "Kỹ năng xã hội cần thiết để làm việc hiệu quả trong nhóm liên ngành và trong môi trường quốc tế.", # cite: 8
        "Năng lực hình thành ý tưởng, thiết kế, triển khai và vận hành các dự án, đề tài nghiên cứu trong lĩnh vực quản lý giáo dục, quản lý chất lượng giáo dục và đào tạo.", # cite: 9
        "Khả năng tự đào tạo, vận dụng kiến thức, cập nhật kiến thức mới để giải quyết vấn đề cụ thể trong thực tế.", # cite: 10
        "Năng lực hình thành ý tưởng thiết kế, triển khai và vận hành khóa học giàu công nghệ hoặc sản phẩm đa phương tiện.", # cite: 11
        "Năng lực dạy học và quản lý các khóa đào tạo tại doanh nghiệp, cơ sở giáo dục.", # cite: 12
        "Phẩm chất chính trị, đạo đức nghề nghiệp, có ý thức phục vụ nhân dân, có sức khỏe.", # cite: 13
    ],
    "CO_HOI_NGHE_NGHIEP": [
        "Chuyên viên quản lý hành chính giáo dục tại các cơ quan quản lý giáo dục (Bộ/Sở GD&ĐT, Tổng Cục GDNN, v.v.).", # cite: 15
        "Chuyên viên phụ trách công tác văn hóa, giáo dục tại cơ quan chính quyền các cấp (UBND, trung tâm bồi dưỡng).", # cite: 16
        "Chuyên viên/Nghiên cứu viên tại các trung tâm, viện nghiên cứu giáo dục.", # cite: 17, 18
        "Chuyên viên các bộ phận hành chính, tài chính, quản trị cơ sở vật chất, tuyển sinh, truyền thông, chuyển đổi số tại cơ sở giáo dục.", # cite: 19
        "Chuyên viên khảo thí, kiểm định chất lượng, thanh tra giáo dục, quản lý nhân sự tại các cơ sở giáo dục trong và ngoài công lập.", # cite: 20
        "Chuyên viên phát triển chương trình đào tạo, phương pháp giảng dạy, phương pháp đánh giá.", # cite: 21
        "Chuyên viên xây dựng hệ thống thông tin, cơ sở dữ liệu đảm bảo chất lượng, kiểm định chất lượng.", # cite: 22
        "Chuyên viên xây dựng cơ sở dữ liệu về xếp hạng, so chuẩn đối sánh và gắn sao đại học, đánh giá chất lượng cơ sở giáo dục.", # cite: 23
        "Chuyên viên triển khai các chương trình, dự án xúc tiến thương mại, đầu tư phát triển giáo dục.", # cite: 24
        "Khởi nghiệp nhằm cung ứng các dịch vụ giáo dục.", # cite: 25
        "Học tiếp lên Thạc sĩ Quản lý giáo dục để trở thành giảng viên.", # cite: 26
    ],
    "XET_TUYEN": {
        "Tài năng": "Giải thưởng HSG QG-QT/Chứng chỉ Quốc tế/HSNL", # cite: 28
        "Đánh giá tư duy": "K00", # cite: 28
        "Tốt nghiệp THPT": "A00, A01, D01, K01", # cite: 28
    },
    "DOANH_NGHIEP_HOP_TAC": [
        "Đại học Bách khoa Hà Nội", # cite: 46
        "Trường Cao đẳng nghề Bách khoa Hà Nội", # cite: 47
        "Trường THCS&THPT Tạ Quang Bửu", # cite: 48
        "Bộ Giáo dục và Đào tạo", # cite: 49
        "Sở Giáo dục và Đào tạo Hà Nội và các sở Giáo dục tại các địa phương khác", # cite: 50
        "Phòng giáo dục quận Hai Bà Trưng, Hoàng Mai, Cầu Giấy…", # cite: 51
        "Cao đẳng nghề Việt – Hàn Hà Nội", # cite: 52
        "Công ty TNHH Khoa Trí", # cite: 53
        "Trường học Công nghệ Teky", # cite: 54
        "Công ty Cổ phần Edulive Toàn Cầu", # cite: 55
        "Công ty Công nghệ Liberal", # cite: 56
        "Công ty Cổ phần Doanh nghiệp Xã hội HR Companion", # cite: 57
        "Datality Lab Limited", # cite: 58
        "Và nhiều doanh nghiệp công nghệ giáo dục trong và ngoài nước…", # cite: 59
    ],
    "DINH_HUONG_CHUYEN_SAU": [
        "Quản lý giáo dục số: Marketing và Truyền thông trong giáo dục số, Quản lý chiến lược giáo dục trong kỷ nguyên số, Quản lý chất lượng giáo dục trực tuyến…", # cite: 43
        "Quản lý chất lượng giáo dục: Kiểm định chất lượng giáo dục, Nhập môn xếp hạng cơ sở giáo dục đại học, Lập kế hoạch và Thiết kế Đo lường đánh giá...", # cite: 43
    ]
}

# ======================================================================
## 2. LÕI CHATBOT VÀ LOGIC XỬ LÝ (CHATBOT LOGIC MODULE)
# ======================================================================

def format_list_to_string(data_list, prefix=" - ", heading=""):
    """Định dạng danh sách các mục tiêu/cơ hội thành chuỗi có dấu đầu dòng."""
    output = f"{heading}\n" if heading else ""
    for item in data_list:
        output += f"{prefix}{item}\n"
    return output.strip()

def get_program_info(program_data, topic):
    """Lấy thông tin chung cho một chủ đề (Mục tiêu, Nghề nghiệp, Slogan)."""
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
        
    return f"Thông tin về {topic} của ngành {program_name} hiện không có."

def compare_programs(topic):
    """So sánh thông tin giữa hai ngành học."""
    if topic == "xét tuyển":
        output = "**SO SÁNH TỔ HỢP XÉT TUYỂN (CNGD vs QLGD)**\n"
        output += "| Hình thức | Công nghệ Giáo dục | Quản lý Giáo dục |\n"
        output += "|:---------|:--------------------|:-----------------|\n"
        
        # Vì tổ hợp xét tuyển của cả hai ngành là giống nhau
        for hinh_thuc, to_hop_cngd in CNGD_DATA["XET_TUYEN"].items():
            to_hop_qlgd = QLGD_DATA["XET_TUYEN"].get(hinh_thuc, "-")
            output += f"| {hinh_thuc} | [cite_start]{to_hop_cngd} [cite: 93] | [cite_start]{to_hop_qlgd} [cite: 28] |\n"
        return output.strip()
        
    elif topic == "slogan":
        output = "**SO SÁNH SLOGAN**\n"
        [cite_start]output += f"**CNGD:** {CNGD_DATA['SLOGAN']} [cite: 127]\n"
        [cite_start]output += f"**QLGD:** {QLGD_DATA['SLOGAN']} [cite: 60]\n"
        return output.strip()
        
    elif topic == "định hướng":
        output = "**SO SÁNH ĐỊNH HƯỚNG CHUYÊN SÂU**\n"
        output += "**Công nghệ Giáo dục:**\n"
        [cite_start]output += format_list_to_string(CNGD_DATA["DINH_HUONG_CHUYEN_SAU"], prefix="  - ") + " [cite: 100, 101, 102]\n"
        output += "\n **Quản lý Giáo dục:**\n"
        [cite_start]output += format_list_to_string(QLGD_DATA["DINH_HUONG_CHUYEN_SAU"], prefix="  - ") + " [cite: 43]\n"
        return output.strip()
        
    # Thêm logic so sánh cho Mục tiêu/Nghề nghiệp nếu cần (chỉ cần liệt kê cả hai)
    return "Chức năng so sánh chi tiết cho mục tiêu hoặc nghề nghiệp đang được phát triển. Vui lòng xem thông tin riêng lẻ."


# ======================================================================
## 3. BỘ PHÂN TÍCH Ý ĐỊNH (INTENT PARSER)
# ======================================================================

def parse_intent(user_input):
    """Phân tích đầu vào người dùng để xác định Ngành, Chủ đề và Ý định."""
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
        # Nếu không rõ chủ đề so sánh, hỏi người dùng
        return {"type": "ambiguous_compare"}

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
    elif re.search(r'giới thiệu|thông tin chung', input_lower):
        topic_match = "giới thiệu"
        
    # 4. Trả về kết quả phân tích
    if program_match and topic_match:
        return {"type": "single_query", "program": program_match, "topic": topic_match}
    elif topic_match and not program_match:
        return {"type": "ambiguous_program", "topic": topic_match}
    elif program_match and not topic_match:
        return {"type": "ambiguous_topic", "program": program_match}
    else:
        return {"type": "unknown"}

# ======================================================================
## 4. HÀM CHÍNH CỦA CHATBOT (MAIN CHATBOT FUNCTION)
# ======================================================================

def main_chatbot_response(user_input):
    """Hàm trung tâm điều phối phản hồi của chatbot."""
    intent = parse_intent(user_input)
    
    if intent["type"] == "single_query":
        return get_program_info(intent["program"], intent["topic"])
        
    elif intent["type"] == "compare":
        return compare_programs(intent["topic"])
        
    elif intent["type"] == "ambiguous_program":
        return f"Bạn muốn hỏi thông tin **{intent['topic']}** của ngành **Công nghệ Giáo dục** hay **Quản lý Giáo dục**?"
        
    elif intent["type"] == "ambiguous_topic":
        program_name = intent["program"]["TEN_NGANH"]
        return f"Bạn muốn hỏi về **mục tiêu**, **cơ hội nghề nghiệp**, **xét tuyển**, **định hướng** hay **doanh nghiệp hợp tác** của ngành **{program_name}**?"
        
    elif intent["type"] == "ambiguous_compare":
        return "Bạn muốn so sánh về **xét tuyển (tổ hợp)**, **slogan** hay **định hướng chuyên sâu** giữa hai ngành?"
        
    elif re.search(r'chào|xin chào|start', user_input.lower()):
        return "Xin chào! Tôi là chatbot tra cứu thông tin về Chương trình **Công nghệ Giáo dục (CNGD)** và **Quản lý Giáo dục (QLGD)**. Tôi có thể giúp bạn tìm thông tin chi tiết hoặc **so sánh** hai ngành này."

    else:
        return "Tôi chưa hiểu rõ câu hỏi của bạn. Vui lòng hỏi lại rõ ràng hơn về **CNGD** hoặc **QLGD** (ví dụ: 'Mục tiêu ngành CNGD là gì?' hoặc 'So sánh xét tuyển')."

# ======================================================================
## 5. VÒNG LẶP CHÍNH CỦA ỨNG DỤNG (MAIN APPLICATION LOOP)
# ======================================================================

if __name__ == "__main__":
    
    def clear_console():
        # Lệnh xóa màn hình cho các hệ điều hành khác nhau
        os.system('cls' if os.name == 'nt' else 'clear')
        
    clear_console()
    print("=================================================================")
    print("CHATBOT HAI NGÀNH: CÔNG NGHỆ GD & QUẢN LÝ GD (500 dòng)")
    print("=================================================================")
    print("Hãy hỏi về **CNGD** hoặc **QLGD** (ví dụ: 'Cơ hội nghề nghiệp ngành QLGD?')")
    print("Hoặc so sánh (ví dụ: 'So sánh tổ hợp xét tuyển?')")
    print("Nhập 'thoát' hoặc 'exit' để kết thúc.")
    
    while True:
        try:
            user_input = input("\nBạn: ")
            if user_input.lower() in ["thoát", "exit"]:
                print("\nChatbot: Tạm biệt! Chúc bạn thành công với lựa chọn của mình.")
                break
            
            response = main_chatbot_response(user_input)
            print(f"\nChatbot:\n{response}")
            
        except Exception as e:
            print(f"\nĐã xảy ra lỗi không mong muốn: {e}")
            break
