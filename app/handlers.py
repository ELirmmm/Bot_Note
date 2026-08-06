from os import name

from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import app.keyboards as kb
import app.database.requests as rq

router = Router()


class CreateNote(StatesGroup):
    note_name = State()
    content = State()


class OpenNote(StatesGroup):
    note_name = State()
    content = State()


class Edit(StatesGroup):
    edit = State()


class Merge(StatesGroup):
    merge_1 = State()
    merge_2 = State()
    merge_3 = State()


class NoteActions(StatesGroup):
    waiting_for_confirm_delete_mind = State()
    waiting_for_confirm_delete_note = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    assert message.from_user is not None
    await rq.set_user(message.from_user.id)
    await message.answer(
        "Добро пожловать!\n"
        "Этот бот поможет вам вести заметки"
        " и сохранять их на ваш компьютер.\n",
        reply_markup=kb.main_kb,
    )


@router.message(Command("ready"))
async def cmd_ready(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Заметка успешно сохранена и закрыта!", reply_markup=kb.main_kb
    )


@router.message(F.text == "Готово")
async def decor_cmd_ready(message: Message, state: FSMContext):
    await cmd_ready(message=message, state=state)


@router.message(Command("view_notes"))
async def cmd_view_notes(message: Message):
    assert message.from_user is not None

    notes = await rq.get_notes_names(tg_id=message.from_user.id)

    if notes:
        text_lines = [f"{i}. {note}" for i, note in enumerate(notes, start=1)]
        notes_text = "\n".join(text_lines)

        await message.answer(text=f"Ваши заметки:\n\n{notes_text}")
    else:
        await message.answer(text="У вас пока нет заметок")


@router.message(Command("view_minds"), StateFilter(CreateNote.content, OpenNote.content))
async def cmd_view_minds(message: Message, state: FSMContext):
    assert message.from_user is not None

    data = await state.get_data()
    name_note = data.get("name_note")

    if not name_note:
        await message.answer("Название заметки не найдено")
        return

    minds = await rq.get_all_minds(name_note=name_note, tg_id=message.from_user.id)

    if minds:
        text_lines = [
            f"Мысль №{i}. \n{mind.content}\n" for i, mind in enumerate(minds, start=1)
        ]
        minds_text = "\n".join(text_lines)

        await message.answer(text=f"{name_note}\n\n{minds_text}")
    else:
        await message.answer(text="В этой заметке пока нет сохраненных мыслей")


@router.message(Command("note"), StateFilter(CreateNote.content, OpenNote.content))
async def cmd_note(message: Message, command: CommandObject, state: FSMContext):
    assert message.from_user is not None
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return
    if not command.args or not command.args.isdigit():
        print("Напишите команду, добавив номер мысли, пример: `/note 3`")
        return

    num_mind = int(command.args)

    data = await state.get_data()
    name_note = data.get("name_note")

    mind = await rq.get_mind_by_number(str(name_note), message.from_user.id, num_mind)
    if mind:
        assert mind is not None
        await message.answer(mind.content)
    else:
        await message.answer("Мысли с таким номером не существует")


@router.message(Command("edit"), StateFilter(CreateNote.content, OpenNote.content))
async def cmd_edit_1(message: Message, command: CommandObject, state: FSMContext):
    assert message.from_user is not None
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return
    if not command.args or not command.args.isdigit():
        print("Напишите команду, добавив номер мысли, пример: `/edit 3`")
        return

    num_mind = int(command.args)

    data = await state.get_data()
    name_note = data.get("name_note")
    current_state = await state.get_state()
    await state.update_data(previous_state=current_state)
    await state.update_data(num_mind=num_mind)

    mind = await rq.get_mind_by_number(str(name_note), message.from_user.id, num_mind)
    if mind:
        await message.answer("Напишите, что хотите добавить в вашу мысль")
        await state.set_state(Edit.edit)
    else:
        await message.answer("Мысли с таким номером нет")


@router.message(Edit.edit)
async def cmd_edit_2(message: Message, state: FSMContext):
    data = await state.get_data()
    name_note = data.get("name_note")
    num_mind = data.get("num_mind")
    previous_state = data.get("previous_state")

    assert message.from_user is not None
    await rq.update_mind_content(name_note=name_note, num_mind=num_mind, tg_id=message.from_user.id, new_content=message.text)  # type: ignore
    await message.answer("Содержимое мысли успешно изменено")
    await state.set_state(previous_state)


