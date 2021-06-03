import difflib
from YaBus import YaBus


class Voice:
    """Класс обработки реплик пользователей.
    """
    def __init__(self):
    # Создание экземпляра класса YaBus()
        yabus = YaBus()

    def hello(self) -> str:
        return 'Добрый день, я расскажу вам расписание транспорта Орла. Произнесите название остановки или адрес ближайшего к ней дома.'

    def routerResp(self, response):
        msg = response.json['request']['command']
        def_name = response.json.get('state', {}).get('session', {}).get('def_name')
