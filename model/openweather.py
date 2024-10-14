import aiohttp
from common.config import Config
from typing import Union
import math #для вычисления направления ветра
from datetime import datetime

class OpenWeather:
    """Класс, работающий с api openweather"""
    
    def __init__(self, city: str) -> None:
        config = Config()
        self.city: str = city #город
        self.api_key: str = config.api_key
        self.base_url = config.base_url
        self.default_params: dict = config.openweather_default_params
    
    async def current_weather(self):
        """Получить информацию о текущей погоде в конкретном городе"""
        url_postfix = 'weather'
        params = {}
        params['q'] = self.city
        params["appid"] = self.api_key
        params.update(self.default_params)
        
        #отправка запроса
        data = await self.send_request(params, url_postfix)
        #int возвращается, если запрос не был выполнен
        if isinstance(data, int):
            if data == 91:
                return "город не найден"
            else:
                return "Произошла неизвестная ошибка. Попробуйте позже."
        #обработка результата
        return_data = OpenWeather.__parse_weather_unit(data)
        return return_data


    async def get_forecast(self, count: int) -> dict:
        """Получение прогноза погоды на несколько временных интервалов. <br>
        Возврат: словарь, в котором ключ - дата, значение - данные о погоде"""
        url_postfix = 'forecast'
        params = {}
        params['q'] = self.city
        params["appid"] = self.api_key
        params["cnt"] = count
        params.update(self.default_params)

        #отправка запроса
        data = await self.send_request(params, url_postfix)
        #int возвращается, если запрос не был выполнен
        if isinstance(data, int):
            if data == 91:
                return "город не найден"
            else:
                return "Произошла неизвестная ошибка. Попробуйте позже."
        
        return_data_list = {}
        #проход по временным интервалам
        for interval in data["list"]:
            date_key = datetime.fromtimestamp(int(interval["dt"])).strftime('%d-%m-%y %H:%M:%S')
            weather_data = OpenWeather.__parse_weather_unit(interval)
            return_data_list.update({date_key: weather_data})
        
        return return_data_list



    def __parse_weather_unit(data: dict) -> dict:
        """парсит данные о погоде за конкретную единицу времени"""
        #добавляем в возвращаемый словарь необходимые поля
        return_data = {}
        #погодные условия
        return_data.update({'условия': data['weather'][0]['description']})
        #ветер
        wind_direction = OpenWeather.wind_degree_converter(data['wind']['deg'])
        wind_description = f'{wind_direction} {data["wind"]["speed"]} м/с'
        
        return_data.update({"ветер": wind_description})
        #температура
        temp_fact = str(data["main"]["temp"]) + u"\u00b0" + 'C'
        temp_feels_like = str(data["main"]["feels_like"]) + u"\u00b0" + 'C'
        return_data.update({"температура": temp_fact,"по ощущениям":temp_feels_like})
        #влажность
        humidity = str(data["main"]["humidity"]) + "%"
        return_data.update({"влажность": humidity})
        return return_data


    async def send_request(self, params, url_postfix) -> Union[int, dict]:
        """Отправка запроса на сервер Openweather"""
        async with aiohttp.ClientSession() as session:
            response = await session.get(self.base_url + url_postfix, params=params)
            #в случае ошибки возвращаем None
            if response.status == 404: #город не найден
                return 90
            elif response.status != 200: #иная ошибка
                return 91
            #status == 200
            data = await response.json()
            return data
    

    def wind_degree_converter(deg: int) -> str:
        """Преобразует градусы в направление ветра"""
        if not isinstance(deg, int):
            return "Н/Д"
        wind_dict = {
            0: "северный", 1: "северо-восточный",
            2: "восточный", 3: "юго-восточный",
            4: "южный", 5: "юго-западный",
            6: "западный", 7: "северо-западный",
            8: "северный"
        }

        wind_key = round(deg/45)
        if not wind_key in wind_dict.keys():
            return "Н/Д"
        return wind_dict[wind_key]


    async def is_city_exists(self) -> bool:
        """проверка на существование города"""
        url_postfix = 'weather'
        params = {}
        params['q'] = self.city
        params["appid"] = self.api_key
        params.update(self.default_params)
        result = await self.send_request(params, url_postfix)
        if result == None:
            return False
        return True