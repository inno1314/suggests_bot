from aiogram.types import (
    Message,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
    InputMediaDocument,
)


def restore_album_part(
    message: Message, sign: str, html_text: str
) -> InputMediaPhoto | InputMediaVideo | InputMediaAudio | InputMediaDocument | None:
    caption = html_text + sign if message.caption is not None else sign

    if message.photo:
        return InputMediaPhoto(media=message.photo[-1].file_id, caption=caption)
    if message.video:
        return InputMediaVideo(media=message.video.file_id, caption=caption)
    if message.audio:
        return InputMediaAudio(media=message.audio.file_id, caption=caption)
    if message.document:
        return InputMediaDocument(media=message.document.file_id, caption=caption)
    return None


def restore_album(
    messages: list[Message], sign: str, html_text: str
) -> list[InputMediaPhoto | InputMediaVideo | InputMediaAudio | InputMediaDocument]:
    media = list()
    for message in messages:
        new_sign = sign
        msg_media = bool(message.video or message.audio or message.document)
        if ((len(media) > 0) and (not msg_media)) or (
            msg_media and (len(messages) - len(media) != 1)
        ):
            new_sign = ""
        item = restore_album_part(message, new_sign, html_text)
        if item is not None:
            media.append(item)
    return media
