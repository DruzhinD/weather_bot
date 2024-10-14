class SingletonMetaclass(type):
    """является метаклассом для синглтонов"""

    #хранит ссылки на существующие объекты классов, в которых этот класс прописан как метакласс
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]