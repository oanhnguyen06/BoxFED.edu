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