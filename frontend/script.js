const backendURL = "https://boxfed-backend.onrender.com";

async function sendChat() {
    const input = document.getElementById("chatbot-input");
    const msg = input.value.trim();
    const box = document.getElementById("chatbot-messages");

    if (!msg) return;

    // hiển thị user message
    box.innerHTML += `<div class="msg user">${msg}</div>`;
    input.value = "";

    // lấy file đang chọn trong select (nếu có)
    const fileSelect = document.getElementById("fileSelect");
    const selectedFile = fileSelect ? fileSelect.value : "";

    const payload = {
        message: msg,
        file: selectedFile
    };

    try {
        const res = await fetch(backendURL + "/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        box.innerHTML += `<div class="msg bot">${data.reply}</div>`;
        box.scrollTop = box.scrollHeight;
    } catch (err) {
        box.innerHTML += `<div class="msg bot">⚠ Lỗi kết nối backend</div>`;
    }
}
