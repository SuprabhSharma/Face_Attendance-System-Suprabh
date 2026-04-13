let videoStream = null;

async function startCamera(videoElementId) {
    const video = document.getElementById(videoElementId);
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = videoStream;
    } catch (err) {
        showStatus('error', 'Could not access the camera. Please allow permissions.');
        console.error("Camera error:", err);
    }
}

function captureBase64(videoElementId, canvasElementId) {
    const video = document.getElementById(videoElementId);
    const canvas = document.getElementById(canvasElementId);
    const context = canvas.getContext('2d');
    
    // Setup canvas size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current frame
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Get base64 (jpeg is smaller)
    return canvas.toDataURL('image/jpeg', 0.8);
}

function showStatus(type, message) {
    const statusEl = document.getElementById('statusMessage');
    if (!statusEl) return;
    
    statusEl.className = 'status ' + type;
    statusEl.textContent = message;
    statusEl.style.display = 'block';
}

function hideStatus() {
    const statusEl = document.getElementById('statusMessage');
    if (statusEl) {
        statusEl.style.display = 'none';
        statusEl.className = 'status';
    }
}
