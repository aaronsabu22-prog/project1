// =============================
// DOM Elements
// =============================

const uploadBtn = document.getElementById("uploadBtn");
const summaryBtn = document.getElementById("summaryBtn");
const askBtn = document.getElementById("askBtn");
const searchBtn = document.getElementById("searchBtn");
const clearBtn = document.getElementById("clearBtn");

const pdfFile = document.getElementById("pdfFile");
const question = document.getElementById("question");
const searchQuery = document.getElementById("searchQuery");

const summary = document.getElementById("summary");
const answer = document.getElementById("answer");
const searchResults = document.getElementById("searchResults");

// =============================
// Upload PDF
// =============================

uploadBtn.addEventListener("click", async () => {

    if (pdfFile.files.length === 0) {
        alert("Please choose a PDF file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", pdfFile.files[0]);

    summary.innerHTML = "Uploading PDF and creating embeddings...";

    try {

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        summary.innerHTML = data.message;

    } catch (err) {

        summary.innerHTML = "Upload failed.";

    }

});

// =============================
// Generate Summary
// =============================

summaryBtn.addEventListener("click", async () => {

    summary.innerHTML = "Generating summary...";

    try {

        const response = await fetch("/summary", {

            method: "POST"

        });

        const data = await response.json();

        if (data.status === "success") {

            summary.innerHTML = data.summary;

        } else {

            summary.innerHTML = data.message;

        }

    }

    catch {

        summary.innerHTML = "Unable to generate summary.";

    }

});

// =============================
// Ask Question
// =============================

askBtn.addEventListener("click", async () => {

    const userQuestion = question.value.trim();

    if (userQuestion === "") {

        alert("Please enter a question.");

        return;

    }

    answer.innerHTML = "Thinking...";

    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                question: userQuestion

            })

        });

        const data = await response.json();

        if (data.status === "success") {

            answer.innerHTML = data.answer;

        } else {

            answer.innerHTML = data.message;

        }

    }

    catch {

        answer.innerHTML = "Unable to answer.";

    }

});

// =============================
// Semantic Search
// =============================

searchBtn.addEventListener("click", async () => {

    const query = searchQuery.value.trim();

    if (query === "") {

        alert("Enter something to search.");

        return;

    }

    searchResults.innerHTML = "Searching...";

    try {

        const response = await fetch("/search", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                query: query

            })

        });

        const data = await response.json();

        if (data.status !== "success") {

            searchResults.innerHTML = data.message;

            return;

        }

        let html = "";

        data.results.forEach((item, index) => {

            html += `
                <div style="margin-bottom:20px">
                    <b>Result ${index + 1}</b><br><br>
                    ${item.content}
                    <hr>
                </div>
            `;

        });

        searchResults.innerHTML = html;

    }

    catch {

        searchResults.innerHTML = "Search failed.";

    }

});

// =============================
// Clear Database
// =============================

clearBtn.addEventListener("click", async () => {

    if (!confirm("Remove the uploaded research paper?")) {

        return;

    }

    try {

        const response = await fetch("/clear", {

            method: "DELETE"

        });

        const data = await response.json();

        summary.innerHTML = "";
        answer.innerHTML = "";
        searchResults.innerHTML = "";

        question.value = "";
        searchQuery.value = "";
        pdfFile.value = "";

        alert(data.message);

    }

    catch {

        alert("Unable to clear project.");

    }

});