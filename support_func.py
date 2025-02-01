import requests
import subprocess
import pprint
import re
import csv
from pathlib import Path
import headers

def response_from_gpt(list_kanji):
    # For test
    # return {'result': '```\n'
    #        '正式, せいしき (Noun), CHÍNH THỨC, chính thức.\n'
    #        '形式, けいしき (Noun), HÌNH THỨC, hình thức.\n'
    #        '```',
    # 'server_code': 'dg',
    # 'status': True}

    url = "https://chatgpt-42.p.rapidapi.com/gpt4"

    payload = {
        "messages": [
            {
                "role": "user",
                "content": 
                    f'''
                        Khi tôi đưa vào kanji, không trả về bất cứ gì ngoài list csv.
                        Động từ ghi TỰ, THA. Tính từ ghi い、な. Danh từ ghi Noun
                        Ví dụ: 教室, きょうしつ (Noun), GIÁO THẤT, lớp học.
                        Tương tự với {', '.join(list_kanji)}
                    '''
            }
        ],
        "web_access": False
    }

    header = headers.headers[0]

    response = requests.post(url, json=payload, headers=header)
    response.raise_for_status()

    print('\n---------------- Dữ liệu trả về từ GPT ----------------')
    pprint.pprint(response.json())

    return response.json()


def get_list_item_from_response(data_response):
    pattern = r'(?<=```)[\s\S]+(?=```)'

    if data_response['status']:
        data = data_response['result']
        data = re.findall(pattern, data)[0]
        data = data.split('\n')
        data = [item.split(', ') for item in data if item]

        return data
    else:
        print(data_response)
        raise ValueError(f'Status: False')


def transform_list_to_dict(data_list):
    fields = ['Kanji', 'Hiragana', 'Chinese character', 'Meaning']

    data_dict_type = []
    for item in data_list:
        data_dict_type_item = {}
        for index, value in enumerate(item):
            data_dict_type_item[fields[index]] = value
        data_dict_type.append(data_dict_type_item)

    return data_dict_type


def save_to_csv(data):
    file_name = Path('./data.csv')
    fields = ['Kanji', 'Hiragana', 'Chinese character', 'Meaning']

    with open(file_name, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        # Không ghi header vì import bị dính
        # writer.writeheader()

        writer.writerows(data)


def read_data_from_csv():
    rows = []

    with open('./data.csv', 'r') as file:
        csvreader = csv.reader(file)
        
        for row in csvreader:
            rows.append(row)
        
    return rows


def show_data():
    print('\n---------------- Dữ liệu trong csv ----------------')
    rows = read_data_from_csv()

    space = [30, 50, 30, 70]
    horizontal_line = '+' + '+'.join(['-' * space[index] for index in range(len(space))]) + '+'

    for row in rows:
        print(horizontal_line)
        print('|' + '|'.join(f' {value:<{ \
            space[index] - ( \
                len(value) if index == 0 else ( \
                    value.find(' ') if index == 1 else 0)) - 1 \
                        }}' for index, value in enumerate(row)) + '|')
    
    print(horizontal_line)


def disable_app_napp(disabled: False):
    status = 'true' if disabled else 'false'

    commands = [
        f'defaults write net.ankiweb.dtop NSAppSleepDisabled -bool {status}',
        f'defaults write net.ichi2.anki NSAppSleepDisabled -bool {status}',
        f'defaults write org.qt-project.Qt.QtWebEngineCore NSAppSleepDisabled -bool {status}'
    ]

    for cmd in commands:
        subprocess.run(cmd, shell=True)

def check_potential_add_notes(data):
    url = 'http://localhost:8765'

    deck_name = 'Kanji N3'
    model_name = 'Kanji'

    notes = []
    for fields in data:
        note = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields
        }

        notes.append(note)

    request = {
        "action": "canAddNotesWithErrorDetail",
        "version": 6,
        "params": {
            "notes": notes
        }
    }

    response = requests.post(url, json=request)
    response.raise_for_status()

    results = response.json()
    results = [res_one_note['canAdd'] for res_one_note in results['result']]
    return results


def add_notes(data, canAdd):
    url = 'http://localhost:8765'

    deck_name = 'Kanji N3'
    model_name = 'Kanji'

    notes = []
    for index, fields in enumerate(data):
        if canAdd[index]:
            note = {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": fields
            }

            notes.append(note)

    request = {
        "action": "addNotes",
        "version": 6,
        "params": {
            "notes": notes
        }
    }

    response = requests.post(url, json=request)
    response.raise_for_status()
    return response.json()

