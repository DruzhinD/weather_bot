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
    await state.set_state(MainState.input_city)  
    await request_input_city(message.bot, message.from_user.id, state)


from aiogram import Bot
async def request_input_city(bot: Bot, user_id: int, state: FSMContext):
    """Отправка запроса на ввод города"""
    msg = "Введите название города"
    await bot.send_message(user_id, msg)


@main_router.message(MainState.input_city)
async def send_weather_type_request(message: ait.Message, state: FSMContext):
    """Запрос на выбор типа погоды: прогноз или текущая погода"""
    #проверка на существование города
    weather = OpenWeather(message.text)
    result = await is_city_exists(weather)
    if not result:
        msg = 'Город не найден'
        await message.answer(msg)
        await state.set_state(MainState.input_city)
        await request_input_city(message.bot, message.from_user.id, state)
        return
    
    #сохраняем данные
    await state.update_data(weather = weather)

    keyboard = ait.InlineKeyboardMarkup(inline_keyboard=[
        [ait.InlineKeyboardButton(text='Текущая погода', callback_data='current'),
         ait.InlineKeyboardButton(text='Прогноз на 5 дней', callback_data='forecast')]
    ])
    msg = 'Выберите нужный пункт'
    await message.answer(msg, reply_markup=keyboard)
    await state.set_state(MainState.select_weather_type)


async def is_city_exists(weather: OpenWeather) -> bool:
    """проверка на корректность ввода города"""
    result = await weather.is_city_exists()
    return result


@main_router.callback_query(F.data == 'current' and MainState.select_weather_type)
async def send_weather_data(callback: ait.CallbackQuery, state: FSMContext):
    """Если город введен верно, то отправляем данные о погоде"""
    await callback.message.edit_reply_markup()
    state_data = await state.get_data()
    weather: OpenWeather = state_data["weather"]
    data = await weather.current_weather()
    #str возвращается, если произошла ошибка
    if isinstance(data, str):   
        await callback.bot.send_message(data)
        await request_input_city(callback.bot, callback.from_user.id, state)
        await state.clear()
        return

    msg = f'Погода в городе {weather.city}' + '\n'
    for key, value in data.items():
        msg += f'{key}:\t{value}' + '\n'
    
    keyboard = ait.InlineKeyboardMarkup(inline_keyboard=[[
        ait.InlineKeyboardButton(text='Сменить город', callback_data='change')]])
    await callback.bot.send_message(callback.from_user.id, msg, reply_markup=keyboard)
    await state.set_state(MainState.send_weather)

#TODO
@main_router.callback_query(MainState.select_weather_type and F.data == 'forecast')
async def send_forecast_data(callback: ait.CallbackQuery, state: FSMContext):
    """прогноз на несколько дней"""
    await callback.message.edit_reply_markup()
    state_data = await state.get_data()
    weather: OpenWeather = state_data["weather"]
    data = await weather.current_weather()
    #str возвращается, если произошла ошибка
    if isinstance(data, str):   
        await callback.bot.send_message(data)
        await request_input_city(callback.bot, callback.from_user.id, state)
        await state.clear()
        return

    msg = f'Погода в городе {weather.city}' + '\n'
    for date, weather in data.items():
        msg += date + '\n'
        for key, value in weather.items():
            msg += '\t' + f'{key}:\t{value}' + '\n'
        msg += '\n'
    
    keyboard = ait.InlineKeyboardMarkup(inline_keyboard=[[
        ait.InlineKeyboardButton(text='Сменить город', callback_data='change')]])
    await callback.bot.send_message(msg, reply_markup=keyboard)
    await state.set_state(MainState.send_weather)


@main_router.callback_query(F.data == 'change' and MainState.send_weather)
async def change_city(callback: ait.CallbackQuery, state: FSMContext):
    """Сменить город"""
    #удаляем inline клавиатуру
    await callback.message.edit_reply_markup()
    await state.clear()
    await state.set_state(MainState.input_city)
    await request_input_city(callback.bot, callback.from_user.id, state)