from dataclasses import Field

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyexpat.errors import messages

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
    userType:str

# User model for login
class LoginUser(BaseModel):
    email: str
    password: str
    userType:str
class GrievanceModel(BaseModel):
    message:str
    user_ref:str
    responded:bool=False




@app.post("/api/v1/user/signup/")
async def signup_user(user: SignupUser):
    try:
        # Check if the user already exists
        user_type=user.userType
        users_ref = db.collection(user_type)
        existing_user = users_ref.where("email", "==", user.email).get()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")


        # Create a document with auto-generated ID
        doc_ref = db.collection(user_type).document()
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = hash_password(user_dict["password"])
        doc_ref.set(user_dict)
        return {"message": "User signed up successfully", "user": user_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/user/login/")
async def login_user(user: LoginUser):
    try:
        user_type = user.userType

        # Use 'where' with keyword arguments to remove the warning
        users_ref = db.collection(user_type)
        user_query = users_ref.where(field_path="email", op_string="==", value=user.email).get()

        # Validate user existence
        if not user_query:
            raise HTTPException(status_code=404, detail="User not found")

        # Get the user document and extract the UID
        user_doc = user_query[0]
        user_data = user_doc.to_dict()
        user_uid = {"user_id":user_doc.id}
        user_data.update(user_uid)
        print(f"User Data: {user_data}")
        # Verify the password
        if hash_password(user.password) != user_data.get("password"):
            raise HTTPException(status_code=400, detail="Invalid password")
        return {
            "message": "Login successful",
            "user_data": user_data
        }
    except Exception as e:
        print(f"error:{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/")
async def get_user(user_id: str):
    try:
        doc_ref = db.collection("Teacher").document(user_id)
        user = doc_ref.get()
        if user.exists:
            return user.to_dict()
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/admin/get_grievance/")
async def get_grievance():
    try:
        doc_ref=db.collection("Grievance")
        docs=doc_ref.stream()
        all_data=[]
        for doc in docs:
            doc_data=doc.to_dict()
            doc_data["ack_number"]=doc.id
            all_data.append(doc_data)
        return{"message":"Grievance","data":all_data}
    except Exception as e:
        raise  HTTPException(status_code=500,detail=str(e))



@app.post("/api/v1/user/add_grievance/")
async def add_grievance(grievance:GrievanceModel):
    try:
        doc_ref=db.collection("Grievance").document()
        print(doc_ref)
        grievance_dict=grievance.dict()
        doc_ref.set(grievance_dict)
        doc_id=doc_ref.id
        return {"message": "Grievance added successfully","acknowledgement number":doc_id ,"grievance": grievance}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

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



