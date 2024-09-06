from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(storage=MemoryStorage())

button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
button_3 = KeyboardButton(text='Купить')
kb = ReplyKeyboardMarkup(keyboard=[[button_1, button_2], [button_3]], resize_keyboard=True)
button_4 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_5 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')

inline_kb = InlineKeyboardMarkup(inline_keyboard=[[button_4, button_5]], resize_keyboard=True)

product_name_list = ['Omega-3', 'Vitamins complex', 'PRO BIOTICS', 'Turbo Tea']
description_list = ['Витаминки с Омегой-3, типа для веганов',
                    'Витаминки A, C, E',
                    'Живые микроорганизмы, приносящие пользу хозяину',
                    'Слабительное под видом чая']
inline_kb_2 = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text=product_name_list[0], callback_data='product_buying'),
    InlineKeyboardButton(text=product_name_list[1], callback_data='product_buying'),
    InlineKeyboardButton(text=product_name_list[2], callback_data='product_buying'),
    InlineKeyboardButton(text=product_name_list[3], callback_data='product_buying')
    ]]
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message(Command("start"))
async def start_message(message: types.Message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.")
    await message.answer("Чтобы посчитать калории нажмите Рассчитать", reply_markup=kb)


@dp.message(F.text == "Рассчитать")
async def main_menu(message: types.Message):
    await message.answer(text='Выберите опцию:', reply_markup=inline_kb)


@dp.message(F.text == "Купить")
async def get_buying_list(message: types.Message):
    for i in range(4):
        await message.answer(text=f'{product_name_list[i]} | {description_list[i]} | Цена: {(i + 1) * 100}$')
        with open('IMG_1.jpg', 'rb'):
            await message.answer_photo(FSInputFile(f'IMG_{i + 1}.jpg'))
    await message.answer(text='Выберите продукт для покупки:', reply_markup=inline_kb_2)


@dp.callback_query(F.data == "product_buying")
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query(F.data == "formulas")
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer('10 x вес(кг) + 6.25 x рост(см) - 5 x возраст(лет) + 5', reply_markup=kb)
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
        await message.answer(f"Вам необходимо {calories} килокалорий в сутки ", reply_markup=kb)
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
    asyncio.run(main())
