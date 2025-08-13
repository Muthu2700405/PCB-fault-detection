// static/script.js

const uploadInput = document.getElementById("upload-button");
const imagePreview = document.getElementById("image-preview");
const resultsContainer = document.getElementById("results-container");
const statusText = document.getElementById("status-text");

// When a user selects a file
uploadInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Show a preview of the selected image
    imagePreview.src = URL.createObjectURL(file);

    // Send the file to the backend for processing
    await sendFile(file);
});

// Function to handle the API call
async function sendFile(file) {
    statusText.innerText = "Processing...";
    resultsContainer.innerHTML = "";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const resp = await fetch("/detect", {
            method: "POST",
            body: formData
        });

        const data = await resp.json();
        if (!resp.ok) {
            statusText.innerText = data.error || "Processing failed";
            return;
        }

        statusText.innerText = `Detected Errors: ${data.detections}`;

        // Create the annotated result image
        const img = document.createElement("img");
        // This line is updated to handle the Base64 image string
        img.src = "data:image/jpeg;base64," + data.result_image_b64;
        img.alt = "Annotated result";
        img.style.maxWidth = "350px";
        img.style.display = "block";
        img.style.marginTop = "12px";

        // Create the list of detected faults
        const listDiv = document.createElement("div");
        listDiv.className = "detected-list";
        if (data.detected && data.detected.length > 0) {
            data.detected.forEach(d => {
                const p = document.createElement("p");
                // Updated to match the new Python response
                p.innerText = `${d.name} — confidence: ${d.confidence}`;
                listDiv.appendChild(p);
            });
        } else {
            const p = document.createElement("p");
            p.innerText = "No defects detected.";
            listDiv.appendChild(p);
        }

        // Add the new elements to the page
        resultsContainer.appendChild(img);
        resultsContainer.appendChild(listDiv);

    } catch (err) {
        console.error(err);
        statusText.innerText = "Prediction failed. Check the console for details.";
    }
}