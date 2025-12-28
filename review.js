document.getElementById("surveyForm").addEventListener("submit", e => {
  e.preventDefault();

  const score = { V:0, A:0, R:0, K:0 };

  document.querySelectorAll("input:checked").forEach(i => {
    score[i.value]++;
  });

  const email = document.getElementById("email").value;

  // VẼ BIỂU ĐỒ
  document.getElementById("result").style.display = "block";
  new Chart(document.getElementById("radarChart"), {
    type: "radar",
    data: {
      labels: ["Visual", "Aural", "Read/Write", "Kinesthetic"],
      datasets: [{
        data: [score.V, score.A, score.R, score.K],
        backgroundColor: "rgba(22,62,156,0.2)",
        borderColor: "#163e9c"
      }]
    },
    options: { scales: { r: { beginAtZero: true } } }
  });

  //  n8n
  fetch("https://oanhnguyen.app.n8n.cloud/webhook-test/vark-survey", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: email,
      V: score.V,
      A: score.A,
      R: score.R,
      K: score.K
    })
  })
  .then(() => alert("Đã gửi kết quả về email!"))
  .catch(() => alert("Lỗi gửi email"));
});
