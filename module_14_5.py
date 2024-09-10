from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import crud_functions

api = ''
bot = Bot(token=api)
dp = Dispatcher(storage=MemoryStorage())

button_reg = KeyboardButton(text='Регистрация')
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
button_3 = KeyboardButton(text='Купить')
reply_kb = ReplyKeyboardMarkup(keyboard=[[button_reg], [button_1, button_2], [button_3]], resize_keyboard=True)

button_4 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_5 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
options_kb = InlineKeyboardMarkup(inline_keyboard=[[button_4, button_5]], resize_keyboard=True)

buy_kb = InlineKeyboardMarkup(inline_keyboard=[], resize_keyboard=True)
builder = InlineKeyboardBuilder()
entries = crud_functions.get_all_products()
for entry in entries:
    builder.add(InlineKeyboardButton(text=entry[1], callback_data='product_buying'))


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State('1000')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message(Command("start"))
async def start_message(message: types.Message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=reply_kb)


@dp.message(F.text == "Регистрация")
async def sing_up(message: types.Message, state: FSMContext):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await state.set_state(RegistrationState.username)


@dp.message(RegistrationState.username)
async def set_username(message: types.Message, state: FSMContext):
    if crud_functions.is_included(message.text):
        await message.answer(text='Пользователь существует, введите другое имя')
        await state.set_state(RegistrationState.username)
    else:
        await message.answer("Введите свой email:")
        await state.update_data(username=message.text)
        await state.set_state(RegistrationState.email)


@dp.message(RegistrationState.email)
async def set_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer(text='Введите свой возраст:')
    await state.set_state(RegistrationState.age)


@dp.message(RegistrationState.age)
async def set_email(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    data = await state.get_data()
    crud_functions.add_user(data['username'], data['email'], data['age'])
    await message.answer('Регистрация прошла успешна', reply_markup=reply_kb)
    await state.clear()


@dp.message(F.text == "Рассчитать")
async def main_menu(message: types.Message):
    await message.answer(text='Выберите опцию:', reply_markup=options_kb)


@dp.message(F.text == "Купить")
async def get_buying_list(message: types.Message):
    products = crud_functions.get_all_products()
    for product in products:
        await message.answer(text=f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}$')
        with open('IMG_1.jpg', 'rb'):
            await message.answer_photo(FSInputFile(f'IMG_{product[0]}.jpg'))
    await message.answer(text='Выберите продукт для покупки:',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@dp.callback_query(F.data == "product_buying")
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query(F.data == "formulas")
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer('10 x вес(кг) + 6.25 x рост(см) - 5 x возраст(лет) + 5', reply_markup=reply_kb)
    await call.answer()


@dp.callback_query(F.data == "calories")
async def set_age(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(text="Введите свой возраст:")
    await state.set_state(UserState.age)
    await call.answer()


@dp.message(UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    try:
        await state.update_data(age=float(message.text))
        await message.answer(text="Введите свой рост в см:")
        await state.set_state(UserState.growth)
    except ValueError:
        await message.answer("Так не годится. Давай по новой")
        await state.clear()
        await start_message(message)


@dp.message(UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    try:
        await state.update_data(growth=float(message.text))
        await message.answer(text="Введите свой вес в кг:")
        await state.set_state(UserState.weight)
    except ValueError:
        await message.answer("Так не годится. Давай по новой")
        await state.clear()
        await start_message(message)


@dp.message(UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    try:
        await state.update_data(weight=float(message.text))
        data = await state.get_data()
        calories = 10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] + 5
        await message.answer(f"Вам необходимо {calories} килокалорий в сутки ", reply_markup=reply_kb)
    except ValueError:
        await message.answer("Так не годится. Давай по новой")
        await start_message(message)
    finally:
        await state.clear()


@dp.message()
async def other_message(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    crud_functions.initiate_db()
    asyncio.run(main())
