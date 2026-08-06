from html import entities

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from app.database.models import User, Note, Mind, async_session


async def set_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()


async def set_note_name(name_note: str, tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return False

        stmt = select(Note).where(Note.title == name_note, Note.user_id == user.id)
        note = await session.scalar(stmt)

        if not note:
            note = Note(title=name_note, user_id=user.id)
            session.add(note)
            await session.commit()
            return True
        else:
            return False


async def get_notes_names(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return

        notes_names = await session.scalars(
            select(Note.title).where(Note.user_id == user.id)
        )

        return list(notes_names.all())


async def get_note_name(tg_id, name_note):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return

        note = await session.scalar(
            select(Note).where(Note.title == name_note, Note.user_id == user.id)
        )

        if note:
            return note


async def set_minds(name_note, content_mind, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return

        note: Note | None = await session.scalar(
            select(Note).where(Note.title == name_note, User.tg_id == tg_id)
        )
        if not note:
            return

        count = await session.scalar(
            select(func.count(Mind.id)).where(Mind.note_id == note.id)
        )
        next_number = (count or 0) + 1

        new_mind = Mind(note_id=note.id, number_mind=next_number, content=content_mind)
        session.add(new_mind)
        await session.commit()


async def get_last_mind_number(name_note: str, tg_id: int):
    async with async_session() as session:
        stmt = (
            select(func.count(Mind.id))
            .join(Note)
            .join(User)
            .where(Note.title == name_note, User.tg_id == tg_id)
        )
        count = await session.scalar(stmt)
        return count or 0


async def get_all_minds(name_note: str, tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return

        note = await session.scalar(
            select(Note).where(Note.title == name_note, Note.user_id == user.id)
        )
        if not note:
            return

        minds = await session.scalars(select(Mind).where(Mind.note_id == note.id))

        return list(minds.all())


async def get_mind_by_number(name_note: str, tg_id: int, num_mind: int):
    async with async_session() as session:
        return await session.scalar(
            select(Mind)
            .join(Note)
            .join(User)
            .where(
                Note.title == name_note,
                User.tg_id == tg_id,
                Mind.number_mind == num_mind,
            )
        )


async def delete_mind_by_number(name_note: str, tg_id: int, num_mind: int):
    async with async_session() as session:
        mind = await session.scalar(
            select(Mind)
            .join(Note)
            .join(User)
            .where(
                Note.title == name_note,
                User.tg_id == tg_id,
                Mind.number_mind == num_mind,
            )
        )
        if not mind:
            return False

        note_id = mind.note_id
        await session.delete(mind)
        await session.flush()

        other_minds = await session.scalars(
            select(Mind)
            .where(Mind.note_id == note_id, Mind.number_mind > num_mind)
            .order_by(Mind.number_mind)
        )
        for item in other_minds:
            item.number_mind -= 1

        await session.commit()
        return True


async def delete_note(name_note: str, tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return False

        stmt = select(Note).where(Note.title == name_note, Note.user_id == user.id)

        note_to_delete = await session.scalar(stmt)

        if note_to_delete:
            await session.delete(note_to_delete)
            await session.commit()
            return True
        else:
            return False


async def update_mind_content(
    name_note: str, tg_id: int, num_mind: int, new_content: str
):
    async with async_session() as session:
        mind = await session.scalar(
            select(Mind)
            .join(Note)
            .join(User)
            .where(
                Note.title == name_note,
                User.tg_id == tg_id,
                Mind.number_mind == num_mind,
            )
        )
        if not mind:
            return False

        mind.content += f"\n{new_content}"

        await session.commit()
        return True


async def merge_notes(new_note_title: str, tg_id: int, mind_contents: list[str]):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return False

        existing_note = await session.scalar(
            select(Note).where(Note.title == new_note_title, Note.user_id == user.id)
        )
        if existing_note:
            return False

        new_note = Note(title=new_note_title, user_id=user.id)
        session.add(new_note)
        await session.flush()

        for index, content in enumerate(mind_contents, start=1):
            session.add(Mind(note_id=new_note.id, number_mind=index, content=content))

        await session.commit()
        return True
