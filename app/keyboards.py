from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Создать_заметку"),
            KeyboardButton(text="Открыть_заметку"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Приступим к записям",
)

ready_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Готово")]], resize_keyboard=True
)

confirm_delete_mind_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Да, удалить", callback_data="confirm_yes_delete_mind"
            ),
            InlineKeyboardButton(text="Отмена", callback_data="confirm_no_delete_mind"),
        ]
    ]
)


confirm_delete_note_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Да, удалить", callback_data="confirm_yes_delete_note"
            ),
            InlineKeyboardButton(text="Отмена", callback_data="confirm_no_delete_note"),
        ]
    ]
)


# notes_list=[]

# async def kb_builder_notes():
#     keyboard=InlineKeyboardBuilder()
#     for note in notes_list:
#         keyboard.add(InlineKeyboardButton(text=note, callback_data="open_note"))
#     return keyboard.adjust(3).as_markup()
