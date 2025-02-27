'''
Author: Henry Huang abs0lutely_zer0@outlook.com
Date: 2025-02-25 23:47:43
LastEditors: Henry Huang abs0lutely_zer0@outlook.com
LastEditTime: 2025-02-27 09:49:41
FilePath: \wechatbot-agent\main.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import fastapi_cdn_host
from module.user import WeChatManager
WCM = WeChatManager()
WCM.enableReceivingMsg()
WCM.wcf.get_contacts()
app = FastAPI()
fastapi_cdn_host.patch_docs(app)

# 模拟数据库中的用户和发送记录
fake_users_db = {"user1": {"id": "user1", "name": "Alice"}}
sent_records_db = set()

# 请求体模型
class SendRequest(BaseModel):
    user_id: str
    content: str

# 响应体模型
class SendResponse(BaseModel):
    code: int
    message: str
    data: Optional[dict]
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
        raise HTTPException(status_code=200, detail="Invitation sent, waiting for response")