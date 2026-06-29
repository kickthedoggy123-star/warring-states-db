let allData = [];

/* 讀取 CSV */
async function loadCSV() {
    const response = await fetch("./events.csv");
    const text = await response.text();

    allData = parseCSV(text);

    buildYearList(allData);
    render(allData.slice(0, 200), "事件內容：顯示前 200 筆");
}

/* 簡易 CSV 解析器 */
function parseCSV(text) {
    const lines = text.trim().split(/\r?\n/);
    const headers = splitCSVLine(lines[0]);

    return lines.slice(1).map(line => {
        const values = splitCSVLine(line);
        let obj = {};

        headers.forEach((header, index) => {
            obj[header.trim()] = values[index] ? values[index].trim() : "";
        });

        return obj;
    });
}

/* 處理 CSV 逗號與引號 */
function splitCSVLine(line) {
    const result = [];
    let current = "";
    let insideQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];

        if (char === '"') {
            insideQuotes = !insideQuotes;
        } else if (char === "," && !insideQuotes) {
            result.push(current);
            current = "";
        } else {
            current += char;
        }
    }

    result.push(current);
    return result;
}

/* 建立左側年份索引 */
function buildYearList(data) {
    const yearList = document.getElementById("yearList");
    yearList.innerHTML = "";

    const years = [...new Set(data.map(row => row["西元前年"]))];

    years.forEach(year => {
        if (!year) return;

        const div = document.createElement("div");
        div.className = "year-item";
        div.textContent = year;

        div.onclick = function () {
            filterByYear(year);
        };

        yearList.appendChild(div);
    });
}

/* 渲染表格 */
function highlight(text){

    const keyword=document.getElementById("searchBox").value.trim();

    if(keyword===""){

        return text;

    }

    const regex=new RegExp(keyword,"gi");

    return String(text).replace(regex,function(match){

        return "<mark>"+match+"</mark>";

    });

function formatText(text) {

    if (!text) return "";

    let result = "";
    let open = true;

    for (const ch of String(text)) {

        if (ch === '"') {

            result += open ? "「" : "」";

            open = !open;

        } else {

            result += ch;

        }

    }

    return result;
}
}
function render(data, titleText) {
    const tbody = document.getElementById("resultBody");
    const title = document.getElementById("resultTitle");

    tbody.innerHTML = "";
    title.textContent = titleText || "事件內容";

    data.forEach(row => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${highlight(row["西元前年"]||"")}</td>
            <td>${highlight(row["紀年標題"]||"")}</td>
            <td>${highlight(row["國家"]||"")}</td>
            <td>${highlight(formatText(row["人物"]))}</td>
            <td>${highlight(formatText(row["事件詞"]))}</td>
            <td>${highlight(formatText(row["原文內容"]))}</td>
`;
        tbody.appendChild(tr);
    });
}

/* 搜尋 */
function searchData() {
    const keyword = document.getElementById("searchBox").value.trim();

    if (!keyword) {
        showAll();
        return;
    }

    const result = allData.filter(row => {
        return Object.values(row).join(" ").includes(keyword);
    });

    render(result, `搜尋結果：「${keyword}」共 ${result.length} 筆`);
}

/* 點年份 */
function filterByYear(year) {
    const result = allData.filter(row => row["西元前年"] === year);
    render(result, `${year}：共 ${result.length} 筆事件`);
}

/* 顯示全部 */
function showAll() {
    render(allData.slice(0, 500), "事件內容：顯示前 500 筆");
}
document.addEventListener("DOMContentLoaded", function () {

    const searchBox = document.getElementById("searchBox");

    searchBox.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

            searchData();

        }

    });

});
loadCSV();