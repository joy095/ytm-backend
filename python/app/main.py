from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from nudenet import NudeDetector
import cv2
import os
import shutil
from PIL import Image

app = FastAPI()

# Initialize NudeDetector with the specified model path
model_path = os.path.join(os.path.dirname(__file__), "ai_models/640m.onnx")
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

detector = NudeDetector(model_path=model_path, inference_resolution=640)

# List of adult content labels to check for
adult_content_labels = [
    "BUTTOCKS_EXPOSED", "FEMALE_BREAST_EXPOSED", "FEMALE_GENITALIA_EXPOSED",
    "ANUS_EXPOSED", "MALE_GENITALIA_EXPOSED"
]

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/", response_class=HTMLResponse)
async def main():
    return """
    <html>
        <head><title>Upload File</title></head>
        <body>
            <h2>Upload an image or video to check for adult content:</h2>
            <form action="/detect-content/" enctype="multipart/form-data" method="post">
                <label for="file">Select an image or video:</label>
                <input name="file" type="file" accept="image/*,video/*" required>
                <br><br>
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    """

@app.post("/detect-content/")
async def detect_content(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        # Determine file type and call the appropriate detection function
        if file.content_type.startswith("image/"):
            return await detect_nudity_in_image(file, temp_file_path)
        elif file.content_type in ["video/mp4", "video/x-matroska"]:
            return await detect_nudity_in_video(file, temp_file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload an image or video.")

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def detect_nudity_in_image(file: UploadFile, temp_file_path: str):
    # Save the uploaded image temporarily
    with open(temp_file_path, "wb") as temp_file:
        shutil.copyfileobj(file.file, temp_file)

    # Verify the image file
    try:
        Image.open(temp_file_path).verify()
    except Exception:
        os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

    # Detect nudity in the image
    result = detector.detect(temp_file_path)
    print(f"Image result: {result}")  # Debugging output

    # Check for adult content in the result
    for item in result:
        if item.get("class") in adult_content_labels and item.get("score", 0) > 0.5:
            os.remove(temp_file_path)
            return JSONResponse(
                content={
                    "status": True,
                    "message": "Warning: Adult content detected in the image."
                },
                status_code=200
            )

    os.remove(temp_file_path)
    return JSONResponse(
        content={
            "status": False,
            "message": "No adult content detected in the image."
        },
        status_code=200
    )

async def detect_nudity_in_video(file: UploadFile, temp_file_path: str):
    # Save the uploaded video temporarily
    with open(temp_file_path, "wb") as temp_file:
        shutil.copyfileobj(file.file, temp_file)

    # Open the video using OpenCV
    video = cv2.VideoCapture(temp_file_path)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(video.get(cv2.CAP_PROP_FPS))
    frame_step = max(1, frame_rate // 2)  # Analyze every half second

    print(f"Total frames: {frame_count}, Frame rate: {frame_rate}, Step: {frame_step}")

    for frame_number in range(0, frame_count, frame_step):
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = video.read()
        if not success:
            break

        # Save the current frame as a temporary image
        frame_path = f"frame_{frame_number}.jpg"
        cv2.imwrite(frame_path, frame)

        # Detect nudity in the current frame
        result = detector.detect(frame_path)
        print(f"Frame {frame_number} result: {result}")  # Debugging output

        # Check for adult content in the detection result
        for item in result:
            if item.get("class") in adult_content_labels and item.get("score", 0) > 0.5:
                video.release()
                os.remove(frame_path)
                os.remove(temp_file_path)
                return JSONResponse(
                    content={
                        "status": True,
                        "message": f"Warning: Adult content detected at frame {frame_number}."
                    },
                    status_code=200
                )

        os.remove(frame_path)

    video.release()
    os.remove(temp_file_path)
    return JSONResponse(
        content={
            "status": False,
            "message": "No adult content detected in the video."
        },
        status_code=200
    )
