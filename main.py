from fastapi import FastAPI, File, UploadFile, HTTPException
from pymongo import MongoClient
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
#load_dotenv()

app = FastAPI()

'''cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)'''

client = MongoClient(os.getenv("MONGO_URI"))
db = client['famnest']  # Replace with your database name
collection = db['media']

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(file.file, folder="uploaded_images")
        image_data = {"url": result['url'], "public_id": result['public_id']}
        collection.insert_one(image_data)
        return {"message": "Image uploaded successfully", "url": result['url']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images")
def get_images():
    try:
        images = list(collection.find({}, {"_id": 0}))
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{public_id}")
def delete_image(public_id: str):
    try:
        cloudinary.api.delete_resources([public_id])
        collection.delete_one({"public_id": public_id})
        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

