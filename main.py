from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import fastapi_cdn_host
import os, dotenv
dotenv.load_dotenv("./config/.env", override=True)
from module.user import WeChatManager
WCM = WeChatManager(target_chatroom=os.getenv("TARGET_GROUP"))
WCM.enableReceivingMsg()
WCM.wcf.get_contacts()
app = FastAPI()
fastapi_cdn_host.patch_docs(app)

# API 路由
@app.get("/add")
def add_user(id: str):
    print(id)
    try:
        status = WCM.send_group_invition(id, 100)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add users")
    
    if status == 0:
        raise HTTPException(status_code=404, detail="User not found")
    if status == 1:
        return {"message": "User added successfully"}