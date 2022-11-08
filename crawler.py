import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import yaml


def get_user_data(name):
    url = 'https://lostark.game.onstove.com/Profile/Character/'
    response = requests.get(url + name)
    soup = BeautifulSoup(response.text, 'html.parser')
    profile = soup.select_one('div.profile-ingame')
    if profile.select_one('div.profile-attention'):
        # print(f'{name} 캐럭터 정보가 없습니다')
        return

    _class = profile.select_one('div.profile-equipment__character > img')['alt']
    itemLV = profile.select('div.level-info2__expedition > span')[1].text.replace('Lv.', '').replace(',', '')
    battleLV = profile.select('div.level-info__item > span')[1].text.replace('Lv.', '')
    expeditionLV = profile.select('div.level-info__expedition > span')[1].text.replace('Lv.', '')

    engraving = [engraving.text for engraving in profile.select('div.profile-ability-engrave > div > div > ul > li > span')]
    engraving_detail = ','.join(engraving)
    engraving_simple = re.sub(r'[^0-9]', '', engraving_detail)

    stat = [stat.text for stat in profile.select('div.profile-ability-battle > ul > li > span')]
    stat = [f'{stat[i]} {stat[i + 1]}' for i in range(0, len(stat), 2) if stat[i] in ['치명', '특화', '신속']]
    stat = ','.join(stat)

    card = profile.select('div.profile-card__text > div > ul > li > div.card-effect__title')[-1].text
    card = ','.join(card.replace(')', '').split(' ('))

    gems = re.findall(r"\d{,2}레벨 ..(?=의 보석)", response.text)
    gems = sorted(gems, key=lambda x: (-int(re.search(r'\d+', x).group()), x.split()[1]))
    counter = {}
    for gem in gems:
        if gem in counter: counter[gem] += 1
        else: counter[gem] = 1
    gem_simple = ','.join(f'{key} x{value}' for key, value in counter.items())

    equipmentLV = re.findall(r"\+.+(?=</FONT></P>)", response.text)
    equipmentLV = ','.join(equipmentLV).replace('+', '')

    power = profile.select_one('div.profile-ability-basic > ul > li:nth-child(1) > span:nth-child(2)').text
    vitality = profile.select_one('div.profile-ability-basic > ul > li:nth-child(2) > span:nth-child(2)').text

    character_data = {
        'name': name,
        'class': _class,
        'itemLV': float(itemLV),
        'battleLV': int(battleLV),
        'expeditionLV': int(expeditionLV),
        'engraving_simple': engraving_simple,
        'engraving_detail': engraving_detail,
        'stat': stat,
        'card': card,
        'gem_simple': gem_simple,
        'equipmentLV': equipmentLV,
        'power': int(power),
        'vitality': int(vitality)
    }

    return character_data


def read_guild_members():
    f = open('./_data/guild_members.txt', 'r', encoding='UTF-8')
    members = f.read().split('\n')
    return members


def data_to_dataframe(guild_members):
    member_data_list = []
    for member in guild_members:
        member_data = get_user_data(member)
        if member_data:
            member_data_list.append(member_data)
            print(member, 'complete')
        else:
            print(member, 'fail')
    df_memberlist = pd.DataFrame(data=member_data_list)
    df_memberlist = df_memberlist.sort_values(by='itemLV', ascending=False)

    return df_memberlist


def data_to_yaml(df):
    level_list = df['itemLV'].to_list()
    representative_value = {
        'highest_level': int(level_list[0]),
        'average_level': int(sum(level_list)/len(level_list)),
        'lowest_level': int(level_list[-1])
    }
    variance = {
        'above_1620': 0,
        'above_1610': 0,
        'above_1600': 0,
        'above_1590': 0,
        'above_1580': 0,
        'above_1570': 0,
        'above_1560': 0,
        'above_1550': 0,
        'above_1540': 0,
        'above_1530': 0,
        'above_1520': 0,
        'above_1510': 0,
        'above_1500': 0,
        'above_1490': 0,
        'under_1490': 0,
    }
    for level in level_list:
        if level >= 1620: variance['above_1620'] += 1
        elif level >= 1610: variance['above_1610'] += 1
        elif level >= 1600: variance['above_1600'] += 1
        elif level >= 1590: variance['above_1590'] += 1
        elif level >= 1580: variance['above_1580'] += 1
        elif level >= 1570: variance['above_1570'] += 1
        elif level >= 1560: variance['above_1560'] += 1
        elif level >= 1550: variance['above_1550'] += 1
        elif level >= 1540: variance['above_1540'] += 1
        elif level >= 1530: variance['above_1530'] += 1
        elif level >= 1520: variance['above_1520'] += 1
        elif level >= 1510: variance['above_1510'] += 1
        elif level >= 1500: variance['above_1500'] += 1
        elif level >= 1490: variance['above_1490'] += 1
        else: variance['under_1490'] += 1

    class_list = df['class'].to_list()
    class_num = {}
    class_num['Berserker'] = class_list.count('버서커')
    class_num['Destroyer'] = class_list.count('디스트로이어')
    class_num['Gunlancer'] = class_list.count('워로드')
    class_num['Paladin'] = class_list.count('홀리나이트')
    class_num['Arcanist'] = class_list.count('아르카나')
    class_num['Summoner'] = class_list.count('서머너')
    class_num['Bard'] = class_list.count('바드')
    class_num['Sorceress'] = class_list.count('소서리스')
    class_num['Wardancer'] = class_list.count('배틀마스터')
    class_num['Scrapper'] = class_list.count('인파이터')
    class_num['Soulfist'] = class_list.count('기공사')
    class_num['Glaivier'] = class_list.count('창술사')
    class_num['Striker'] = class_list.count('스트라이커')
    class_num['Deathblade'] = class_list.count('블레이드')
    class_num['Shadowhunter'] = class_list.count('데모닉')
    class_num['Reaper'] = class_list.count('리퍼')
    class_num['Sharpshooter'] = class_list.count('호크아이')
    class_num['Deadeye'] = class_list.count('데빌헌터')
    class_num['Artillerist'] = class_list.count('블래스터')
    class_num['Machinist'] = class_list.count('스카우터')
    class_num['Gunslinger'] = class_list.count('건슬링어')
    class_num['Artist'] = class_list.count('도화가')
    class_num['Aeromancer'] = class_list.count('기상술사')

    data = {'representative_value': representative_value,
            'variance': variance,
            'class_num': class_num
            }
    return data


def update_log():
    filename = datetime.now().strftime('%y-%m-%d') + '.csv'
    update_time = datetime.now().strftime('%y-%m-%d %H:%M:%S')
    log = {
        'filename': filename,
        'update_time': update_time
    }
    return [log]


def data_to_file(df):
    path = './_data/chart/'
    filename = datetime.now().strftime('%y-%m-%d') + '.csv'
    df.to_csv(path + filename, index=False)
    df.to_csv('./_data/member_chart.csv', index=False)
    with open('./_data/total_info.yml', 'w') as file:
        yaml.dump(data_to_yaml(df), file, default_flow_style=False)
    with open('./_data/update_time.yml', 'a') as file:
        yaml.dump(update_log(), file, default_flow_style=False)


if __name__ == '__main__':
    guild_members = read_guild_members()
    df = data_to_dataframe(guild_members)
    data_to_file(df)