@router.message(Command("delete_note"))
async def cmd_delete_note(message: Message, command: CommandObject, state: FSMContext):
    assert message.from_user is not None
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return
    if not command.args:
        await message.answer(
            "Напишите имя заметки для удаления, например: `/delete_note имя_заметки`"
        )
        return

    name_note = str(command.args)

    await state.update_data(name_note=name_note)

    note = await rq.get_note_name(tg_id=message.from_user.id, name_note=name_note)

    if note:
        await message.answer(
            text=f"Вы уверены, что хотите удалить заметку `{name_note}`?",
            reply_markup=kb.confirm_delete_note_kb,
        )
        await state.set_state(NoteActions.waiting_for_confirm_delete_note)
    else:
        await message.answer("Заметки с таким именем не существует")


# Если пользователь выбрад "Да, удалить"
@router.callback_query(
    F.data == "confirm_yes_delete_note", NoteActions.waiting_for_confirm_delete_note
)
async def confirm_yes_delete_note(callback: CallbackQuery, state: FSMContext):
    assert callback.from_user is not None

    data = await state.get_data()
    name_note = data.get("name_note")

    assert name_note

    success = await rq.delete_note(name_note=name_note, tg_id=callback.from_user.id)

    if isinstance(callback.message, Message):
        if success:
            await callback.message.edit_text(text=f"Заметка {name_note} удалена")
        else:
            await callback.message.edit_text(text=f"Заметка {name_note} не найдена")

    await callback.answer(text="Удалено" if success else "Ошибка")


# Если пользователь нажал "Отмена"
@router.callback_query(
    F.data == "confirm_no_delete_note", NoteActions.waiting_for_confirm_delete_note
)
async def confirm_no_delete_note(callback: CallbackQuery):
    if isinstance(callback.message, Message):
        await callback.message.edit_text(text="Действие отменено")
    await callback.answer(text="Отменено")


@router.message(Command("delete_mind"), StateFilter(CreateNote.content, OpenNote.content))
async def cmd_delete_mind(message: Message, command: CommandObject, state: FSMContext):
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return
    if not command.args or not command.args.isdigit():
        await message.answer(
            "Укажите номер мысли для удаления, например: `/delete_mind 1`"
        )
        return

    num_mind = int(command.args)

    await state.update_data(num_mind=num_mind)
    await state.set_state(NoteActions.waiting_for_confirm_delete_mind)

    await message.answer(
        text=f"Вы уверены, что хотите удалить Мысль №{num_mind}?",
        reply_markup=kb.confirm_delete_mind_kb,
    )


# Если пользователь выбрал "Да, удалить"
@router.callback_query(F.data == "confirm_yes_delete_mind", NoteActions.waiting_for_confirm_delete_mind)
async def confirm_yes_delete_mind(callback: CallbackQuery, state: FSMContext):
    assert callback.from_user is not None

    data = await state.get_data()
    num_mind = data.get("num_mind")
    name_note = data.get("name_note")

    assert name_note and num_mind

    success = await rq.delete_mind_by_number(
        name_note=name_note, tg_id=callback.from_user.id, num_mind=num_mind
    )

    if isinstance(callback.message, Message):
        if success:
            await callback.message.edit_text(text=f"Мысль №{num_mind} удалена")
        else:
            await callback.message.edit_text(
                text=f"Мысль №{num_mind} не найдена в этой заметке."
            )

    await state.set_state(CreateNote.content)
    await callback.answer(text="Удалено" if success else "Ошибка")


# Если пользователь нажал "Отмена"
@router.callback_query(F.data == "confirm_no_delete_mind", NoteActions.waiting_for_confirm_delete_mind)
async def confirm_no_delete_mind(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateNote.content)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(text="Действие отменено")
    await callback.answer(text="Отменено")


@router.message(F.text == "Создать_заметку")
async def create_1(message: Message, state: FSMContext):
    await state.set_state(CreateNote.note_name)
    await message.answer("Назовите свою новую заметку")


