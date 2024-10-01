from pydantic import BaseModel
from aiogram.types import Message, User, Chat, PhotoSize, Audio, Video, VideoNote, Voice, Animation, Document 
from typing import List, Optional
from datetime import datetime


class MessageModel(BaseModel):
    message_id: int
    from_user: User
    chat: Chat
    date: float
    caption: Optional[str] = None
    media_group_id: Optional[str] = None
    text: Optional[str] = None
    photo: Optional[List[PhotoSize]] = None
    video: Optional[Video] = None
    document: Optional[Document] = None
    animation: Optional[Animation] = None
    audio: Optional[Audio] = None
    voice: Optional[Voice] = None
    video_note: Optional[VideoNote] = None

    def to_aiogram(self) -> Message:
        return Message(
            message_id=self.message_id,
            from_user=User(**self.from_user.model_dump()),
            chat=Chat(**self.chat.model_dump()),
            date=datetime.fromtimestamp(self.date),
            caption=self.caption,
            media_group_id=self.media_group_id,
            text=self.text,
            photo=[PhotoSize(**photo.model_dump()) for photo in self.photo] if self.photo else None,
            video=Video(**self.video.model_dump()) if self.video else None,
            document=Document(**self.document.model_dump()) if self.document else None,
            animation=Animation(**self.animation.model_dump()) if self.animation else None,
            audio=Audio(**self.audio.model_dump()) if self.audio else None,
            voice=Voice(**self.voice.model_dump()) if self.voice else None,
            video_note=VideoNote(**self.video_note.model_dump()) if self.video_note else None
        )

