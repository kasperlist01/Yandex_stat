import difflib
import pickle
from pprint import pprint

import requests
from lxml import html
from key import key
import math


class YaBus:
    """
    Класс нужен для получения информации об транспорте
    -------------------------
    Метод geopoz_stat() нужен для нахожения ближайшей остновки.
    Вызывается с параметром street - адрес пользователя.
    Возвращает список состоящий из названия остановки и её id.
    -------------------------
    Метод cr_list_buses нужен отображения маршруток, которые подходят к остановке.
    Вызывается с параметром fin_id_station - название остановки.
    Возвращает словарь состоящий из номера маршрутки и времени её прибытия.
    """

    def __init__(self):
        with open('dc_org_stat.pickle', 'rb') as f:
            self.dc_info_state = pickle.load(f)
        with open('dc_full_org.pickle', 'rb') as f:
            self.dc_info_org = pickle.load(f)
        self.ls_state = []

    def find_stat(self, street):
        """Метод находит ближайшую остновку.

        :param street: Адрес пользователя.
        :return: Список состоящий из названия остановки и её id.
        """
        ls = []
        street = '+'.join(street.split())
        dc_res = requests.get(
            f'https://geocode-maps.yandex.ru/1.x/?apikey={key}&format=json'
            f'&geocode={street}').json()
        addres = dc_res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        addres = addres.split()
        fin_id_station = ''
        fin_station = ''
        min_coord = 99
        for dc in self.dc_info_state.items():
            if math.fabs(float(addres[0]) - float(dc[1]['coord_long'])) + math.fabs(
                    float(addres[1]) - float(dc[1]['coord_lat'])) < min_coord:
                min_coord = math.fabs(float(addres[0]) - float(dc[1]['coord_long'])) + math.fabs(
                    float(addres[1]) - float(dc[1]['coord_lat']))
                fin_id_station = dc[0]
                fin_station = dc[1]['name']
        for dc in self.dc_info_state.items():
            if dc[1]['name'] == fin_station:
                ls.append(dc)
        return [fin_station, fin_id_station, addres, ls]

    def find_oll_min_stat(self, fin_station):
        """Метод находит ближайшие остновки.

        :param coord_stat: Название остановки
        :return: Список остановок
        """
        ls = [dc for dc in self.dc_info_state.items() if dc[1]['name'].lower() == fin_station]
        return ls

    def find_dist(self, coord_pl, coord_stat):
        """Метод находит расстояние до ближайшей остновки.

        :param coord_pl: Координаты пользователя.
        :param coord_stat: Координаты остановки
        :return: Дистанцию в метрах.
        """
        distance = math.sqrt(
            (float(coord_pl[0]) - float(coord_stat[0])) ** 2 + ((float(coord_pl[1]) - float(coord_stat[1])) ** 2))
        distance = str(distance)[2:7]
        while distance[0] == '0':
            distance = distance[1:]
        return (distance)

    def cr_list_buses(self, fin_id_station):
        """Метод отображает маршрутоки, которые подходят к остановке.

        :param fin_id_station: Название остановки
        :return: Словарь состоящий из номера маршрутки и времени её прибытия.
        """
        response = requests.get(f'https://yandex.ru/maps/10/orel/stops/{fin_id_station}')
        HtmlTree = html.fromstring(response.content)
        ls_blocks = HtmlTree.xpath("//div[@class='masstransit-vehicle-snippet-view__row']")
        ls_name_mr = []
        ls_time_mr = []
        for block in ls_blocks:
            ls = block.xpath("./*/a[@class='masstransit-vehicle-snippet-view__name']/@title")[0].split()
            del ls[-1]
            del ls[-1]
            ls_name_mr.append(' '.join(ls))
            ls_time_mr.append(block.xpath(".//span[@class='masstransit-prognoses-view__title-text']/text()"))
        dc_mr = dict(zip(ls_name_mr, ls_time_mr))
        dc_mr = {key: val[0] for key, val in dc_mr.items() if len(val) != 0 and ':' not in val[0]}
        return dc_mr

    def ost_or_str(self, request):
        """Метод различает остановку и адрес.

        :return: Словарь {'GEO': 'адрес'} | {'BUS_STAT': 'название остановки'} | {'GEO_PREC': 'адрес'} | {'ERROR': '1'}
        """
        ls_word = request.json["request"]["nlu"]["tokens"]
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
            ls_stat = [el[1]['name'].lower() for el in self.dc_info_state.items()]
            ost = difflib.get_close_matches(' '.join(ls_word).lower(), ls_stat, n=1, cutoff=0.7)
            dc_ans = {'BUS_STAT': ost[0]} if len(ost) != 0 else {'ERROR': '1'}
        return dc_ans

    def find_id_org(self):
        ls_org_user = []
        for cn in range(len(self.ls_state)):
            for el in self.ls_state[cn][1].items():
                if el[0] == 'org':
                    ls_org_user.append(el[1])
        return ls_org_user

    def cn_ost(self, dc_info):
        """Метод считает кол-во остановок.

        :param dc_info: Словарь {'GEO': 'адрес'} | {'BUS_STAT': 'название остановки'} | {'GEO_PREC': 'адрес'} | {'ERROR': '1'}
        :return: Реплику пользователю
        """
        ls_org = []
        with open('dc_full_org.pickle', 'rb') as f:
            dc_org = pickle.load(f)

        if dc_info.get('GEO', ''):
            ls_name_and_id_coord = self.find_stat(dc_info['GEO']) if 'орел' in dc_info['GEO'] else self.find_stat(
                'орел ' + dc_info['GEO'])
            self.ls_state = ls_name_and_id_coord[3]
        elif dc_info.get('BUS_STAT', ''):
            self.ls_state = self.find_oll_min_stat(dc_info['BUS_STAT'])
        elif dc_info.get('ERROR', ''):
            self.ls_state = [('0', {'name': 'ERROR'})]
        elif dc_info.get('GEO_PREC', ''):
            self.ls_state = [('0', {'name': dc_info['GEO_PREC']})]

        if self.ls_state[0][1]['name'] == 'ERROR':
            ans = 'Упс, извините, произнесите ещё раз, название остановки или адрес ближайшего к ней дома.'
        elif len(self.ls_state) == 1:
            dc = dc_org[self.dc_info_state[str(self.ls_state[0][0])]['org']]
            category = dc['category'] if bool(dc.get('category', None)) else ''
            title = dc['title'] if bool(dc.get('title', None)) else ''
            ans = 'Ближайшая остановка по вашему адресу ' + self.ls_state[0][1][
                'name'] + ' рядом с ' + category + ' ' + title
            ls_org.append(category + ' ' + title)
            print(self.ls_state)
        else:
            stat_v = 'остановок' if len(self.ls_state) >= 5 else 'остановки'
            ans = f'Я нашла {len(self.ls_state)} {stat_v} с названием, {self.ls_state[0][1]["name"]}'
            for cn in range(len(self.ls_state)):
                dc = dc_org[self.dc_info_state[str(self.ls_state[cn][0])]["org"]]
                category = dc['category'] if bool(dc.get('category', None)) else ''
                title = dc['title'] if bool(dc.get('title', None)) else ''
                if cn == 0:
                    ans += f'. Первая остановка находится рядом с {category} {title}'
                    ls_org.append(category + ' ' + title)
                elif cn == 1:
                    ans += f'. Вторая остановка находится около {category} {title}'
                    ls_org.append(category + ' ' + title)
                elif cn == 2:
                    ans += f'. Третья остановка находится рядом с {category} {title}'
                    ls_org.append(category + ' ' + title)
                elif cn == 3:
                    ans += f'. Четвертая остановка находится около {category} {title}'
                    ls_org.append(category + ' ' + title)
                elif cn == 4:
                    ans += f'. Пятая остановка находится возле {category} {title}'
                    ls_org.append(category + ' ' + title)
                elif cn == 5:
                    ans += f'. Шестая остановка находится рядом с {category} {title}'
                    ls_org.append(category + ' ' + title)
            ans += '. Возле чего находится нужная вам остановка?'
        ans = ans.replace('  ', ' ')
        return ans

    def recong_org(self, ans_pl):
        ls_org = []
        ls_id_org = self.find_id_org()
        for el in ls_id_org:
            dc = self.dc_info_org[str(el)]
            category = dc['category'] if bool(dc.get('category', None)) else ''
            title = dc['title'] if bool(dc.get('title', None)) else ''
            ls_org.append(category + ' ' + title)
        org = difflib.get_close_matches(ans_pl, ls_org, cutoff=0.5, n=1)[0]
        ans = f'Вы выбрали остановку {self.ls_state[0][1]["name"]} возле {org}, я правильно поняла?'
        return ans