@router.message(CreateNote.note_name)
async def create_2(message: Message, state: FSMContext):
    name_note = f"{message.text}"
    assert message.from_user is not None
    is_created = await rq.set_note_name(name_note=name_note, tg_id=message.from_user.id)
    if is_created:
        await state.update_data(name_note=name_note)
        await message.answer(
            "Заполните заметку своими мыслями.\nЧтобы сохранить заметку - нажмите <Готово>",
            reply_markup=kb.ready_kb,
        )
        await state.set_state(CreateNote.content)
    else:
        await message.answer(
            "Заметка с таким именем уже существует.\n" "Придумайте другое название"
        )


@router.message(CreateNote.content)
async def create_3(message: Message, state: FSMContext):
    assert message.from_user is not None
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return

    content = message.text
    data = await state.get_data()
    name_note = data.get("name_note")

    await state.update_data(content=content)
    await rq.set_minds(
        name_note=name_note,
        content_mind=content,
        tg_id=message.from_user.id,
    )
    await message.answer(f"Мысль сохранена")


@router.message(F.text == "Открыть_заметку")
async def open_1(message: Message, state: FSMContext):
    await state.set_state(OpenNote.note_name)
    await message.answer("Напишите имя заметки, которую хотите открыть")


@router.message(OpenNote.note_name)
async def open_2(message: Message, state: FSMContext):
    assert message.from_user is not None

    if message.text == None:
        message.answer("Напишите название заметки")
        return

    name_note = str(message.text)
    is_created = await rq.get_note_name(name_note=name_note, tg_id=message.from_user.id)

    if is_created:
        await message.answer(
            f"Вы открыли заметку {name_note}.\n"
            "Заполните заметку своими мыслями.\n"
            "Чтобы сохранить заметку - нажмите <Готово>",
            reply_markup=kb.ready_kb,
        )
        await state.update_data(name_note=name_note)
        await state.set_state(OpenNote.content)
    else:
        await message.answer("Заметки с такоим именем не существует")


@router.message(OpenNote.content)
async def open_3(message: Message, state: FSMContext):
    assert message.from_user is not None
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return

    content = message.text
    data = await state.get_data()
    name_note = data.get("name_note")

    await state.update_data(content=content)
    await rq.set_minds(
        name_note=name_note,
        content_mind=content,
        tg_id=message.from_user.id,
    )
    await message.answer(f"Мысль сохранена")


@router.message(Command("merge"))
async def cmd_merge(message: Message, state: FSMContext):
    await message.answer("Напишите название первой заметки")
    await state.set_state(Merge.merge_1)


@router.message(Merge.merge_1)
async def cmd_merge_1(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return

    first_note = message.text

    assert message.from_user is not None
    first_minds_obj = await rq.get_all_minds(
        name_note=first_note, tg_id=message.from_user.id
    )

    if first_minds_obj:
        first_minds_content = [mind.content for mind in first_minds_obj]
        await state.update_data(first_minds=first_minds_content)
        await message.answer("Напишите название второй заметки")
        await state.set_state(Merge.merge_2)
    else:
        await message.answer("Заметка не может быть пустой")


@router.message(Merge.merge_2)
async def cmd_merge_2(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return

    second_note = message.text

    assert message.from_user is not None
    second_minds_obj = await rq.get_all_minds(
        name_note=second_note, tg_id=message.from_user.id
    )

    if second_minds_obj:
        second_minds_content = [mind.content for mind in second_minds_obj]
        await state.update_data(second_minds=second_minds_content)
        await message.answer(
            "Напишите название новой заметки, "
            "в которой будет находиться содержимое двух вышеназванных заметок"
        )
        await state.set_state(Merge.merge_3)
    else:
        await message.answer("Заметка не может быть пустой")


@router.message(Merge.merge_3)
async def cmd_merge_3(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Отправляйте только текстовое сообщение")
        return

    new_note = message.text
    data = await state.get_data()
    first_minds = data.get("first_minds")
    second_minds = data.get("second_minds")

    assert message.from_user is not None
    assert first_minds is not None
    assert second_minds is not None

    new_content = [*first_minds, *second_minds]

    is_created = await rq.merge_notes(
        new_note_title=new_note, tg_id=message.from_user.id, mind_contents=new_content
    )
    if is_created:
        await message.answer("Заметки успешно объединены!")
    else:
        await message.answer("Заметка с таким названием уже есть, придумайте другое")
        return
