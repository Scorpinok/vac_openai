from datetime import datetime
import time
import json
import os

from tkinter import filedialog
from tkinter.filedialog import askopenfilenames
import tkinter as tk

import pandas as pd


root = tk.Tk()
root.withdraw()

def get_folder_name(fldr_nm, folder_or_not):
    root = tk.Tk()
    root.withdraw()

    if folder_or_not:
        folder_path = filedialog.askdirectory(title=f"Выберите папку с {fldr_nm}")
        root.destroy()
        return folder_path
    else:
        f_name = askopenfilenames(initialdir=r"C:",
                                  filetypes=(("json File", "*.json"), ("All Files", "*.*")),
                                  title=f"Выберите файл с {fldr_nm}"
                                  )
        root.destroy()
        return f_name

def process_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
        return None
    except json.JSONDecodeError:
        print(f"Некорректный JSON в файле {file_path}")
        return None


    occupation = []
    salary_min = []
    salary_max = []
    work_schedule = []

    url_vac = []
    city_vac = []
    field_vac = []
    date_vac = []
    contact_employer = []

    # hh
    if type(data) != list and data.get('items', 0) != 0:
        for i in range(len(data['items'])):
            occupation.append(data['items'][i]['name'])
            salary_min.append(data['items'][i]['salary']['from'] if data['items'][i]['salary'] is not None else None)
            salary_max.append(data['items'][i]['salary']['to'] if data['items'][i]['salary'] is not None else None)
            work_schedule.append(f"{data['items'][i]['schedule']['name'] if data['items'][i]['schedule'] is not None else ' '}; "
            f"{data['items'][i]['work_schedule_by_days'][0]['name'] if data['items'][i]['work_schedule_by_days'] is not None else ' '}; "
            f"{data['items'][i]['employment']['name'] if data['items'][i]['employment'] is not None else ' '}; "
            f"{data['items'][i]['working_hours'][0]['name'] if data['items'][i]['working_hours'] is not None else ' '}")

            url_vac.append(data['items'][i].get('alternate_url', 'не указано'))
            city_vac.append(data['items'][i].get('area', 'не указано').get('name','не указано'))
            date_vac.append(data['items'][i].get('published_at', 'не указано').split('T')[0])
            field_vac.append(data['items'][i].get('professional_roles', 'не указано')[0].get('name','не указано'))

            ser_cntc_empl = f"{data['items'][i].get('employer', 'не указано').get('name', 'не указано')}; " \
                            f"{data['items'][i].get('employer', 'не указано').get('alternate_url', 'не указано')}"

            contact_employer.append(ser_cntc_empl)

    #super_job
    if type(data) != list and data.get('objects', 0) != 0:
        for i in range(len(data['objects'])):
            occupation.append(data['objects'][i]['profession'])
            salary_min.append(data['objects'][i].get('payment_from', None))
            salary_max.append(data['objects'][i].get('payment_to', None))
            work_schedule.append(data['objects'][i]['type_of_work']['title'] if data['objects'][i]['type_of_work'] is not None else ' ')

            city_vac.append(data['objects'][i]['address'])
            url_vac.append(data['objects'][i]['link'])
            contact_employer.append(data['objects'][i]['phone'])

            if data['objects'][i].get('catalogues', None):
                if len(data['objects'][i]['catalogues']) == 3:
                    res_field = f'{data['objects'][i]['catalogues'][0].get('title', 'не указано')}; ' \
                                  f"{data['objects'][i]['catalogues'][0]['positions'][0].get('title', 'не указано')}; " \
                                  f'{data['objects'][i]['catalogues'][1].get('title', 'не указано')}; ' \
                                  f"{data['objects'][i]['catalogues'][1]['positions'][0].get('title', 'не указано')}; " \
                                  f'{data['objects'][i]['catalogues'][2].get('title', 'не указано')}; ' \
                                  f"{data['objects'][i]['catalogues'][2]['positions'][0].get('title', 'не указано')}; "
                elif len(data['objects'][i]['catalogues']) == 2:
                    res_field = f'{data['objects'][i]['catalogues'][0].get('title', 'не указано')}; ' \
                                  f"{data['objects'][i]['catalogues'][0]['positions'][0].get('title', 'не указано')}; " \
                                  f'{data['objects'][i]['catalogues'][1].get('title', 'не указано')}; ' \
                                  f"{data['objects'][i]['catalogues'][1]['positions'][0].get('title', 'не указано')}; "
                elif len(data['objects'][i]['catalogues']) == 1:
                    res_field = f'{data['objects'][i]['catalogues'][0].get('title', 'не указано')}; ' \
                                  f"{data['objects'][i]['catalogues'][0]['positions'][0].get('title', 'не указано')}; "
            else:
                res_field = 'не указан'

            field_vac.append(res_field)
            date_vac.append(datetime.fromtimestamp(data['objects'][i]['date_published']).strftime('%Y-%m-%d'))

    # trudvsem
    if type(data) != list and data.get('results', 0) != 0:
        if data['results']['vacancies'] is not None:
            for i in range(len(data['results']['vacancies'])):
                url_vac.append(data['results']['vacancies'][i]['vacancy'].get('vac_url', 'не указано'))
                city_vac.append(data['results']['vacancies'][i]['vacancy'].get('addresses', 'не указано').get('address', 'не указано')[0].get('location', 'не указано'))
                field_vac.append(data['results']['vacancies'][i]['vacancy'].get('category', 'не указано').get('specialisation', 'не указано'))
                date_vac.append(data['results']['vacancies'][i]['vacancy'].get('creation-date', 'не указано'))

                if data['results']['vacancies'][i]['vacancy'].get('contact_list', None):
                    if len(data['results']['vacancies'][i]['vacancy']['contact_list']) == 3:
                        res_contact = f'{data['results']['vacancies'][i]['vacancy'].get('contact_person', 'не указано')}; ' \
                            f"Тел.1: {data['results']['vacancies'][i]['vacancy']['contact_list'][0].get('contact_value','не указано')}; " \
                            f"Тел.2: {data['results']['vacancies'][i]['vacancy']['contact_list'][1].get('contact_value', 'не указано')}; "\
                            f"Эл.почта: {data['results']['vacancies'][i]['vacancy']['contact_list'][2].get('contact_value', 'не указано')}"
                    elif len(data['results']['vacancies'][i]['vacancy']['contact_list']) == 2:
                        res_contact = f'{data['results']['vacancies'][i]['vacancy'].get('contact_person', 'не указано')}; ' \
                            f"Тел.: {data['results']['vacancies'][i]['vacancy']['contact_list'][0].get('contact_value','не указано')}; " \
                            f"Эл.почта: {data['results']['vacancies'][i]['vacancy']['contact_list'][1].get('contact_value', 'не указано')}"
                else:
                    res_contact = 'не указан'

                contact_employer.append(res_contact)

                occupation.append(data['results']['vacancies'][i]['vacancy'].get('job-name', 'не указано'))
                salary_min.append(data['results']['vacancies'][i]['vacancy'].get('salary_min', 'не указано'))
                salary_max.append(data['results']['vacancies'][i]['vacancy'].get('salary_max', 'не указано'))
                work_schedule.append(f"{data['results']['vacancies'][i]['vacancy'].get('schedule', ' ')} "
                      f"{data['results']['vacancies'][i]['vacancy'].get('employment', ' ')}")


    df_data = {
        'occupation': occupation,
        'salary_min': salary_min,
        'salary_max': salary_max,
        'work_schedule': work_schedule,
        'url_vac' : url_vac,
        'city_vac' : city_vac,
        'field_vac' : field_vac,
        'date_vac' : date_vac,
        'contact_employer' : contact_employer
    }

    # telega
    if type(data) == list:
        for i in range(len(data)):
            occupation.append(data[i]['text'])
            df_data = {
                'occupation': occupation
            }

    df = pd.DataFrame(df_data)
    return df

dataframes = {}

f_name = get_folder_name('json',0)

start_time = time.time()

for file_path in (f_name):
    df = process_json_file(file_path)
    if df is not None:
        dataframes[file_path] = df
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.basename(file_path).replace('.json', '')
        output_file = f"output_{base_name}_{timestamp}"
        df.to_csv(f"{output_file}.csv", index=False, encoding='utf-8')
        df.to_excel(f"{output_file}.xlsx", index=False, engine='openpyxl')
        print(f"Сохранено в {os.path.dirname(file_path)}/{output_file}")

end_time = time.time()
execution_time = end_time - start_time
print(f"\nВремя выполнения: {execution_time:.2f} секунд")