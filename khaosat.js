const form = document.getElementById("surveyForm");
const resultSection = document.getElementById("result");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    email: email.value,
    visual: +visual.value,
    aural: +aural.value,
    readwrite: +readwrite.value,
    kinesthetic: +kinesthetic.value
  };

  // 1️⃣ VẼ RADAR
  drawRadar(data);

  // 2️⃣ GỢI Ý GIẢNG VIÊN
  suggestLecturers(data);

  // 3️⃣ GỬI DỮ LIỆU SANG N8N
  fetch("https://oanhnguyen.app.n8n.cloud/webhook/vark-survey", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });

  resultSection.classList.remove("hidden");
});

function drawRadar(d) {
  new Chart(document.getElementById("radarChart"), {
    type: "radar",
    data: {
      labels: ["Visual", "Aural", "Read/Write", "Kinesthetic"],
      datasets: [{
        label: "Phong cách học tập",
        data: [d.visual, d.aural, d.readwrite, d.kinesthetic],
        fill: true
      }]
    }
  });
}

async function suggestLecturers(d) {
  const res = await fetch("lecturers.json");
  const lecturers = await res.json();

  const dominant = Object.entries(d)
    .slice(1)
    .sort((a,b)=>b[1]-a[1])[0][0];

  const map = {
    visual: "Visual",
    aural: "Aural",
    readwrite: "ReadWrite",
    kinesthetic: "Kinesthetic"
  };

  const box = document.getElementById("lecturers");
  box.innerHTML = "";

  lecturers
    .filter(l => l.style === map[dominant])
    .forEach(l => {
      box.innerHTML += `
        <div class="card">
          <b>${l.name}</b>
          <p>${l.course}</p>
        </div>
      `;
    });
}