# Обновляет список заведений
def cr_obsh_file():
    with open('dc_apteka.pickle', 'rb') as f:
        dc_obj = pickle.load(f)
    with open('dc_kafe.pickle', 'rb') as f:
        dc_obj.update(pickle.load(f))
    with open('dc_shop.pickle', 'rb') as f:
        dc_obj.update(pickle.load(f))
    for dc in dc_obj.items():
        dc[1]['coordinates'] = dc[1]['coordinates'].split(',')

    with open('dc_org.pickle', 'wb') as f:
        pickle.dump(dc_obj, f)
    return dc_obj


# Привязывает заведение к отстановке
"""def cr_new_dc(dc_info_stations, dc_obj):
    min_station = ''
    dc_old = dc_info_stations.copy()
    min_coord = 99
    for dc2 in dc_old.items():
        for dc1 in dc_obj.items():
            if math.fabs(float(dc1[1]['coordinates'][0]) - float(dc2[1]['coord_long'])) + math.fabs(
                    float(dc1[1]['coordinates'][1]) - float(dc2[1]['coord_lat'])) < min_coord:
                min_coord = math.fabs(float(dc1[1]['coordinates'][0]) - float(dc2[1]['coord_long'])) + math.fabs(
                    float(dc1[1]['coordinates'][1]) - float(dc2[1]['coord_lat']))
                min_station = dc2[1]['name']
        print(dc1[1]['title'], min_station)
        # dc2[1]['coord_long'], dc2[1]['coord_lat'] = 100, 100
        min_coord = 99"""

if __name__ == '__main__':
    # st = input()
    ls = []
    st = 'Орел спасибо'
    sched = YaBus()
    ls_name_and_id_coord = sched.find_stat(st)
    ls_stat = sched.find_oll_min_stat("Стадион имени Ленина")
    print(ls_stat, len(ls_stat))
    ls_stat = ls_name_and_id_coord[3]
    print(ls_stat, len(ls_stat))
    # print(sched.dc_state)
    # print(ls_name_and_id_coord[0])
    # print(dc_buses)
    # cr_new_dc(sched.dc_state, cr_obsh_file())
