from aiogram import F, Router #magic команда и роутер
from aiogram.filters import Command, CommandStart #команда
from aiogram.fsm.context import FSMContext #контекст
import aiogram.types as ait #сообщения, query, клавиатура и т.п.
from aiogram.enums.parse_mode import ParseMode #перечисление для типа разметки текста

from chatbot.scenario import MainState
from model.openweather import OpenWeather

main_router = Router()

@main_router.message(CommandStart())
async def program_start(message: ait.Message, state: FSMContext):
    respond_msg = ("Приветствую!\n" +
        "Я могу узнать погоду в любом городе мира!\n")
    await message.answer(respond_msg)
    await state.clear()
    await state.set_state(MainState.input_city)  
    await request_input_city(message.bot, message.from_user.id, state)


from aiogram import Bot
async def request_input_city(bot: Bot, user_id: int, state: FSMContext):
    """Отправка запроса на ввод города"""
    msg = "Введите название города"
    await bot.send_message(user_id, msg)


@main_router.message(MainState.input_city)
async def send_weather_data(message: ait.Message, state: FSMContext):
    """Если город введен верно, то отправляем данные о погоде"""
    weather: OpenWeather = OpenWeather(message.text)
    data = await weather.current_weather()
    #str возвращается, если произошла ошибка
    if isinstance(data, str):   
        await message.bot.send_message(data)
        await request_input_city(message.bot, message.from_user.id, state)
        await state.set_state(MainState.input_city)
        return

    msg = f'Погода в городе {weather.city}' + '\n'
    for key, value in data.items():
        msg += f'{key}:\t{value}' + '\n'
    
    keyboard = ait.InlineKeyboardMarkup(inline_keyboard=[[
        ait.InlineKeyboardButton(text='Сменить город', callback_data='change')]])
    await message.bot.send_message(message.from_user.id, msg, reply_markup=keyboard)
    await state.set_state(MainState.send_weather)


@main_router.callback_query(F.data == 'change' and MainState.send_weather)
async def change_city(callback: ait.CallbackQuery, state: FSMContext):
    """Сменить город"""
    #удаляем inline клавиатуру
    await callback.message.edit_reply_markup()
    await state.clear()
    await state.set_state(MainState.input_city)
    await request_input_city(callback.bot, callback.from_user.id, state)