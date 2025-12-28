let varkChart = null;

document.getElementById("surveyForm").addEventListener("submit", e => {
  e.preventDefault();

  // 1. TÍNH ĐIỂM
  const score = { V:0, A:0, R:0, K:0 };

  const checked = document.querySelectorAll("input[type=checkbox]:checked");
  if (checked.length === 0) {
    alert("Vui lòng chọn ít nhất một đáp án.");
    return;
  }

  checked.forEach(i => {
    if (score[i.value] !== undefined) {
      score[i.value]++;
    }
  });

  // 2. TÌM PHONG CÁCH TRỘI
  let dominant = "V";
  let max = score.V;
  for (const k in score) {
    if (score[k] > max) {
      max = score[k];
      dominant = k;
    }
  }

  const styleName = {
    V: "Thị giác (Visual)",
    A: "Thính giác (Aural)",
    R: "Đọc/Viết (Read/Write)",
    K: "Vận động (Kinesthetic)"
  };

  // 3. HIỂN THỊ KẾT QUẢ
  document.getElementById("result").style.display = "block";

  // 4. VẼ BIỂU ĐỒ (DESTROY CHART CŨ)
  const ctx = document.getElementById("radarChart");

  if (varkChart) {
    varkChart.destroy();
  }

  varkChart = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Visual", "Aural", "Read/Write", "Kinesthetic"],
      datasets: [{
        label: "Điểm VARK",
        data: [score.V, score.A, score.R, score.K],
        backgroundColor: "rgba(22,62,156,0.25)",
        borderColor: "#163e9c",
        borderWidth: 2,
        pointBackgroundColor: "#163e9c"
      }]
    },
    options: {
      responsive: true,
      scales: {
        r: {
          beginAtZero: true,
          ticks: { stepSize: 1 }
        }
      }
    }
  });

  // 5. HIỂN THỊ PHONG CÁCH TRỘI
  let resultText = document.getElementById("dominantStyle");
  if (!resultText) {
    resultText = document.createElement("p");
    resultText.id = "dominantStyle";
    resultText.style.marginTop = "15px";
    resultText.style.fontWeight = "bold";
    document.getElementById("result").appendChild(resultText);
  }

  resultText.innerText = "Phong cách học tập trội: " + styleName[dominant];

  // 6. GỬI SANG n8n (EMAIL / LOG / DATABASE)
  fetch("https://oanhnguyen.app.n8n.cloud/webhook-test/vark-survey", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      dominant: dominant,
      scores: score,
      timestamp: new Date().toISOString()
    })
  })
  .then(() => alert("Đã gửi kết quả thành công!"))
  .catch(() => alert("Lỗi gửi dữ liệu"));
});
