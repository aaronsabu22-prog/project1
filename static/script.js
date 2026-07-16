async function uploadPaper() {

    const fileInput = document.getElementById("paper");

    if (fileInput.files.length === 0) {
        alert("Please select a PDF file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    document.getElementById("uploadMessage").innerHTML =
        data.message;
}


async function generateSummary() {

    const response = await fetch("/summary");

    const data = await response.json();

    document.getElementById("summary").innerHTML =
        data.summary;
}


async function askQuestion() {

    const question =
        document.getElementById("question").value;

    if (question === "") {
        alert("Enter a question.");
        return;
    }

    const formData = new FormData();

    formData.append("question", question);

    const response = await fetch("/ask", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    document.getElementById("answer").innerHTML =
        data.answer;
}


async function semanticSearch() {

    const query =
        document.getElementById("searchQuery").value;

    if (query === "") {
        alert("Enter a search query.");
        return;
    }

    const formData = new FormData();

    formData.append("query", query);

    const response = await fetch("/search", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    let output = "";

    data.results.forEach((item, index) => {
        output += `<p><b>Result ${index + 1}</b></p>`;
        output += `<p>${item}</p><hr>`;
    });

    document.getElementById("results").innerHTML =
        output;
}


async function clearPaper() {

    const response = await fetch("/clear");

    const data = await response.json();

    document.getElementById("uploadMessage").innerHTML =
        data.message;

    document.getElementById("summary").innerHTML =
        "";

    document.getElementById("answer").innerHTML =
        "";

    document.getElementById("results").innerHTML =
        "";

    document.getElementById("question").value = "";

    document.getElementById("searchQuery").value = "";

    document.getElementById("paper").value = "";
}