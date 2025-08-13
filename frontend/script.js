const backendURL = "https://your-render-backend.onrender.com"; // change after deployment

const uploadInput = document.getElementById("upload-button");
const imagePreview = document.getElementById("image-preview");
const resultsContainer = document.getElementById("results-container");
const statusText = document.getElementById("status-text");

uploadInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    imagePreview.src = URL.createObjectURL(file);
    await sendFile(file);
});

async function sendFile(file) {
    statusText.innerText = "Processing...";
    resultsContainer.innerHTML = "";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const resp = await fetch(`${backendURL}/detect`, {
            method: "POST",
            body: formData
        });

        const data = await resp.json();
        if (!resp.ok) {
            statusText.innerText = data.error || "Processing failed";
            return;
        }

        statusText.innerText = `Detected Errors: ${data.detections}`;

        const img = document.createElement("img");
        img.src = "data:image/jpeg;base64," + data.result_image_b64;
        img.alt = "Annotated result";
        img.style.maxWidth = "350px";
        img.style.display = "block";
        img.style.marginTop = "12px";

        const listDiv = document.createElement("div");
        listDiv.className = "detected-list";
        if (data.detected && data.detected.length > 0) {
            data.detected.forEach(d => {
                const p = document.createElement("p");
                p.innerText = `${d.name} — confidence: ${d.confidence}`;
                listDiv.appendChild(p);
            });
        } else {
            const p = document.createElement("p");
            p.innerText = "No defects detected.";
            listDiv.appendChild(p);
        }

        resultsContainer.appendChild(img);
        resultsContainer.appendChild(listDiv);

    } catch (err) {
        console.error(err);
        statusText.innerText = "Prediction failed. Check console.";
    }
}
