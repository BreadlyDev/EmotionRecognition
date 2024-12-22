const addPhotoButton = document.getElementById("addPhotoButton");
const cameraModal = document.getElementById("cameraModal");
const closeModal = document.getElementById("closeModal");
const video = document.getElementById("video");
const captureButton = document.getElementById("captureButton");
const photoInput = document.getElementById("photoInput");
const photoNotification = document.getElementById("photoNotification");
const overlay = document.getElementById("overlay");

let stream;

addPhotoButton.addEventListener("click", async () => {
  cameraModal.classList.add("active");
  overlay.classList.add("active");
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
  } catch (error) {
    console.error("Error accessing camera:", error);
    alert("Unable to access camera. Please check permissions.");
  }
});

closeModal.addEventListener("click", () => {
  cameraModal.classList.remove("active");
  overlay.classList.remove("active");
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
});

//captureButton.addEventListener("click", () => {
//  const canvas = document.createElement("canvas");
//  canvas.width = video.videoWidth;
//  canvas.height = video.videoHeight;
//
//  const context = canvas.getContext("2d");
//  context.drawImage(video, 0, 0, canvas.width, canvas.height);
//
//  const photoData = canvas.toDataURL("image/png");
//  photoInput.value = photoData;
//  photoNotification.style.display = "block";
//
//  cameraModal.classList.remove("active");
//  overlay.classList.remove("active");
//  if (stream) {
//    stream.getTracks().forEach((track) => track.stop());
//  }
//});

captureButton.addEventListener("click", async () => {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const photoData = canvas.toDataURL("image/png");

  cameraModal.classList.remove("active");
  overlay.classList.remove("active");
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }

  try {
    const response = await fetch("/login-by-photo/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        photo: photoData,
      }),
    });

    const result = await response.json();
    if (result.success) {
      alert("Login successful!");
      window.location.href = "/home"; // Redirect to home page
    } else {
      alert(result.message || "Login failed!");
    }
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while trying to log in.");
  }
});

