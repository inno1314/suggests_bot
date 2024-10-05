from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def channels_list(
    channels: list[dict], markup: InlineKeyboardMarkup, page: int = 0
) -> InlineKeyboardMarkup:
    # Собираем кнопки из текущего разметки
    buttons = []
    for row in markup.inline_keyboard[:1]:
        for button in row:
            buttons.append(button)

    # Создаем новую разметку с сохранением старых кнопок
    new_markup = InlineKeyboardMarkup(inline_keyboard=[])
    new_markup.inline_keyboard.append(buttons)

    channels_per_page = 2
    start_index = page * channels_per_page
    end_index = start_index + channels_per_page
    current_channels = channels[start_index:end_index]

    for channel in current_channels:
        new_markup.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=channel["name"], callback_data=f"send_to {channel['id']}"
                )
            ]
        )

    print(start_index, end_index, len(channels))

    if start_index == 0 and len(channels) > end_index:
        new_markup.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="Вперед ➡️", callback_data=f"channel_page {page + 1}"
                )
            ]
        )
    elif start_index > 0 and len(channels) > end_index:
        new_markup.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"channel_page {page - 1}"
                ),
                InlineKeyboardButton(
                    text="Вперед ➡️", callback_data=f"channel_page {page + 1}"
                ),
            ]
        )
    elif start_index > 0:
        new_markup.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"channel_page {page - 1}"
                )
            ]
        )

    new_markup.inline_keyboard.append(
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_publish")]
    )

    return new_markup
