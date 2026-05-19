import json 
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    WebSocket
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from sqlalchemy.orm import Session

from database import (
    engine,
    Base,
    get_db
)

from models import (
    User,
    Room,
    Message,
    RoomMember
)

from schemas import (
    RegisterSchema,
    LoginSchema,
    RoomSchema,
    InviteSchema,
    ForgotSchema,
    ResetSchema
)
from jose import jwt
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_reset_token,
    SECRET_KEY,
    ALGORITHM

)
from mail import ( send_reset_email)


from websocket import manager


# FASTAPI APP
app = FastAPI()


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-burst2.onrender.com",
        "http://localhost:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# CREATE TABLES
Base.metadata.create_all(bind=engine)


# HOME
@app.get("/")
def home():

    return {
        "message":
        "Burst Backend Running"
    }


# REGISTER
@app.post("/register")
def register(
    user: RegisterSchema,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(

        username=user.username,

        email=user.email,

        password=hash_password(
            user.password
        )
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message":
        "User registered successfully"
    }


# LOGIN
@app.post("/login")
def login(
    user: LoginSchema,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email"
        )

    if not verify_password(
        user.password,
        existing_user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token({

        "id": existing_user.id,

        "username":
        existing_user.username
    })

    return {

        "access_token": token,

        "token_type": "bearer",

        "id": existing_user.id,

        "username":
        existing_user.username
    }
    # GET ALL USERS
@app.get("/users")
def get_users(
    db: Session = Depends(get_db)
):

    users = db.query(User).all()

    return [

        {
            "id": user.id,

            "username":
            user.username,

            "email":
            user.email
        }

        for user in users
    ]


# CREATE ROOM
@app.post("/rooms")
def create_room(
    room: RoomSchema,
    db: Session = Depends(get_db)
):

    existing_room = db.query(Room).filter(
        Room.name == room.name
    ).first()

    if existing_room:

        raise HTTPException(
            status_code=400,
            detail="Room already exists"
        )

    # CREATE ROOM
    new_room = Room(
        name=room.name
    )

    db.add(new_room)

    db.commit()

    db.refresh(new_room)

    # ADD CREATOR TO ROOM
    room_member = RoomMember(

        room_id=new_room.id,

        user_id=room.user_id
    )

    db.add(room_member)

    db.commit()

    return {

        "id": new_room.id,

        "name": new_room.name
    }


# GET USER ROOMS
@app.get("/rooms/{user_id}")
def get_rooms(
    user_id: int,
    db: Session = Depends(get_db)
):

    rooms = db.query(Room).join(
        RoomMember,
        Room.id == RoomMember.room_id
    ).filter(
        RoomMember.user_id == user_id
    ).all()

    return [
        {
            "id": room.id,
            "name": room.name
        }
        for room in rooms
    ]


 
@app.post("/rooms/{room_id}/invite")
def invite_user(
    room_id: int,

    invite: InviteSchema,

    db: Session = Depends(get_db)
):

    # CHECK USER EXISTS
    user = db.query(User).filter(
        User.email == invite.email
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # CHECK ALREADY MEMBER
    existing_member = db.query(
        RoomMember
    ).filter(

        RoomMember.room_id
        == room_id,

        RoomMember.user_id
        == user.id

    ).first()

    if existing_member:

        raise HTTPException(
            status_code=400,
            detail=
            "User already in room"
        )

    # ADD USER
    new_member = RoomMember(

        room_id = room_id,

        user_id = user.id
    )

    db.add(new_member)

    db.commit()

    return {

        "message":
        "User invited successfully"
    }


# GET ROOM MESSAGES
@app.get("/messages/{room_id}")
def get_messages(
    room_id: int,
    db: Session = Depends(get_db)
):

    messages = db.query(Message).filter(
        Message.room_id == room_id
    ).all()

    return [
        {
            "id": message.id,

            "content":
            message.content,

            "created_at":
            str(message.created_at),

            "user_id":
            message.user_id,

            "room_id":
            message.room_id,

            "username":
            message.user.username
        }
        for message in messages
    ]
# FORGOT PASSWORD
@app.post(
    "/forgot-password"
)
def forgot_password(

    data:
    ForgotSchema,

    db: Session =
    Depends(get_db)

):

    # CHECK EMAIL EXISTS
    user = db.query(
        User
    ).filter(

        User.email
        == data.email

    ).first()

    if not user:

        raise HTTPException(

            status_code=404,

            detail= "User not found"
        )
    token= create_reset_token(user.email)
    send_reset_email(user.email,token)
    return {

        "message":"Reset link created"
       
    }
@app.post(
"/reset-password"
)
def reset_password(

    data:
    ResetSchema,

    db: Session=
    Depends(get_db)

):

    try:

        payload=jwt.decode(

            data.token,

            SECRET_KEY,

            algorithms=[
            ALGORITHM
            ]
        )

        email=payload.get(
        "sub"
        )

    except:

        raise HTTPException(

            status_code=401,

            detail=
            "Invalid token"
        )

    user=db.query(User).filter(

    User.email==email

    ).first()

    if not user:

        raise HTTPException(

        status_code=404,

        detail=
        "User not found"

        )

    user.password=hash_password(
    data.new_password
    )

    db.commit()

    return {

    "message":
    "Password rese successful"

    }
@app.delete("/rooms/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db)
):

    room = db.query(Room).filter(
        Room.id == room_id
    ).first()

    if not room:

        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    db.delete(room)

    db.commit()

    return {
        "message":
        "Room deleted"
    }
# WEBSOCKET
@app.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: int
):

    print("WS endpoint hit")
    print("Room:", room_id)
    print("Headers:", dict(websocket.headers))

    try:

        print(
            "Origin:",
            websocket.headers.get("origin")
        )

        await manager.connect(
            websocket,
            room_id
        )

        print(
            f"Connected room {room_id}"
        )

        db_generator = get_db()
        db = next(db_generator)

        while True:

            data = await websocket.receive_text()

            print("Received:", data)

            parsed_data = json.loads(data)

            print("Parsed:", parsed_data)

            new_message = Message(
                content=parsed_data.get("content"),
                user_id=parsed_data.get("user_id"),
                room_id=parsed_data.get("room_id"),
            )

            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            parsed_data["id"] = new_message.id

            parsed_data["created_at"] = str(
                new_message.created_at
            )

            await manager.broadcast(
                room_id,
                json.dumps(parsed_data)
            )

    except Exception as e:

        print(
            "WebSocket Error:",
            e
        )

        manager.disconnect(
            websocket,
            room_id
        )