let allData = [];

async function loadCSV() {
  const response = await fetch("../data/events.csv");
  const text = await response.text();

  const lines = text.trim().split("\n");
  const headers = lines[0].split(",");

  allData = lines.slice(1).map(line => {
    const values = line.split(",");
    let obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = values[i] ? values[i].trim() : "";
    });
    return obj;
  });

  render(allData.slice(0, 100));
}

function render(data) {
  const tbody = document.getElementById("resultBody");
  tbody.innerHTML = "";

  data.forEach(row => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${row["西元前年"] || row["year_label"] || ""}</td>
      <td>${row["紀年標題"] || row["reign_title"] || ""}</td>
      <td>${row["國家"] || row["states"] || ""}</td>
      <td>${row["人物"] || row["people"] || ""}</td>
      <td>${row["事件詞"] || row["keywords"] || ""}</td>
      <td>${row["原文內容"] || row["event_text"] || ""}</td>
    `;

    tbody.appendChild(tr);
  });
}

function searchData() {
  const keyword = document.getElementById("searchBox").value.trim();

  if (!keyword) {
    render(allData.slice(0, 100));
    return;
  }

  const result = allData.filter(row => {
    return Object.values(row).join(" ").includes(keyword);
  });

  render(result);
}

loadCSV();