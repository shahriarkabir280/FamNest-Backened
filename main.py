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
async def upload_image(file: UploadFile = File(...), title: str = None, description: str = None):
    try:
        # Upload the image to Cloudinary
        result = cloudinary.uploader.upload(file.file, folder="uploaded_images")
        
        # Extract metadata
        image_data = {
            "title": title,  # Optional title for the image
            "description": description,  # Optional description
            "url": result['url'],  # Image URL from Cloudinary
            "public_id": result['public_id'],  # Cloudinary public ID
            "created_at": result['created_at'],  # Timestamp of upload
            "width": result['width'],  # Image width
            "height": result['height'],  # Image height
            "format": result['format']  # Image format (e.g., jpg, png)
        }
        
        # Store metadata in MongoDB
        collection.insert_one(image_data)

        return {"message": "Image uploaded successfully", "image_data": image_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images")
def get_images():
    try:
        # Fetch all image metadata from MongoDB
        images = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB `_id` field
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{public_id}")
def delete_image(public_id: str):
    try:
        # Delete the image from Cloudinary
        cloudinary.api.delete_resources([public_id])
        
        # Remove metadata from MongoDB
        collection.delete_one({"public_id": public_id})

        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
