from aiogram.fsm.state import State, StatesGroup

class MainState(StatesGroup):
    input_city = State()
    send_weather = State()