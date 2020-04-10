class AppSettings:
    def __init__(self):
        """Инициализация объекта с конфигурацией приложения"""

        self.__dict__.update(
            RESTPLUS_MASK_SWAGGER=False
        )
