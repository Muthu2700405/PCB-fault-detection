// script.js (frontend)
const BACKEND_URL = "https://REPLACE_WITH_YOUR_RENDER_URL"; // e.g. https://pcb-backend.onrender.com

const uploadInput = document.getElementById("upload-button");
const imagePreview = document.getElementById("image-preview");
const resultsContainer = document.getElementById("results-container");
const statusText = document.getElementById("status-text");

uploadInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // show preview locally
    imagePreview.src = URL.createObjectURL(file);

    // send to backend
    statusText.innerText = "Processing...";
    resultsContainer.innerHTML = "";

    const fd = new FormData();
    fd.append("file", file);

    try {
        const resp = await fetch(`${BACKEND_URL}/detect`, {
            method: "POST",
            body: fd
        });

        const data = await resp.json();
        if (!resp.ok) {
            statusText.innerText = data.error || "Server error";
            return;
        }

        statusText.innerText = `Detected Errors: ${data.detections}`;

        // annotated image is base64
        const img = document.createElement("img");
        img.src = "data:image/jpeg;base64," + data.image_b64;
        img.style.maxWidth = "350px";
        img.style.display = "block";
        img.style.marginTop = "12px";

        // list detected
        const list = document.createElement("div");
        list.className = "detected-list";
        if (data.detected && data.detected.length) {
            data.detected.forEach(d => {
                const p = document.createElement("p");
                p.innerText = `${d.name} — conf: ${d.confidence}`;
                list.appendChild(p);
            });
        } else {
            const p = document.createElement("p");
            p.innerText = "No defects detected.";
            list.appendChild(p);
        }

        resultsContainer.appendChild(img);
        resultsContainer.appendChild(list);
    } catch (err) {
        console.error(err);
        statusText.innerText = "Request failed";
    }
});
