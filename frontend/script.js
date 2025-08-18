document.addEventListener('DOMContentLoaded', () => {
    const uploadButton = document.getElementById('upload-button');
    const imagePreview = document.getElementById('image-preview');
    const statusText = document.getElementById('status-text');
    const resultsContainer = document.getElementById('results-container');

    uploadButton.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        // Create a local URL for the selected image and show a preview
        const localImageUrl = URL.createObjectURL(file);
        imagePreview.src = localImageUrl;

        // Clear previous results and update status
        statusText.textContent = 'Uploading and detecting...';
        resultsContainer.innerHTML = '';

        // Prepare data for sending to the backend
        const formData = new FormData();
        formData.append('file', file);

        // Send the image to the backend for processing
        fetch('/detect', {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Update the image with the one with detections from the backend
            imagePreview.src = data.image;
            
            // Display the detection results
            if (data.detections && data.detections.length > 0) {
                statusText.textContent = 'Detection complete!';
                const detectionList = document.createElement('div');
                detectionList.className = 'detected-list';
                
                const title = document.createElement('h4');
                title.textContent = 'Detected Faults:';
                detectionList.appendChild(title);
                
                // Use a Set to count unique detections
                const counts = {};
                data.detections.forEach(item => {
                    counts[item] = (counts[item] || 0) + 1;
                });

                for (const item in counts) {
                    const p = document.createElement('p');
                    p.textContent = `• ${item}: ${counts[item]}`;
                    detectionList.appendChild(p);
                }
                resultsContainer.appendChild(detectionList);
            } else {
                statusText.textContent = 'No faults detected.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            statusText.textContent = `Error: ${error.message}`;
        });
    });
});