import requests
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod

class APIManager(ABC):

    @abstractmethod
    def get_vacancies(self):
        """
        Получает вакансии по API и возвращает список вакансий согласно запросу пользователя.
        """
        pass

class Vakancy:
    def __init__(self, name, page, top_n):
        """
        Инициализация объекта Vacancy.

        :param name: Название вакансии.
        :param page: Номер страницы.
        :param top_n: Количество вакансий на странице.
        """
        self.name = name
        self.page = page
        self.top_n = top_n

    def __repr__(self):
        return f'{self.name}'

class HH(Vakancy, APIManager):
    def __init__(self, name, page, top_n):
        super().__init__(name, page, top_n)
        self.url = 'https://api.hh.ru'

    def get_vacancies(self):
        """
        Получает вакансии с помощью API и возвращает их в виде списка.

        :return: Список вакансий.
        """
        data = requests.get(f'{self.url}/vacancies', params={'text': self.name, 'page': self.page, 'per_page': self.top_n}).json()
        return data

    def load_vacancy(self):
        """
        Загружает вакансии с помощью API и возвращает список вакансий.

        :return: Список вакансий.
        """
        data = self.get_vacancies()
        vacancies = []
        for vacancy in data.get('items', []):
            published_at = datetime.strptime(vacancy['published_at'], "%Y-%m-%dT%H:%M:%S%z")
            vacancy_info = {
                'id': vacancy['id'],
                'name': vacancy['name'],
                'solary_ot': vacancy['salary']['from'] if vacancy.get('salary') else None,
                'solary_do': vacancy['salary']['to'] if vacancy.get('salary') else None,
                'responsibility': vacancy['snippet']['responsibility'],
                'data': published_at.strftime("%d.%m.%Y")
            }
            vacancies.append(vacancy_info)
        return vacancies

class Super_job(Vakancy, APIManager):
    def __init__(self, name, page, top_n):
        super().__init__(name, page, top_n)
        self.url = 'https://api.superjob.ru/2.0/vacancies/'

    def get_vacancies(self):
        """
        Получает вакансии с помощью API SuperJob и возвращает их в виде списка.

        :return: Список вакансий.
        """
        headers = {
            'X-Api-App-Id': os.getenv('API_KEY_SJ'),
        }
        data = requests.get(self.url, headers=headers, params={'keywords': self.name, 'page': self.page, 'count': self.top_n}).json()
        return data

    def load_vacancy(self):
        """
        Загружает вакансии с помощью API SuperJob и возвращает список вакансий.

        :return: Список вакансий.
        """
        data = self.get_vacancies()
        vacancy_list_SJ = []
        for i in data['objects']:
            published_at = datetime.fromtimestamp(i.get('date_published', ''))
            super_job = {
                'id': i['id'],
                'name': i.get('profession', ''),
                'solary_ot': i.get('payment_from', '') if i.get('payment_from') else None,
                'solary_do': i.get('payment_to') if i.get('payment_to') else None,
                'responsibility': i.get('candidat').replace('\n', '').replace('•', '') if i.get('candidat') else None,
                'data': published_at.strftime("%d.%m.%Y"),
            }
            vacancy_list_SJ.append(super_job)
        return vacancy_list_SJ

def job_vacancy():
    """
    Основной код проекта, после ввода данных пользователем, данные сортируются согласно запросу пользователя и сохраняются в JSON файл.
    Пользователь может выбрать платформу для поиска вакансий (HH, SJ, обе) и просматривать результаты поиска.

    :return: None
    """
    name = input('Введите вакансию: ')
    top_n = input('Введите кол-во вакансий: ')
    page = int(input('Введите номер страницы: '))
    hh_instance = HH(name, page, top_n)
    sj_instance = Super_job(name, page, top_n)
    combined_dict = {'HH': hh_instance.load_vacancy(), 'SJ': sj_instance.load_vacancy()}

    with open('Super_job.json', 'w', encoding='utf-8') as file:
        json.dump(combined_dict, file, ensure_ascii=False, indent=2)

    platforma = input('Введите платформу для поиска: (1 - HH, 2 - SJ, 3 - обе платформы)  ')

    if platforma == '1':
        while True:
            hh_instance.page = page
            sj_instance.page = page
            hh_data = hh_instance.load_vacancy()

            combined_dict['HH'] = hh_data

            with open('Super_job.json', 'w', encoding='utf-8') as file:
                json.dump(combined_dict, file, ensure_ascii=False, indent=2)

            for platform in combined_dict['HH']:
                print(f"\nid - {platform['id']}\nДолжность - {platform['name']}\nЗ.п от - {platform['solary_ot']}\nЗ.п до - {platform['solary_ot']}\nОписание - {platform['responsibility']}\nДата - {platform['data']}\n")
            a = input('перейти на следующую страницу? y/n ')
            if a == 'y':
                page += 1
            else:
                break
    elif platforma == '2':
        while True:
            hh_instance.page = page
            sj_instance.page = page
            hh_data = hh_instance.load_vacancy()
            sj_data = sj_instance.load_vacancy()

            combined_dict['HH'] = hh_data
            combined_dict['SJ'] = sj_data

            with open('Super_job.json', 'w', encoding='utf-8') as file:
                json.dump(combined_dict, file, ensure_ascii=False, indent=2)

            for platform in combined_dict['SJ']:
                print(f"\nid - {platform['id']}\nДолжность - {platform['name']}\nЗ.п от - {platform['solary_ot']}\nЗ.п до - {platform['solary_do']}\nОписание - {platform['responsibility']}\nДата - {platform['data']}\n")

            a = input('перейти на следующую страницу? y/n ')
            if a == 'y':
                page += 1
            else:
                break
    elif platforma == '3':
        while True:
            hh_instance.page = page
            sj_instance.page = page
            hh_data = hh_instance.load_vacancy()
            sj_data = sj_instance.load_vacancy()

            combined_dict['HH'] = hh_data
            combined_dict['SJ'] = sj_data

            with open('Super_job.json', 'w', encoding='utf-8') as file:
                json.dump(combined_dict, file, ensure_ascii=False, indent=2)

            for platform, data in combined_dict.items():
                print(f"\n \033Платформа: {platform}")
                for item in data:
                    print(f"id - {item['id']}\nДолжность - {item['name']}\nЗ.п от - {item['solary_ot']}\nЗ.п до - {item['solary_do']}\nОписание - {item['responsibility']}\nДата - {item['data']}\n")

            a = input('перейти на следующую страницу? y/n ')
            if a == 'y':
                page += 1
            else:
                break

job_vacancy()
