from dataclasses import Field
from logging import raiseExceptions

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
class StudentSignupUser(BaseModel):
    name: str
    email: str
    roll_no:int
    gender:str
    contact_number:str
    password: str
    batch:int
    user_type:str

class FacultySignupUser(BaseModel):
    name: str
    email: str
    password: str
    user_type:str
    designation:str
    department:str
    contact_number:str



# User model for login
class LoginUser(BaseModel):
    email: str
    password: str
    userType:str

class GrievanceModel(BaseModel):
    title:str
    message:str
    user_ref:str

class approveUser(BaseModel):
    user_id:str
    user_type:str
    approved:bool

class replyModel(BaseModel):
    reply:str
    ack_number:str

@app.post("/api/v1/student/signup/")
async def signup_user(user: StudentSignupUser):
    try:
        # Check if the user already exists
        user_type=user.user_type
        users_ref = db.collection(user_type)
        existing_user = users_ref.where("email", "==", user.email).get()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")


        # Create a document with auto-generated ID
        doc_ref = db.collection(user_type).document()
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = hash_password(user_dict["password"])
        user_dict["approved"]=False
        doc_ref.set(user_dict)
        return {"message": "User signed up successfully", "user": user_dict}
    except Exception as e:
        print(f"error:{str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/faculty/signup/")
async def signup_user(user: FacultySignupUser):
    try:
        # Check if the user already exists
        print(user)
        user_type=user.user_type
        users_ref = db.collection(user_type)
        existing_user = users_ref.where("email", "==", user.email).get()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        # Create a document with auto-generated ID
        doc_ref = db.collection(user_type).document()
        user_dict = user.dict()
        # Hash the password before storing
        user_dict["password"] = hash_password(user_dict["password"])
        user_dict["approved"]=False
        doc_ref.set(user_dict)
        return {"message": "User signed up successfully", "user": user_dict}
    except Exception as e:
        print(f"error:{str(e)}")
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
        if not user_data["approved"]:
            raise HTTPException(status_code=400, detail="User not approved")
        return {
            "message": "Login successful",
            "user_data": user_data
        }
    except Exception as e:
        print(f"error:{str(e)}")
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
        grievance_dict=grievance.dict()
        grievance_dict["user_ref"]=grievance.user_ref
        doc_id = doc_ref.id
        grievance_dict["ack_number"]=doc_id
        grievance_dict["responded"]=False
        doc_ref.set(grievance_dict)
        return {"message": "Grievance added successfully","grievance": grievance_dict}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.put("/api/v1/admin/approve_user/")
async def approve_user(user:approveUser):
    try:
        print(user)
        doc_ref = db.collection(user.user_type).document(user.user_id)
        user_dict = user.dict()
        user_dict["approved"]=user.approved
        doc_ref.update(user_dict)
        return {"message": "User updated successfully", "user": user_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/v1/user/get_grievances/{user_id}")
async def my_grievances(user_id:str):
    try:
        doc_ref=db.collection("Grievance").where("user_ref","==",user_id)
        docs=doc_ref.stream()
        all_data=[]
        for doc in docs:
            doc_data=doc.to_dict()
            print(doc_data)
            all_data.append(doc_data)
        print(all_data)
        return{"message":"Grievance","data":all_data}
    except Exception as e:
        raise  HTTPException(status_code=500,detail=str(e))

@app.post("/api/v1/admin/reply_grievance/")
async def reply_grievance(reply:replyModel):
    try:
        ack_number=reply.ack_number
        doc_ref=db.collection("Grievance").document(ack_number)
        reply_dict=reply.dict()
        reply_dict["responded"]=True
        doc_ref.update(reply_dict)
        print(reply_dict)
        return {"message": "Replied to grievance successfully","ack_number":ack_number ,"reply": reply_dict}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


def get_approved_data(user_type:str):
    doc_ref = db.collection(user_type)
    docs = doc_ref.stream()
    data = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data["user_id"] = doc.id
        if doc_data["approved"]:
            data.append(doc_data)
    return data

def get_not_approved_data(user_type:str):
    doc_ref = db.collection(user_type)
    docs = doc_ref.stream()
    data = []
    for doc in docs:
        doc_data = doc.to_dict()
        doc_data["user_id"] = doc.id
        if not doc_data["approved"]:
            data.append(doc_data)
    return data


@app.get("/api/v1/get_approved_users")
async def get_approved_users():
    try:
        data=[]
        student_data=get_approved_data("student")
        teacher_data = get_approved_data("teacher")
        non_teacher_data = get_approved_data("non_teacher")
        data.append(student_data)
        data.append(teacher_data)
        data.append(non_teacher_data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.get("/api/v1/admin/get_pending_approval_users")
async def get_not_approved_users():
    try:
        data=[]
        student_data=get_not_approved_data("student")
        teacher_data = get_not_approved_data("teacher")
        non_teacher_data = get_not_approved_data("non_teacher")
        data.append(student_data)
        data.append(teacher_data)
        data.append(non_teacher_data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))