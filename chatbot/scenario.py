from aiogram.fsm.state import State, StatesGroup

class MainState(StatesGroup):
    input_city = State()
    select_weather_type = State()
    """Состояние выбора: прогноз или текущая погода"""
    send_weather = State()