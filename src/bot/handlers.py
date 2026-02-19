import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.bot.config import settings
from src.bot.i18n import TEXTS, get_text
from src.bot.keyboards import ask_walk_keyboard, language_keyboard, main_keyboard, parameter_keyboard
from src.bot.notifications import broadcast_walk
from src.bot.scheduler import (
    cancel_walk_timer,
    schedule_walk_finalization,
)
from src.bot.utils import parse_time as _parse_time
from src.database import crud
from src.database.session import async_session

router = Router()


class WalkStates(StatesGroup):
    """FSM states for multi-step user input flows."""
    awaiting_time = State()
    awaiting_name = State()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Handle /start command - show language selection."""
    await state.clear()
    logger.info(f"User {message.from_user.id} ({message.from_user.username}) started bot")
    await message.answer(
        text=get_text("welcome", "ru") + "\n" + get_text("welcome", "en"),
        reply_markup=language_keyboard(),
    )


@router.message(F.text == "🇷🇺 Русский")
async def set_russian(message: Message, state: FSMContext) -> None:
    """Set Russian language."""
    await _set_language(message, state, "ru")


@router.message(F.text == "🇬🇧 English")
async def set_english(message: Message, state: FSMContext) -> None:
    """Set English language."""
    await _set_language(message, state, "en")


async def _set_language(message: Message, state: FSMContext, lang: str) -> None:
    """Set user language and show main keyboard."""
    await state.clear()
    async with async_session() as session:
        user = await crud.get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
        )
        await crud.set_user_language(session, user.id, lang)
        logger.info(f"User {message.from_user.id} set language to {lang}")

    await message.answer(
        text=get_text("language_set", lang),
        reply_markup=main_keyboard(lang),
    )


@router.message(F.text.in_({TEXTS["ru"]["walk_button"], TEXTS["en"]["walk_button"]}))
async def start_walk(message: Message, state: FSMContext) -> None:
    """Handle walk button press - create walk and show parameter keyboard."""
    await state.clear()

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            logger.warning(f"Unregistered user {message.from_user.id} tried to start walk")
            await message.answer("Please /start first")
            return

        lang = user.language

        # Check for existing pending walk
        existing_walk = await crud.get_pending_walk(session, user.id)
        if existing_walk:
            logger.debug(f"User {user.telegram_id} has existing pending walk {existing_walk.id}")
            await message.answer(
                text=get_text("walk_started", lang),
                reply_markup=parameter_keyboard(lang),
            )
            return

        # Create new walk
        walk = await crud.create_walk(session, user.id)
        logger.info(f"User {user.telegram_id} ({user.username}) started walk {walk.id}")

        # Schedule auto-finalization
        await schedule_walk_finalization(user.id, walk.id)

        await message.answer(
            text=get_text("walk_started", lang),
            reply_markup=parameter_keyboard(lang),
        )


@router.message(F.text.in_({TEXTS["ru"]["walk_at_time_button"], TEXTS["en"]["walk_at_time_button"]}))
async def walk_at_time(message: Message, state: FSMContext) -> None:
    """Handle 'log walk at time' button - enter time-input mode."""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            logger.warning(f"Unregistered user {message.from_user.id} tried to log walk at time")
            await message.answer("Please /start first")
            return

        lang = user.language

        # If there's already a pending walk, just show parameter keyboard
        existing_walk = await crud.get_pending_walk(session, user.id)
        if existing_walk:
            logger.debug(f"User {user.telegram_id} has existing pending walk {existing_walk.id}")
            await message.answer(
                text=get_text("walk_started", lang),
                reply_markup=parameter_keyboard(lang),
            )
            return

    await state.set_state(WalkStates.awaiting_time)
    logger.info(f"User {message.from_user.id} entered time-input mode")
    await message.answer(text=get_text("enter_time_prompt", lang))


@router.message(F.text.in_({TEXTS["ru"]["didnt_poop"], TEXTS["en"]["didnt_poop"]}))
async def toggle_didnt_poop(message: Message, state: FSMContext) -> None:
    """Toggle 'didn't poop' parameter."""
    await _toggle_param(message, state, "didnt_poop")


