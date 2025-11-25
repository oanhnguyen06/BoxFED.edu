const backendURL = "http://localhost:3000";

// tải danh sách file từ backend
async function loadFiles() {
    const res = await fetch(backendURL + "/files");
    const data = await res.json();
    const select = document.getElementById("fileSelect");

    data.files.forEach(f => {
        const opt = document.createElement("option");
        opt.value = f;
        opt.textContent = f;
        select.appendChild(opt);
    });
}

loadFiles();

async function sendMessage() {
    let msg = document.getElementById("msgInput").value.trim();
    let file = document.getElementById("fileSelect").value;
    let box = document.getElementById("chatBox");

    if (!msg) return;

    box.innerHTML += `<div class="msg"><span class="user">Bạn:</span> ${msg}</div>`;
    document.getElementById("msgInput").value = "";

    const payload = {
        message: msg,
        file: file
    };

    const res = await fetch(backendURL + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    box.innerHTML += `<div class="msg"><span class="bot">Bot:</span> ${data.reply}</div>`;
    box.scrollTop = box.scrollHeight;
}
