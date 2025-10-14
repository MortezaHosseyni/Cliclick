"""
Support chat routes
مسیرهای گفتگوی پشتیبانی
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
from app.db.database import get_db
from app.db.models.user import User
from app.db.models.support import SupportChat, SupportMessage
from app.db.schemas.support import SupportChatCreate, SupportChatResponse, SupportMessageCreate, SupportMessageResponse
from app.core.security import get_current_user, get_current_secretary_or_admin
from app.utils.messages_fa import ERROR_MESSAGES, SUCCESS_MESSAGES

router = APIRouter(prefix="/support", tags=["پشتیبانی / Support"])

# WebSocket connection manager / مدیریت اتصالات وب‌سوکت
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        self.active_connections[chat_id] = websocket
    
    def disconnect(self, chat_id: int):
        if chat_id in self.active_connections:
            del self.active_connections[chat_id]
    
    async def send_message(self, message: str, chat_id: int):
        if chat_id in self.active_connections:
            await self.active_connections[chat_id].send_text(message)

manager = ConnectionManager()


@router.post("/chats", response_model=SupportChatResponse, status_code=status.HTTP_201_CREATED, summary="ایجاد گفتگو جدید")
async def create_chat(
    chat_data: SupportChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new support chat
    ایجاد گفتگوی پشتیبانی جدید
    """
    # Create new chat / ایجاد گفتگوی جدید
    new_chat = SupportChat(
        patient_user_id=current_user.id,
        subject=chat_data.subject
    )
    
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    
    chat_dict = SupportChatResponse.model_validate(new_chat).model_dump()
    chat_dict["patient_name"] = current_user.full_name
    
    return SupportChatResponse(**chat_dict)


@router.get("/chats", response_model=List[SupportChatResponse], summary="دریافت لیست گفتگوها")
async def get_chats(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get support chats
    دریافت گفتگوهای پشتیبانی
    """
    if current_user.role in ["Admin", "Secretary"]:
        # Get all chats for admin/secretary / دریافت تمام گفتگوها برای مدیر/منشی
        chats = db.query(SupportChat).offset(skip).limit(limit).all()
    else:
        # Get only user's chats for patients / فقط گفتگوهای خود کاربر برای بیماران
        chats = db.query(SupportChat).filter(
            SupportChat.patient_user_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    result = []
    for chat in chats:
        chat_dict = SupportChatResponse.model_validate(chat).model_dump()
        chat_dict["patient_name"] = chat.patient_user.full_name
        result.append(SupportChatResponse(**chat_dict))
    
    return result


@router.get("/chats/{chat_id}", response_model=SupportChatResponse, summary="دریافت اطلاعات گفتگو")
async def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get chat by ID
    دریافت گفتگو با شناسه
    """
    chat = db.query(SupportChat).filter(SupportChat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["support_chat_not_found"]
        )
    
    # Check access / بررسی دسترسی
    if current_user.role == "Patient" and chat.patient_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES["permission_denied"]
        )
    
    chat_dict = SupportChatResponse.model_validate(chat).model_dump()
    chat_dict["patient_name"] = chat.patient_user.full_name
    
    # Add sender names to messages / افزودن نام فرستنده به پیام‌ها
    for i, msg in enumerate(chat_dict["messages"]):
        sender = db.query(User).filter(User.id == msg["sender_user_id"]).first()
        chat_dict["messages"][i]["sender_name"] = sender.full_name if sender else None
    
    return SupportChatResponse(**chat_dict)


@router.post("/messages", response_model=SupportMessageResponse, status_code=status.HTTP_201_CREATED, summary="ارسال پیام")
async def send_message(
    message_data: SupportMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send message to chat
    ارسال پیام به گفتگو
    """
    # Check if chat exists / بررسی وجود گفتگو
    chat = db.query(SupportChat).filter(SupportChat.id == message_data.chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["support_chat_not_found"]
        )
    
    # Check access / بررسی دسترسی
    if current_user.role == "Patient" and chat.patient_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES["permission_denied"]
        )
    
    # Create new message / ایجاد پیام جدید
    new_message = SupportMessage(
        chat_id=message_data.chat_id,
        sender_user_id=current_user.id,
        message=message_data.message
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    msg_dict = SupportMessageResponse.model_validate(new_message).model_dump()
    msg_dict["sender_name"] = current_user.full_name
    
    # Try to send via WebSocket / تلاش برای ارسال از طریق وب‌سوکت
    await manager.send_message(message_data.message, message_data.chat_id)
    
    return SupportMessageResponse(**msg_dict)


@router.put("/chats/{chat_id}/close", response_model=SupportChatResponse, summary="بستن گفتگو")
async def close_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_secretary_or_admin)
):
    """
    Close support chat (Secretary/Admin only)
    بستن گفتگوی پشتیبانی (فقط منشی/مدیر)
    """
    chat = db.query(SupportChat).filter(SupportChat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["support_chat_not_found"]
        )
    
    chat.status = "Closed"
    db.commit()
    db.refresh(chat)
    
    chat_dict = SupportChatResponse.model_validate(chat).model_dump()
    chat_dict["patient_name"] = chat.patient_user.full_name
    
    return SupportChatResponse(**chat_dict)


@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    """
    WebSocket endpoint for real-time chat
    نقطه پایانی وب‌سوکت برای گفتگوی آنی
    """
    await manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(f"Echo: {data}", chat_id)
    except WebSocketDisconnect:
        manager.disconnect(chat_id)