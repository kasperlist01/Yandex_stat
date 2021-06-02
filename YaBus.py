import pickle
import requests
from lxml import html
from key import key
import math
import re


class Schedule:
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
        with open('stations.html', "rb") as file:
            response = file.read()
        self.dc_state = self.info_stat(response)

    def info_stat(self, response):
        """Возвращает информацию о всех остановках в городе

        :param response: HTML файл всех остановок
        :return: Словарь хронящий информацию об остновках
        """
        ls_name_stations = []
        ls_id_stations = []
        ls_coordinates_stations = []
        ls_address_stations = []
        ls_info_stations = []

        HtmlTree = html.fromstring(response)
        ls_stations = HtmlTree.xpath("//div[@data-chunk='search-snippet']")
        for ost in ls_stations:
            if len(ost.xpath(".//div[@class='search-business-snippet-view__title']/text()")) != 0:
                ls_name_stations.append(ost.xpath(".//div[@class='search-business-snippet-view__title']/text()")[0])
                match = re.search(r'\d+', str(ost.xpath(".//a[@class='search-snippet-view__link-overlay']/@href")))
                ls_id_stations.append(match[0])
                ls_address_stations.append(
                    ost.xpath(".//div[@class='search-business-snippet-view__address']/text()")[0])
                ls_coordinates_stations.append(ost.xpath(".//div[@class='search-snippet-view__body "
                                                         "_type_business']/@data-coordinates"))
        for info in range(len(ls_name_stations)):
            ls_info_stations.append(
                [ls_name_stations[info], ls_id_stations[info], ls_address_stations[info],
                 ls_coordinates_stations[info][0].split(',')[0], ls_coordinates_stations[info][0].split(',')[1]])
        dc_info_stations = {info[1]: {'name': info[0], 'addr': info[2], 'coord_long': info[3], 'coord_lat': info[4]} for
                            info in ls_info_stations}
        return dc_info_stations

    def geopoz_stat(self, street):
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
        for dc in self.dc_state.items():
            if math.fabs(float(addres[0]) - float(dc[1]['coord_long'])) + math.fabs(
                    float(addres[1]) - float(dc[1]['coord_lat'])) < min_coord:
                min_coord = math.fabs(float(addres[0]) - float(dc[1]['coord_long'])) + math.fabs(
                    float(addres[1]) - float(dc[1]['coord_lat']))
                fin_id_station = dc[0]
                fin_station = dc[1]['name']
        for dc in self.dc_state.items():
            if dc[1]['name'] == fin_station:
                ls.append(dc)
        return [fin_station, fin_id_station, addres, ls]

    def dc_ls_stat(self, fin_station):
        """Метод находит ближайшие остновки.

        :param coord_stat: Название остановки
        :return: Список остановок
        """
        ls = [dc for dc in self.dc_state.items() if dc[1]['name'].lower() == fin_station]
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
    sched = Schedule()
    ls_name_and_id_coord = sched.geopoz_stat(st)
    ls_stat = sched.dc_ls_stat("Стадион имени Ленина")
    print(ls_stat, len(ls_stat))
    ls_stat = ls_name_and_id_coord[3]
    print(ls_stat, len(ls_stat))
    dc_buses = sched.cr_list_buses(ls_name_and_id_coord[1])
    ls.append(sched.dc_state[ls_name_and_id_coord[1]]['coord_long'])
    ls.append(sched.dc_state[ls_name_and_id_coord[1]]['coord_lat'])
    print(sched.find_dist(ls_name_and_id_coord[2], ls))
    # print(sched.dc_state)
    # print(ls_name_and_id_coord[0])
    # print(dc_buses)
    # cr_new_dc(sched.dc_state, cr_obsh_file())
