"""
Библиотека функций ETL
1. Принимает словари огранизаций и остановок
2. Нахождение ближайшей организации
3. Выгрузка словаря организаций
"""
import pickle

# 1. Загрузка словаря организаций
from pprint import pprint

with open('dc_full_org.pickle', 'rb') as f:
    dc_obj2 = pickle.load(f)
# 1. Загрузка словаря остановок
with open('dump.dat', 'rb') as f:
    dc_obj1 = pickle.load(f)
# Объявление переменных
min_coord = 99
fin_org = ''
fin_id_org = ''
ls_id_org = []
fin_address = ''
fin_station = ''
# 2. Нахождение ближайшей организации
for dc1 in dc_obj1.items():
    for dc2 in dc_obj2.items():
        x1 = float(dc1[1]['coord_long'])
        x2 = float(dc2[1]['lon'])
        y1 = float(dc1[1]['coord_lat'])
        y2 = float(dc2[1]['lat'])
        if abs(x1 - x2) + abs(y1 - y2) < min_coord:
            min_coord = abs(x1 - x2) + abs(y1 - y2)
            fin_id_station = dc1[0]
            fin_id_org = dc2[0]
            fin_station = dc1[1]['name']
            fin_org = str(dc2[1]['category']) + ' ' + dc2[1]['title']
            fin_address = dc2[1]['address']
    dc1[1]['org'] = fin_id_org
    ls_id_org.append(fin_id_org)
    min_coord = 99
    print(fin_org, fin_id_org)
pprint(dc_obj1)
# cn = 0
# new_dc = {}
# ls_vr = []
# st = set([el[1]['name'] for el in dc_obj1.items()])
# for el in st:
#     for dc in dc_obj1.items():
#         if el == dc[1]['name']:
#             cn += 1
#             if cn >= 2:
#                 new_dc[dc[0]] = dc[1]
#                 ls_vr.append(dc[1]['name'])
#     cn = 0
# st = list(set(ls_vr))
# pprint(st)
# pprint(dc_obj1)

# 3. Выгрузка словаря организаций
with open('dc_org_stat.pickle', 'wb') as f:
    pickle.dump(dc_obj1, f)
