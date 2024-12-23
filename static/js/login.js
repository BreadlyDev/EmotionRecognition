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
    video.play();
    detectionInterval = setInterval(captureAndDetectFace, 3000);
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
  if (detectionInterval) {
    clearInterval(detectionInterval); 
  }
});

cv.onRuntimeInitialized = () => {
  console.log('OpenCV.js загружен');
  const haarFilePath = '/static/ai/haarcascade_frontalface_default.xml';

  fetch(haarFilePath)
      .then(response => {
          if (!response.ok) {
              throw new Error(`Ошибка загрузки файла каскада Haar: ${response.statusText}`);
          }
          return response.arrayBuffer();
      })
      .then(data => {
          cv.FS_createDataFile('/', 'haarcascade_frontalface_default.xml', new Uint8Array(data), true, false, false);
          
          classifier = new cv.CascadeClassifier();
          if (!classifier.load('haarcascade_frontalface_default.xml')) {
              throw new Error('Не удалось загрузить классификатор!');
          }
          console.log('Файл каскада Haar успешно загружен.');

          setInterval(captureAndDetectFace, 3000);
      })
      .catch(err => console.error('Ошибка загрузки файла через fetch:', err));
};

const lineWidth = 4;

function captureAndDetectFace() {
  if (!classifier || !detectionInterval) {
    console.error('Классификатор ещё не загружен или поиск лиц уже остановлен.');
    return;
  }

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  let src = cv.imread(canvas);
  let gray = new cv.Mat();
  let faces = new cv.RectVector();

  cv.cvtColor(src, gray, cv.COLOR_BGR2GRAY);
  classifier.detectMultiScale(gray, faces, 1.1, 3, 0, new cv.Size(100, 100), new cv.Size(400, 400));

  if (faces.size() > 0) {
    let face = faces.get(0);
    console.log('Лицо найдено:', face);

    ctx.beginPath();
    ctx.rect(face.x, face.y, face.width, face.height);
    ctx.lineWidth = lineWidth;
    ctx.strokeStyle = 'red';
    ctx.stroke();

    faceDetected = true;

    setTimeout(() => {
      if (faceDetected) {
        sendPhoto(canvas, face); 
        stopFaceDetection(); 
      }
    }, 5000); 
  } else {
    console.log('Лицо не найдено.');
    faceDetected = false;
  }

  src.delete();
  gray.delete();
  faces.delete();
}

async function sendPhoto(canvas, face) {
  const photoCanvas = document.createElement('canvas');
  photoCanvas.width = face.width; 
  photoCanvas.height = face.height; 

  const photoContext = photoCanvas.getContext('2d');
  photoContext.drawImage(canvas, face.x + lineWidth, face.y + lineWidth, face.width - lineWidth, face.height - lineWidth, 0, 0, face.width - lineWidth, face.height - lineWidth);
  const photoData = photoCanvas.toDataURL("image/png");

  cameraModal.classList.remove("active");
  overlay.classList.remove("active");
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }

  try {
    const response = await fetch("/login_by_photo/", {
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
      window.location.href = "/";
    } else {
      alert(result.message || "Login failed!");
    }
    showPhoto(photoData);
  } catch (error) {
    console.error("Error:", error);
    alert("An error occurred while trying to log in.");
  }
}

function showPhoto(photoData) {
  const photoModal = document.getElementById("photoModal");
  const sentPhoto = document.getElementById("sentPhoto");
  const closePhotoModal = document.getElementById("closePhotoModal");

  sentPhoto.src = photoData;
  photoModal.style.display = "block";

  closePhotoModal.onclick = () => {
    photoModal.style.display = "none";
  };

  window.onclick = (event) => {
    if (event.target === photoModal) {
      photoModal.style.display = "none";
    }
  };
}


function stopFaceDetection() {
  if (detectionInterval) {
    clearInterval(detectionInterval);
    detectionInterval = null;
    console.log('Поиск лиц остановлен.');
  }
}

// captureButton.addEventListener("click", async () => {
//   const canvas = document.createElement("canvas");
//   canvas.width = video.videoWidth;
//   canvas.height = video.videoHeight;

//   const context = canvas.getContext("2d");
//   context.drawImage(video, 0, 0, canvas.width, canvas.height);

//   const photoData = canvas.toDataURL("image/png");

//   cameraModal.classList.remove("active");
//   overlay.classList.remove("active");
//   if (stream) {
//     stream.getTracks().forEach((track) => track.stop());
//   }

//   try {
//     const response = await fetch("/login_by_photo/", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/x-www-form-urlencoded",
//       },
//       body: new URLSearchParams({
//         photo: photoData,
//       }),
//     });

//     const result = await response.json();
//     if (result.success) {
//       alert("Login successful!");
//       window.location.href = "/";
//     } else {
//       alert(result.message || "Login failed!");
//     }
//   } catch (error) {
//     console.error("Error:", error);
//     alert("An error occurred while trying to log in.");
//   }
// });
