from YaBus import YaBus


class Voice:
    """Класс обработки реплик пользователей.
    """

    def __init__(self):
        # Создание экземпляра класса YaBus()
        self.yabus_obj = YaBus()
        self.cn_state = 0

    def first_mess(self) -> str:
        """Метод говорит первую реплику Алисы.

        :return: Реплика Алисы.
        """
        return 'Добрый день, я расскажу вам расписание транспорта Орла. Скажите название остановки или адрес ' \
               'ближайшего к ней дома.'

    def routerResp(self, request):
        """Метод реализует ветвление.

        :param request: Словарь приходящий от пользователя.
        :return: Нужная функция
        """
        def_name = request.json.get('state', {}).get('session', {}).get('def_name')
        if def_name == 'first_msg':
            return self.stat_ls(request)
        elif def_name == 'stat_ls' and self.cn_state != 1:
            return self.recong_org(request)
        elif def_name == 'stat_ls' and self.cn_state == 1:
            return self.yes_no(request)
        elif def_name == 'recong_org':
            return self.yes_no(request)

    def stat_ls(self, request):
        """Метод озвучивает остановки и привязанные к ним организации.

        :param request: Словарь приходящий от пользователя.
        :return: Словарь {'text_resp': реплика Алисы, 'def_name': название функции}
        """
        def_name = 'stat_ls'
        dc = self.yabus_obj.ost_or_str(request)
        txt = self.yabus_obj.cn_ost(dc)
        self.cn_state = self.yabus_obj.cn_state
        if dc.get('ERROR'):
            txt = 'Упс, извините, произнесите ещё раз, название остановки или адрес ближайшиго к ней дома'
            def_name = 'first_msg'
        return {'text_resp': txt, 'def_name': def_name}

    def recong_org(self, request):
        """Метод озвучивает финальную остановку пользователя и привязаннуу к нёй организацию.

        :param request: Словарь приходящий от пользователя.
        :return: Словарь {'text_resp': реплика Алисы, 'def_name': название функции}
        """
        def_name = 'recong_org'
        msg = request.json['request']['command']
        txt = self.yabus_obj.recong_org(msg)
        return {'text_resp': txt, 'def_name': def_name}

    def yes_no(self, request):
        """Метод обрабатывает вопросы да/нет.

        :param request: Словарь приходящий от пользователя.
        :return: Словарь {'text_resp': реплика Алисы, 'def_name': название функции}
        """
        def_name = ''
        txt = ''
        if request.json['request']['nlu']['tokens'][0] == 'да':
            txt = 'Хотите услышать какой транспорт прибудет на остановку в ближайшее время?'
        else:
            txt = 'Упс, извините, произнесите ещё раз, название остановки или адрес ближайшиго к ней дома'
            def_name = 'first_msg'
        return {'text_resp': txt, 'def_name': def_name}
