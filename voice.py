import difflib

from YaBus import Schedule


class Voice:
    """Класс обработки реплик пользователей.
    """
    def __init__(self):
        pass

    def hello(self) -> str:
        return 'Добрый день, я расскажу вам расписание транспорта Орла. Произнесите название остановки или адрес ближайшего к ней дома.'

    def routerResp(self, response):
        pass

    def ost_or_str(self, request):
        """Метод различает остановку и адрес.

        :return: Словарь {'GEO': 'адрес'} | {'BUS_STAT': 'название остановки'} | {'GEO_PREC': 'адрес'} | {'ERROR': '1'}
        """
        ls_word = request.json["request"]["nlu"]["tokens"]
        with open('stations.html', "rb") as file:
            response = file.read()
        sched = Schedule()
        dc = sched.info_stat(response)
        dc_ans = {}

        if ('рядом' in ls_word) or ('возле' in ls_word) or ('около' in ls_word):
            dc_ans = {'GEO_PREC': ' '.join(ls_word).lower()}

        if len(dc_ans) == 0:
            if len(request.json.get('request', '').get('nlu', '').get('entities', '')) != 0:
                for st in request.json.get('request', '').get('nlu', '').get('entities', ''):
                    if st['type'] == 'YANDEX.GEO':
                        if len(st.get('value', '').get('house_number', '')) != 0:
                            dc_ans = {'GEO': ' '.join(ls_word).lower()}

        if len(dc_ans) == 0:
            ls_stat = [el[1]['name'].lower() for el in dc.items()]
            ost = difflib.get_close_matches(' '.join(ls_word).lower(), ls_stat, n=1, cutoff=0.7)
            dc_ans = {'BUS_STAT': ost[0]} if len(ost) != 0 else {'ERROR': '1'}

        """dc = ost_or_str(request)
        if cn_ost(dc)[0] == 'ERROR':
            response["response"][
                "text"] = 'Упс, извините, произнесите ещё раз, название остановки или адрес ближайшего к ней дома.'
        elif int(cn_ost(dc)[1]) == 1:
            response["response"]["text"] = 'Вы выбрали остановку ' + cn_ost(dc)[
                0]
        else:
            response["response"]["text"] = 'Вы выбрали остановку ' + cn_ost(dc)[
                0] + ', но остановок с таким названием найдено ' + cn_ost(dc)[1]"""

        return dc_ans

    def cn_ost(self, dc_info):
        """Метод считает кол-во остановок.

        :param dc_info: Словарь {'GEO': 'адрес'} | {'BUS_STAT': 'название остановки'} | {'GEO_PREC': 'адрес'} | {'ERROR': '1'}
        :return: (название остановки, кол-во остановок)
        """
        sched = Schedule()
        ls_stat = []

        if dc_info.get('GEO', ''):
            ls_name_and_id_coord = sched.geopoz_stat(dc_info['GEO']) if 'орел' in dc_info['GEO'] else sched.geopoz_stat(
                'орел ' + dc_info['GEO'])
            ls_stat = ls_name_and_id_coord[3]
        elif dc_info.get('BUS_STAT', ''):
            ls_stat = sched.dc_ls_stat(dc_info['BUS_STAT'])
        elif dc_info.get('ERROR', ''):
            ls_stat = [('0', {'name': 'ERROR'})]
        elif dc_info.get('GEO_PREC', ''):
            ls_stat = [('0', {'name': dc_info['GEO_PREC']})]
        print(ls_stat)
        return ls_stat[0][1]['name'], str(len(ls_stat))
