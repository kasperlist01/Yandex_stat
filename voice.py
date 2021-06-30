import difflib
from YaBus import YaBus


class Voice:
    """Класс обработки реплик пользователей.
    """

    def __init__(self):
        # Создание экземпляра класса YaBus()
        self.yabus_obj = YaBus()

    def hello(self) -> str:
        return 'Добрый день, я расскажу вам расписание транспорта Орла. Скажите название остановки или адрес ' \
               'ближайшего к ней дома. '

    def routerResp(self, request):
        def_name = request.json.get('state', {}).get('session', {}).get('def_name')
        if def_name == 'first_msg':
            return self.stat_ls(request)
        elif def_name == 'stat_ls':
            return self.recong_org(request)

    def stat_ls(self, request):
        def_name = 'stat_ls'
        dc = self.yabus_obj.ost_or_str(request)
        txt = self.yabus_obj.cn_ost(dc)
        return {'text_resp': txt, 'def_name': def_name}

    def recong_org(self, request):
        def_name = 'recong_org'
        msg = request.json['request']['command']
        txt = self.yabus_obj.recong_org(msg)
        return {'text_resp': txt, 'def_name': def_name}
