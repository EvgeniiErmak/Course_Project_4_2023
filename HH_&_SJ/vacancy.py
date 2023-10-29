import requests
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod

class APIManager(ABC):
    @abstractmethod
    def get_vacancies(self):
        pass

class Vacancy:
    def __init__(self, name, page, top_n):
        self.name = name
        self.page = page
        self.top_n = top_n

    def __repr__(self):
        return f'{self.name}'

class HH(Vacancy, APIManager):
    def __init__(self, name, page, top_n):
        super().__init__(name, page, top_n)
        self.url = 'https://api.hh.ru'
        self.platform = 'HH'

    def get_vacancies(self):
        data = requests.get(f'{self.url}/vacancies', params={'text': self.name, 'page': self.page, 'per_page': self.top_n}).json()
        return data

    def load_vacancy(self):
        data = self.get_vacancies()
        vacancies = []
        for vacancy in data.get('items', []):
            published_at = datetime.strptime(vacancy['published_at'], "%Y-%m-%dT%H:%M:%S%z")
            vacancy_info = {
                'platform': self.platform,
                'id': vacancy['id'],
                'name': vacancy['name'],
                'salary_from': vacancy['salary']['from'] if vacancy.get('salary') else None,
                'salary_to': vacancy['salary']['to'] if vacancy.get('salary') else None,
                'responsibility': vacancy['snippet']['responsibility'],
                'date': published_at.strftime("%d.%m.%Y"),
                'city': vacancy['area']['name'] if vacancy.get('area') else 'N/A',
                'work_schedule': vacancy['schedule']['name'] if vacancy.get('schedule') else 'N/A'
                # Добавьте другие детали, если они предоставлены API
            }
            vacancies.append(vacancy_info)
        return vacancies

class SuperJob(Vacancy, APIManager):
    def __init__(self, name, page, top_n):
        super().__init__(name, page, top_n)
        self.url = 'https://api.superjob.ru/2.0/vacancies/'
        self.platform = 'SuperJob'

    def get_vacancies(self):
        headers = {
            'X-Api-App-Id': os.getenv('API_KEY_SJ'),
        }
        data = requests.get(self.url, headers=headers, params={'keywords': self.name, 'page': self.page, 'count': self.top_n}).json()
        return data

    def load_vacancy(self):
        data = self.get_vacancies()
        vacancies = []
        for vacancy in data['objects']:
            published_at = datetime.fromtimestamp(vacancy.get('date_published', ''))
            super_job = {
                'platform': self.platform,
                'id': vacancy['id'],
                'name': vacancy.get('profession', ''),
                'salary_from': vacancy.get('payment_from', '') if vacancy.get('payment_from') else None,
                'salary_to': vacancy.get('payment_to') if vacancy.get('payment_to') else None,
                'responsibility': vacancy.get('candidat', '').replace('\n', '').replace('•', '') if vacancy.get('candidat') else None,
                'date': published_at.strftime("%d.%m.%Y"),
                'city': vacancy.get('town', {}).get('title', 'N/A'),
                'work_schedule': vacancy.get('schedule', {}).get('title', 'N/A')
                # Добавьте другие детали, если они предоставлены API
            }
            vacancies.append(super_job)
        return vacancies

def job_vacancy():
    name = input('Введите вакансию: ')
    top_n = input('Введите кол-во вакансий: ')
    page = int(input('Введите номер страницы: '))
    hh_instance = HH(name, page, top_n)
    sj_instance = SuperJob(name, page, top_n)
    combined_list = hh_instance.load_vacancy() + sj_instance.load_vacancy()

    with open('SuperJob.json', 'w', encoding='utf-8') as file:
        json.dump(combined_list, file, ensure_ascii=False, indent=2)

    platform_choice = input('Выберите платформу для поиска: (1 - HH, 2 - SuperJob, 3 - Обе) ')

    while True:
        if platform_choice == '1':
            hh_vacancies = [vacancy for vacancy in combined_list if vacancy['platform'] == 'HH']
            for platform in hh_vacancies:
                print(f"\nПлатформа: {platform['platform']}\nID вакансии: {platform['id']}\nДата публикации: {platform['date']}\nДолжность: {platform['name']}\nЗарплата от: {platform['salary_from']}\nЗарплата до: {platform['salary_to']}\nОписание: {platform['responsibility']}\nГород: {platform['city']}\nГрафик работы: {platform['work_schedule']}\n")

        elif platform_choice == '2':
            sj_vacancies = [vacancy for vacancy in combined_list if vacancy['platform'] == 'SuperJob']
            for platform in sj_vacancies:
                print(f"\nПлатформа: {platform['platform']}\nID вакансии: {platform['id']}\nДата публикации: {platform['date']}\nДолжность: {platform['name']}\nЗарплата от: {platform['salary_from']}\nЗарплата до: {platform['salary_to']}\nОписание: {platform['responsibility']}\nГород: {platform['city']}\nГрафик работы: {platform['work_schedule']}\n")

        elif platform_choice == '3':
            for platform in combined_list:
                print(f"\nПлатформа: {platform['platform']}\nID вакансии: {platform['id']}\nДата публикации: {platform['date']}\nДолжность: {platform['name']}\nЗарплата от: {platform['salary_from']}\nЗарплата до: {platform['salary_to']}\nОписание: {platform['responsibility']}\nГород: {platform['city']}\nГрафик работы: {platform['work_schedule']}\n")

        next_page = input('Перейти на следующую страницу? (y/n) ')
        if next_page.lower() != 'y':
            break
        page += 1

job_vacancy()
