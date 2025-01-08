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
            "title": title,
            "description": description,
            "url": result['url'],
            "public_id": result['public_id'],
            "created_at": result['created_at'],
            "width": result['width'],
            "height": result['height'],
            "format": result['format']
        }
        
        # Store metadata in MongoDB
        insert_result = collection.insert_one(image_data)
        image_data["_id"] = str(insert_result.inserted_id)  # Convert ObjectId to string

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
        # Ensure the public_id doesn't include the folder path
        public_id = public_id.replace("uploaded_images/", "")
        
        # Delete the image from Cloudinary
        cloudinary.api.delete_resources([public_id])
        
        # Remove metadata from MongoDB
        collection.delete_one({"public_id": public_id})

        return {"message": "Image deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
