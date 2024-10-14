import json

from common.singleton_metaclass import SingletonMetaclass


class Config(metaclass=SingletonMetaclass):
    """Класс конфигурации. Реализует синглтон"""
    def __init__(self) -> None:
        self.save_directory: str = "data"
        self.config_path: str = f'{self.save_directory}\\config.json'
        
        self.__read_config()
    

    def __read_config(self):
        """Чтение данных конфигурации"""
        with open(self.config_path, 'r', encoding='utf-8') as file:
            data = json.loads(
                ''.join(file.readlines()))
        #добавляем новые атрибуты в конфиг из файла конфига
        self.__dict__.update(data)