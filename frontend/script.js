const backendURL = "http://localhost:3000";

// tải danh sách file từ backend
async function loadFiles() {
    try {
        const res = await fetch(backendURL + "/files");
        const data = await res.json();
        const select = document.getElementById("fileSelect");

        select.innerHTML = `<option value="">-- Chọn file dữ liệu --</option>`;

        data.files.forEach(f => {
            const opt = document.createElement("option");
            opt.value = f;
            opt.textContent = f;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error("Lỗi loadFiles:", err);
    }
}

loadFiles();

async function sendMessage() {
    let msg = document.getElementById("msgInput").value.trim();
    let file = document.getElementById("fileSelect").value;
    let box = document.getElementById("chatBox");

    if (!msg) return;
    if (!file) {
        alert("Hãy chọn file dữ liệu trước!");
        return;
    }

    box.innerHTML += `<div class="msg"><span class="user">Bạn:</span> ${msg}</div>`;
    document.getElementById("msgInput").value = "";

    try {
        const res = await fetch(backendURL + "/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: msg,
                file: file
            })
        });

        const data = await res.json();

        if (data.error) {
            box.innerHTML += `<div class="msg error">⚠️ Lỗi: ${data.error}</div>`;
        } else {
            box.innerHTML += `<div class="msg"><span class="bot">Bot:</span> ${data.reply}</div>`;
        }

    } catch (err) {
        box.innerHTML += `<div class="msg error">⚠️ Không gửi được: ${err}</div>`;
    }

    box.scrollTop = box.scrollHeight;
}
