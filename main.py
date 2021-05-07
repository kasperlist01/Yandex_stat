import requests
from lxml import html
import math
import re


def buse(fin_id_station):
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


def geopoz_pl(street, dc_info_stations):
    street = '+'.join(street.split())
    dc_res = requests.get(f'https://geocode-maps.yandex.ru/1.x/?apikey=f390a15e-4214-4c6c-afef-0021ee3458e0&format=json'
                          f'&geocode={street}').json()
    addres = dc_res['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    addres = addres.split()
    fin_id_station = ''
    fin_station = ''
    min_coord = 99
    for dc in dc_info_stations.items():
        if math.fabs(float(addres[0]) - float(dc[1]['coord_long'])) + math.fabs(
                float(addres[1]) - float(dc[1]['coord_lat'])) < min_coord:
            min_coord = math.fabs(float(addres[0]) - float(dc[1]['coord_long'])) + math.fabs(
                float(addres[1]) - float(dc[1]['coord_lat']))
            fin_id_station = dc[0]
            fin_station = dc[1]['name']
    print(fin_station)
    return [fin_station, fin_id_station]


def info_stat():
    ls_name_stations = []
    ls_id_stations = []
    ls_coordinates_stations = []
    ls_address_stations = []
    ls_info_stations = []

    with open('stations.html', "rb") as file:
        res = file.read()
    HtmlTree = html.fromstring(res)
    ls_stations = HtmlTree.xpath("//div[@data-chunk='search-snippet']")
    for ost in ls_stations:
        if len(ost.xpath(".//div[@class='search-business-snippet-view__title']/text()")) != 0:
            ls_name_stations.append(ost.xpath(".//div[@class='search-business-snippet-view__title']/text()")[0])
            match = re.search(r'\d+', str(ost.xpath(".//a[@class='search-snippet-view__link-overlay']/@href")))
            ls_id_stations.append(match[0])
            ls_address_stations.append(ost.xpath(".//div[@class='search-business-snippet-view__address']/text()")[0])
            ls_coordinates_stations.append(ost.xpath(".//div[@class='search-snippet-view__body "
                                                     "_type_business']/@data-coordinates"))
    for info in range(len(ls_name_stations)):
        ls_info_stations.append(
            [ls_name_stations[info], ls_id_stations[info], ls_address_stations[info],
             ls_coordinates_stations[info][0].split(',')[0], ls_coordinates_stations[info][0].split(',')[1]])
    dc_info_stations = {info[1]: {'name': info[0], 'addr': info[2], 'coord_long': info[3], 'coord_lat': info[4]} for
                        info in ls_info_stations}
    return dc_info_stations


if __name__ == '__main__':
    st = input()
    dc_info_state = info_stat()