@router.message(F.text.in_({TEXTS["ru"]["long_walk"], TEXTS["en"]["long_walk"]}))
async def toggle_long_walk(message: Message, state: FSMContext) -> None:
    """Toggle 'long walk' parameter."""
    await _toggle_param(message, state, "long_walk")


async def _toggle_param(message: Message, state: FSMContext, param: str) -> None:
    """Toggle a walk parameter."""
    await state.clear()

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Please /start first")
            return

        lang = user.language
        walk = await crud.get_pending_walk(session, user.id)

        if walk is None:
            logger.debug(f"User {message.from_user.id} tried to toggle param without active walk")
            await message.answer(
                text=get_text("no_active_walk", lang),
                reply_markup=main_keyboard(lang),
            )
            return

        # Toggle the parameter
        if param == "didnt_poop":
            new_value = not walk.didnt_poop
            await crud.update_walk_params(session, walk.id, didnt_poop=new_value)
        elif param == "long_walk":
            new_value = not walk.long_walk
            await crud.update_walk_params(session, walk.id, long_walk=new_value)

        logger.debug(f"User {user.telegram_id} toggled {param}={new_value} for walk {walk.id}")

        await message.answer(
            text=get_text("param_toggled", lang),
            reply_markup=parameter_keyboard(lang),
        )


@router.message(F.text.in_({TEXTS["ru"]["send"], TEXTS["en"]["send"]}))
async def send_walk(message: Message, state: FSMContext, bot: Bot) -> None:
    """Finalize and send walk notification."""
    await state.clear()

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Please /start first")
            return

        lang = user.language
        walk = await crud.get_pending_walk(session, user.id)

        if walk is None:
            logger.debug(f"User {message.from_user.id} tried to send without active walk")
            await message.answer(
                text=get_text("no_active_walk", lang),
                reply_markup=main_keyboard(lang),
            )
            return

        # Cancel the timer
        await cancel_walk_timer(user.id)

        # Finalize the walk
        walk = await crud.finalize_walk(session, walk.id)
        logger.info(
            f"User {user.telegram_id} ({user.username}) finalized walk {walk.id} "
            f"[didnt_poop={walk.didnt_poop}, long_walk={walk.long_walk}]"
        )

        # Send confirmation
        await message.answer(
            text=get_text("walk_sent", lang),
            reply_markup=main_keyboard(lang),
        )

        # Broadcast to all users
        await broadcast_walk(session, walk, user, bot)


@router.message(F.text.in_({TEXTS["ru"]["cancel"], TEXTS["en"]["cancel"]}))
async def cancel_walk(message: Message, state: FSMContext) -> None:
    """Cancel the current pending walk."""
    await state.clear()

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Please /start first")
            return

        lang = user.language
        walk = await crud.get_pending_walk(session, user.id)

        if walk is None:
            await message.answer(
                text=get_text("no_active_walk", lang),
                reply_markup=main_keyboard(lang),
            )
            return

        await cancel_walk_timer(user.id)
        await crud.delete_walk(session, walk.id)
        logger.info(f"User {user.telegram_id} cancelled walk {walk.id}")

        await message.answer(
            text=get_text("walk_cancelled", lang),
            reply_markup=main_keyboard(lang),
        )


@router.message(F.text.in_({TEXTS["ru"]["change_name_button"], TEXTS["en"]["change_name_button"]}))
async def change_name(message: Message, state: FSMContext) -> None:
    """Handle 'change name' button - enter name-input mode."""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            logger.warning(f"Unregistered user {message.from_user.id} tried to change name")
            await message.answer("Please /start first")
            return

        lang = user.language
        current = user.display_name or user.username or f"User {user.telegram_id}"

    await state.set_state(WalkStates.awaiting_name)
    logger.info(f"User {message.from_user.id} entered name-input mode")
    await message.answer(text=get_text("change_name_prompt", lang).format(current=current))


