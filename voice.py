import difflib
from YaBus import YaBus


class Voice:
    """Класс обработки реплик пользователей.
    """

    def __init__(self):
        # Создание экземпляра класса YaBus()
        self.yabus_obj = YaBus()

    def hello(self) -> str:
        return 'Добрый день, я расскажу вам расписание транспорта Орла. Произнесите название остановки или адрес ближайшего к ней дома.'

    def routerResp(self, request):
        msg = request.json['request']['command']
        def_name = request.json.get('state', {}).get('session', {}).get('def_name')
        if def_name == 'first_msg':
            return self.stat(request)
        else:
            return self.stat(request)

    def stat(self, request):
        def_name = 'stat'
        dc = self.yabus_obj.ost_or_str(request)
        txt = self.yabus_obj.cn_ost(dc)
        return {'text_resp': txt, 'def_name': def_name}
