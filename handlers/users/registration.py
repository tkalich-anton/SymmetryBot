import bcrypt
import re

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ContentTypes

from data import config
from filters import IsUnregistered
from keyboards.inline.keyboard_generators import generate_inline_keyboard
from keyboards.inline.register_keyboard import role_keyboard
from loader import dp, bot
from states.registration import Registration
from utils.db_api.database import db
from utils.db_api.models import User, Student, Parent, Curator, Teacher
from utils.useful_functions import answer_and_delete


@dp.message_handler(Text(equals=["Отменить", "отменить", "Отменить регистрацию", "отменить регистрацию"]),
                    state=Registration)
async def cancel_registration(message: Message, state: FSMContext):
    user_data = await state.get_data()
    # ID сообщения "Начать регистрацию"
    call_id = user_data["call_registration_id"]
    await state.finish()
    await bot.edit_message_text(
        message_id=call_id,
        chat_id=message.from_user.id,
        text=f"Вы отменили регистрацию.\n"
             f"Если хотите, можете пройти регистрацию заново.",
        reply_markup=generate_inline_keyboard([
            {"text": "🚀Начать регистрацию", "callback_data": "start_registration"}
        ])
    )
    await message.delete()


@dp.callback_query_handler(text="cancel_registration", state=Registration)
async def cancel_registration(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(
        f"Вы отменили регистрацию.\n"
        f"Если хотите, можете пройти регистрацию заново.",
        reply_markup=generate_inline_keyboard([
            {"text": "🚀Начать регистрацию", "callback_data": "start_registration"}
        ])
    )


@dp.callback_query_handler(IsUnregistered(), text="start_registration")
async def wait_first_name(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        f"🔥Отлично! Приступим...\n\n"
        f"Я задам несколько вопросов. Это займет не более 2️⃣ минут.\n\n"
        f"Итак, напишите ваше имя (только имя)",
        reply_markup=generate_inline_keyboard([
            {"text": "Отменить регистрацию", "callback_data": "cancel_registration"}
        ])
    )
    await Registration.wait_first_name.set()
    call_registration_id = call.message.message_id
    await state.update_data(call_registration_id=call_registration_id)
    await call.answer()


@dp.callback_query_handler(text="to_wait_first_name", state=Registration)
async def to_wait_first_name(call: CallbackQuery):
    await Registration.wait_first_name.set()
    await call.message.edit_text(
        f"Напишите ваше имя",
        reply_markup=generate_inline_keyboard([
            {"text": "Отменить регистрацию", "callback_data": "cancel_registration"}
        ])
    )
    await call.answer()


@dp.message_handler(state=Registration.wait_first_name)
async def check_first_name(message: Message, state: FSMContext):
    user_data = await state.get_data()
    # ID сообщения "Начать регистрацию"
    call_id = user_data["call_registration_id"]
    if re.match("^[а-яА-Я*]{1,23}$", message.text):
        await state.update_data(first_name=message.text.capitalize())
        await Registration.wait_last_name.set()
        await bot.edit_message_text(
            message_id=call_id,
            chat_id=message.from_user.id,
            text=f"Отлично, {message.text.capitalize()}!🙂\n"
                 f"Теперь напишите вашу фамилию",
            reply_markup=generate_inline_keyboard([
                {"text": "Назад", "callback_data": "to_wait_first_name"}
            ])
        )
        await message.delete()
    else:
        await answer_and_delete(
            message=message,
            text=f"Имя должно являться одним словом хотя бы из двух букв русского алфавита.\n"
                 f"Введите корректное имя!",
            delay=6
        )


@dp.callback_query_handler(text="to_wait_last_name", state=Registration)
async def to_wait_last_name(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await Registration.wait_last_name.set()
    await call.message.edit_text(
        text=f"{user_data['first_name']}, напишите вашу фамилию",
        reply_markup=generate_inline_keyboard([
            {"text": "Назад", "callback_data": "to_wait_first_name"}
        ])
    )
    await call.answer()


@dp.message_handler(state=Registration.wait_last_name)
async def check_last_name(message: Message, state: FSMContext):
    user_data = await state.get_data()
    call_id = user_data["call_registration_id"]
    if re.match("^[а-яА-Я*]{1,23}$", message.text):
        await state.update_data(last_name=message.text.capitalize())
        user_data = await state.get_data()
        await Registration.wait_role.set()
        await bot.edit_message_text(
            message_id=call_id,
            chat_id=message.from_user.id,
            text=f"Приятно познакомиться,\n{user_data['first_name']} {user_data['last_name']} 🤝\n"
                 f"Давайте определимся с вашей ролью:",
            reply_markup=role_keyboard()
        )
        await message.delete()
    else:
        await answer_and_delete(
            message=message,
            text=f"Фамилия должна являться одним словом хотя бы из двух букв русского алфавита.\n"
                 f"Введите корректную фамилию!",
            delay=6
        )


@dp.callback_query_handler(text="to_wait_role", state=Registration)
async def to_wait_role(call: CallbackQuery):
    await Registration.wait_role.set()
    await call.message.edit_text(
        text=f"Итак, давайте попробуем еще раз.\n"
             f"Ваша роль:",
        reply_markup=role_keyboard()
    )
    await call.answer()


@dp.callback_query_handler(text="student", state=Registration.wait_role)
async def role_student(call: CallbackQuery, state: FSMContext):
    await state.update_data(role=call.data)
    await call.message.edit_text(
        text=f"Вот бы и мне сейчас вернуться обратно в школу🎒\n"
             f"Предупреждаю сразу, мы не любим халявщиков! Так что советуем приготовиться к плодотворной работе)\n"
             f"Хорошо, теперь введите свой Email",
        reply_markup=generate_inline_keyboard([
            {"text": "Назад", "callback_data": "to_wait_role"}
        ])
    )
    await Registration.wait_email.set()
    await call.answer()


@dp.callback_query_handler(text="parent", state=Registration.wait_role)
async def role_parent(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(role=call.data)
    await call.message.edit_text(
        text=f"Записал, что вы — Родитель👌\n"
             f"Будьте уверены, ваш ребенок оказался в надежных руках)\n"
             f"Теперь введите ваш Email",
        reply_markup=generate_inline_keyboard([
            {"text": "Назад", "callback_data": "to_wait_role"}
        ])
    )
    await Registration.wait_email.set()


@dp.callback_query_handler(text="teacher", state=Registration.wait_role)
@dp.callback_query_handler(text="curator", state=Registration.wait_role)
async def role_teacher_curator(call: CallbackQuery, state: FSMContext):
    await state.update_data(role=call.data)
    await call.message.edit_text(
        text=f"Приятно видеть своих 🤜🤛\n"
             f"Чтобы прдолжить, нужен секретный код.",
        reply_markup=generate_inline_keyboard([
            {"text": "😈Ввести код!", "callback_data": "have_secret_code"},
            {"text": "🤷‍♂️Какой код...?", "callback_data": "have_no_secret_code"}
        ])
    )
    await call.answer()


@dp.callback_query_handler(text="have_secret_code", state=Registration.wait_role)
@dp.callback_query_handler(text="to_wait_secret_code", state=Registration)
async def wait_secret_code(call: CallbackQuery):
    await Registration.wait_secret_code.set()
    await call.message.edit_text(
        text=f"Введите секретный код",
        reply_markup=generate_inline_keyboard([
            {"text": "На самом деле не знаю😬", "callback_data": "to_wait_role"}
        ])
    )
    await call.answer()


@dp.callback_query_handler(text="have_no_secret_code", state=Registration)
async def wait_secret_code(call: CallbackQuery):
    await call.message.edit_text(
        "Обратитесь в поддержку.\n"
        "Если оказались здесь по ошибке, то выберите другую роль!",
        reply_markup=generate_inline_keyboard([
            {"text": "Выбрать другую роль", "callback_data": "to_wait_role"}
        ])
    )
    await call.answer()


@dp.message_handler(state=Registration.wait_secret_code)
async def check_secret_code(message: Message, state: FSMContext):
    user_data = await state.get_data()
    # ID сообщения "Начать регистрацию"
    call_id = user_data["call_registration_id"]
    if message.text == config.SECRET_CODE:
        await bot.edit_message_text(
            message_id=call_id,
            chat_id=message.from_user.id,
            text=f"Все четко. Танцуем💃💃💃\n"
                 f"И вводим Email:",
            reply_markup=generate_inline_keyboard([
                {"text": "Назад", "callback_data": "to_wait_role"}
            ])
        )
        await Registration.wait_email.set()
        await message.delete()
    else:
        await message.answer(
            f"Код введен неверно💀\n"
            f"Попробуйте ввсети секретный код снова.\nЕсли вы забрели сюда из любопытства, то выберите другую роль.",
            reply_markup=generate_inline_keyboard([
                {"text": "Попробовать еще раз", "callback_data": "to_wait_secret_code"},
                {"text": "Выбрать другую роль", "callback_data": "to_wait_role"}
            ])
        )


@dp.callback_query_handler(text="to_wait_email", state=Registration)
async def to_wait_email(call: CallbackQuery):
    await Registration.wait_email.set()
    await call.message.edit_text(
        f"Давайте введем Email еще раз😃",
        reply_markup=generate_inline_keyboard([
            {"text": "Назад", "callback_data": "to_wait_role"}
        ])
    )
    await call.answer()


@dp.message_handler(state=Registration.wait_email)
async def check_email(message: Message, state: FSMContext):
    await Registration.wait_email.set()
    user_data = await state.get_data()
    # ID сообщения "Начать регистрацию"
    call_id = user_data["call_registration_id"]
    if re.match("^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$", message.text):
        email_in_db = await db["users-permissions_user"].find_one({"email": message.text})
        if not email_in_db:
            await state.update_data(email=message.text.lower())
            await bot.edit_message_text(
                message_id=call_id,
                chat_id=message.from_user.id,
                text=f"Осталось совсем немного.\n"
                     f"Придумайте и введите пароль.\n",
                reply_markup=generate_inline_keyboard([
                    {"text": "Назад", "callback_data": "to_wait_email"}
                ])
            )
            await Registration.wait_password.set()
            await message.delete()

        else:
            await answer_and_delete(
                message=message,
                text="Пользователь с таким Email уже существует"
            )
    else:
        await answer_and_delete(
            message=message,
            text="Введите правильный Email"
        )


@dp.callback_query_handler(text="to_wait_password", state=Registration)
async def to_wait_password(call: CallbackQuery):
    await Registration.wait_password.set()
    await call.message.edit_text(
        f"Хорошо, давайте попробуем другой пароль😃",
        reply_markup=generate_inline_keyboard([
            {"text": "Назад", "callback_data": "to_wait_email"}
        ])
    )
    await call.answer()


@dp.message_handler(state=Registration.wait_password)
async def check_password(message: Message, state: FSMContext):
    await Registration.wait_password.set()
    user_data = await state.get_data()
    # ID сообщения "Начать регистрацию"
    call_id = user_data["call_registration_id"]
    if re.match("(?=.*[0-9])(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{6,}", message.text):
        await state.update_data(password=message.text)
        await bot.edit_message_text(
            message_id=call_id,
            chat_id=message.from_user.id,
            text=f"И, для нажедности, повторите пароль😉",
            reply_markup=generate_inline_keyboard([
                {"text": "Изменить пароль", "callback_data": "to_wait_password"}
            ])
        )
        await Registration.wait_confirm_password.set()
        await message.delete()
    else:
        await answer_and_delete(
            message=message,
            text=f"Придумайте более надежный пароль.\n\nТребования к паролю:\n"
                 f"- иметь не менее 6 символов;\n"
                 f"- начинаться с буквы;\n"
                 f"- иметь хотя бы одну цифру.",
            delay=6
        )


@dp.message_handler(state=Registration.wait_confirm_password)
async def check_confirm_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    # ID сообщения "Начать регистрацию"
    call_id = user_data["call_registration_id"]
    if not message.text == user_data["password"]:
        await answer_and_delete(
            message=message,
            text=f"Пароли не совпадают!\n"
                 f"Попробуйте повторить пароль еще раз, либо измените пароль."
        )
        return
    await Registration.wait_confirm_registration.set()
    role = await db["users-permissions_role"].find_one({"type": user_data["role"]})
    await bot.edit_message_text(
        message_id=call_id,
        chat_id=message.from_user.id,
        text=f"Пароль подтвержден!\n\n"
             f"Давайте проверим ваши данные и подтвердим регистрацию.\n\n"
             f"*Вас зовут:* {user_data['last_name']} {user_data['first_name']}\n"
             f"*Ваша роль:* {role['name']}\n"
             f"*Ваш Email:* {user_data['email']}\n"
             f"*Ваш пароль:* {user_data['password']}\n",
        parse_mode="Markdown",
        reply_markup=generate_inline_keyboard([
            {"text": "Подтвердить!", "callback_data": "confirm_registration"},
            {"text": "Назад", "callback_data": "to_wait_password"},
            {"text": "Отменить регистрацию", "callback_data": "cancel_registration"}
        ])
    )
    await message.delete()


@dp.callback_query_handler(text="confirm_registration", state=Registration.wait_confirm_registration)
async def confirm_registration(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    role = await db["users-permissions_role"].find_one({"type": user_data["role"]})
    count_users = await db["users-permissions_user"].count_documents({})
    current_value = count_users + 1
    username = f"u_{call.from_user.id}"
    encoded_password = user_data["password"].encode("utf-8")
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt(10, b'2a'))
    if hashed_password:
        new_user = User(
            full_name=f"{user_data['last_name']} {user_data['first_name']}",
            first_name=f"{user_data['first_name']}",
            last_name=f"{user_data['last_name']}",
            email=user_data['email'],
            username=username,
            password=hashed_password,
            telegram_id=call.from_user.id,
            role=role["_id"],
            all_roles=[role["_id"]],
            confirmed=True,
            blocked=False,
            provider="local"
        )
        write_user = await new_user.commit()
        if write_user.acknowledged:
            if role["type"] == "student":
                new_student = Student(
                    full_name=f"{user_data['last_name']} {user_data['first_name']}",
                    telegram_id=call.from_user.id,
                    account=write_user.inserted_id
                )
                write_student = await new_student.commit()
                if write_student.acknowledged:
                    new_user.student = write_student.inserted_id
                    await new_user.commit()
                    await call.message.edit_text(text=f"Поздравляю, {user_data['first_name']}!🎉\n"
                                                      f"Вы успешно зарегистрированы👏")
                    await state.finish()
                    await call.answer()
            if role["type"] == "parent":
                new_parent = Parent(
                    full_name=f"{user_data['last_name']} {user_data['first_name']}",
                    telegram_id=call.from_user.id,
                    account=write_user.inserted_id
                )
                write_parent = await new_parent.commit()
                if write_parent.acknowledged:
                    new_user.parent = write_parent.inserted_id
                    await new_user.commit()
                    await call.message.edit_text(text=f"Поздравляю, {user_data['first_name']}!🎉\n"
                                                      f"Вы успешно зарегистрированы👏")
                    await state.finish()
                    await call.answer()
            if role["type"] == "curator":
                new_curator = Curator(
                    full_name=f"{user_data['last_name']} {user_data['first_name']}",
                    telegram_id=call.from_user.id,
                    account=write_user.inserted_id
                )
                write_curator = await new_curator.commit()
                if write_curator.acknowledged:
                    new_user.curator = write_curator.inserted_id
                    await new_user.commit()
                    await call.message.edit_text(text=f"Поздравляю, {user_data['first_name']}!🎉\n"
                                                      f"Вы успешно зарегистрированы👏")
                    await state.finish()
                    await call.answer()
            if role["type"] == "teacher":
                new_teacher = Teacher(
                    full_name=f"{user_data['last_name']} {user_data['first_name']}",
                    telegram_id=call.from_user.id,
                    account=write_user.inserted_id
                )
                write_teacher = await new_teacher.commit()
                if write_teacher.acknowledged:
                    new_user.teacher = write_teacher.inserted_id
                    await new_user.commit()
                    await call.message.edit_text(text=f"Поздравляю, {user_data['first_name']}!🎉\n"
                                                       f"Вы успешно зарегистрированы👏")
                    await state.finish()
                    await call.answer()


@dp.message_handler(state=Registration, content_types=ContentTypes.ANY)
async def invalid_text(message: Message):
    await answer_and_delete(message=message, text=f"Я не совсем тебя понимаю...")
