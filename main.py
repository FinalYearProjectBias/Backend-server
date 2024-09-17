from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from firebase_config import db  # Firebase config
from typing import Optional
import hashlib

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change this to specific origins for production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Hash password using SHA-256 (for basic security)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# User model for signup
class SignupUser(BaseModel):
    name: str
    email: str
    password: str

# User model for login
class LoginUser(BaseModel):
    email: str
    password: str

@app.post("/signup/")
async def signup_user(user: SignupUser):
    try:
        # Check if the user already exists
        users_ref = db.collection("users")
        existing_user = users_ref.where("email", "==", user.email).get()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Create a document with auto-generated ID
        doc_ref = db.collection("users").document()
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = hash_password(user_dict["password"])
        doc_ref.set(user_dict)
        return {"message": "User signed up successfully", "user": user_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login/")
async def login_user(user: LoginUser):
    try:
        # Search for the user by email
        users_ref = db.collection("users")
        user_query = users_ref.where("email", "==", user.email).get()

        # Validate user existence
        if not user_query:
            raise HTTPException(status_code=404, detail="User not found")

        # Get the user data from Firestore
        user_data = user_query[0].to_dict()

        # Verify the password
        if hash_password(user.password) != user_data.get("password"):
            raise HTTPException(status_code=400, detail="Invalid password")

        return {"message": "Login successful", "user": {"name": user_data.get("name"), "email": user_data.get("email")}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        doc_ref = db.collection("users").document(user_id)
        user = doc_ref.get()
        if user.exists:
            return user.to_dict()
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}")
async def update_user(user_id: str, user: SignupUser):
    try:
        doc_ref = db.collection("users").document(user_id)
        user_dict = user.dict()
        # Hash the password before updating
        user_dict["password"] = hash_password(user_dict["password"])
        doc_ref.update(user_dict)
        return {"message": "User updated successfully", "user": user_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        doc_ref = db.collection("users").document(user_id)
        doc_ref.delete()
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