@router.message(F.text.in_({TEXTS["ru"]["ask_walk_button"], TEXTS["en"]["ask_walk_button"]}))
async def ask_walk(message: Message, state: FSMContext) -> None:
    """Show inline keyboard for selecting walk request recipient."""
    await state.clear()

    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            await message.answer("Please /start first")
            return

        lang = user.language
        users = await crud.get_all_active_users(session)

    await message.answer(
        text=get_text("ask_walk_choose", lang),
        reply_markup=ask_walk_keyboard(users, lang),
    )


@router.callback_query(F.data.startswith("ask_walk:"))
async def ask_walk_callback(callback: CallbackQuery, bot: Bot) -> None:
    """Send walk request to selected user(s)."""
    target = callback.data.split(":", 1)[1]

    async with async_session() as session:
        requester = await crud.get_user_by_telegram_id(session, callback.from_user.id)
        if requester is None:
            await callback.answer("Please /start first")
            return

        lang = requester.language
        requester_name = (
            requester.display_name or requester.username or f"User {requester.telegram_id}"
        )

        if target == "all":
            recipients = await crud.get_all_active_users(session)
        else:
            target_user = await crud.get_user_by_telegram_id(session, int(target))
            recipients = [target_user] if target_user else []

    sent = 0
    for recipient in recipients:
        msg = get_text("ask_walk_request", recipient.language).format(requester=requester_name)
        try:
            await bot.send_message(chat_id=recipient.telegram_id, text=msg)
            sent += 1
        except Exception as e:
            logger.warning(f"Failed to send walk request to {recipient.telegram_id}: {e}")

    logger.info(f"User {callback.from_user.id} sent walk request to {target!r} ({sent} delivered)")
    await callback.answer(get_text("ask_walk_sent", lang))
    # Remove inline keyboard after selection
    await callback.message.edit_reply_markup(reply_markup=None)


# --- FSM state handlers: registered after button handlers, before the catch-all ---


@router.message(WalkStates.awaiting_time)
async def handle_time_input(message: Message, state: FSMContext) -> None:
    """Process time input from a user in time-entry mode."""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            return

        lang = user.language
        parsed = _parse_time(message.text or "")

        if parsed is None:
            logger.debug(f"User {message.from_user.id} sent unparseable time: {message.text!r}")
            await message.answer(text=get_text("invalid_time", lang))
            return

        # Create walk with the custom time
        walk = await crud.create_walk(session, user.id)
        await crud.update_walk_time(session, walk.id, parsed)

        await state.clear()
        logger.info(f"User {user.telegram_id} set walk {walk.id} time to {parsed}")

        # Schedule auto-finalization
        await schedule_walk_finalization(user.id, walk.id)

        # Build confirmation — append "(yesterday)" when date differs
        # parsed is naive UTC; convert to local time for display
        tz = ZoneInfo(settings.display_timezone)
        local_time = parsed.replace(tzinfo=timezone.utc).astimezone(tz)
        time_str = local_time.strftime("%H:%M")
        if local_time.date() < datetime.now(tz).date():
            time_str += f" ({get_text('yesterday', lang)})"

        await message.answer(
            text=get_text("time_set", lang).format(time=time_str),
            reply_markup=parameter_keyboard(lang),
        )


@router.message(WalkStates.awaiting_name)
async def handle_name_input(message: Message, state: FSMContext) -> None:
    """Process name input from a user in name-entry mode."""
    async with async_session() as session:
        user = await crud.get_user_by_telegram_id(session, message.from_user.id)
        if user is None:
            return

        lang = user.language
        name = (message.text or "").strip()

        if not name:
            await message.answer(text=get_text("invalid_name", lang))
            return

        if len(name) > 30 or not re.fullmatch(r"[\w\s]+", name, re.UNICODE):
            await message.answer(text=get_text("invalid_name_format", lang))
            return

        await crud.set_display_name(session, user.id, name)

    await state.clear()
    logger.info(f"User {message.from_user.id} set display name to {name!r}")
    await message.answer(
        text=get_text("name_set", lang).format(name=name),
        reply_markup=main_keyboard(lang),
    )


# --- catch-all: MUST be registered after every other handler ---


@router.message(StateFilter(None))
async def handle_unexpected(message: Message) -> None:
    """Silently ignore unexpected messages when no FSM state is active."""
    pass
