document.getElementById("surveyForm").addEventListener("submit", e => {
  e.preventDefault();

  const score = { V:0, A:0, R:0, K:0 };

  document.querySelectorAll("input:checked").forEach(i => {
    score[i.value]++;
  });

  document.getElementById("result").style.display = "block";

  new Chart(document.getElementById("radarChart"), {
    type: "radar",
    data: {
      labels: ["Visual", "Aural", "Read/Write", "Kinesthetic"],
      datasets: [{
        data: [score.V, score.A, score.R, score.K],
        backgroundColor: "rgba(22,62,156,0.2)",
        borderColor: "#163e9c",
        borderWidth: 2
      }]
    },
    options: {
      scales: { r: { beginAtZero: true } }
    }
  });
});
