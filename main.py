import json
import os
from pprint import pprint
from statistics import mean
from itertools import count
import requests
from dotenv import load_dotenv


def spec_vacancy(search_text):
    url = 'https://api.hh.ru/vacancies'

    result_vacancies = []

    headers = {
        'User - Agent': 'hh_client / 1.0(hh_client - statik2002@gmail.com)',
    }

    for page in count(0):

        params = {
            'text': search_text,
            'search_field': 'description',
            'specialization': '1.221',
            'area': 1,
            'page': page,
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        vacancy_page = response.json()

        if page >= vacancy_page['pages']:
            break

        result_vacancies.append(vacancy_page)

    return result_vacancies


def vacancy_count(search_text):
    url = 'https://api.hh.ru/vacancies'

    headers = {
        'User - Agent': 'hh_client / 1.0(hh_client - statik2002@gmail.com)',
    }

    params = {
        'text': search_text,
        'clusters': True,
        'per_page': 0,
        'search_field': 'description',
        'area': 1,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def predict_rub_salary(vacancies):

    average_salary = []

    for vacancy_page in vacancies:
        for vacancy in vacancy_page['items']:
            salary = vacancy['salary']

            if not salary:
                continue

            if salary['currency'] != 'RUR':
                continue

            if salary['from'] and salary['to']:
                average_salary.append((salary['from'] + salary['to'])//2)

            if salary['from'] and not salary['to']:
                average_salary.append(int(salary['from']*1.2))

            if not salary['from'] and salary['to']:
                average_salary.append(int(salary['to']*0.8))

    return int(mean(average_salary)), len(average_salary)


def superjob_vacancies(token, keyword):

    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {
        'Authorization': f'Bearer r.137022255.155c8bc62ac576ac37a78ae617e286684904fab1.d3d22e52914d63f61c886c444a1cb20d0ed98003',
        'X-Api-App-Id': 'v3.r.137022255.155c8bc62ac576ac37a78ae617e286684904fab1.d3d22e52914d63f61c886c444a1cb20d0ed98003',
        'Content-Type': 'application / x - www - form - urlencoded',
    }

    params = {
        'town': 4,
        'keywords': {keyword},
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    vacancies = [vacancy for vacancy in response.json()['objects']]

    #for vacancy in response.json()['objects']:
    #    print(f"{vacancy['profession']} / {vacancy['town']['title']}")

    return vacancies


def predict_rub_salary_for_superJob(vacancy):

    salary = []

    if vacancy['currency'] != 'rub':
        return None

    payment_from = vacancy['payment_from']
    payment_to = vacancy['payment_to']
    if payment_from != 0 and payment_to != 0:
        salary.append((payment_from+payment_to)//2)
    elif payment_from != 0 and payment_to == 0:
        salary.append(payment_from*1.2)
    elif payment_from == 0 and payment_to != 0:
        salary.append(payment_to*0.8)
    else:
        return None

    return int(mean(salary))


def main():

    load_dotenv()

    professions = ['Программист SQL', ]

    superjob_token = os.environ['SUPERJOB_TOKEN']
    superjob_id = os.environ['SUPERJOB_ID']

    superjob_all_vacancies = superjob_vacancies(superjob_token, 'Программист')
    for vacancy in superjob_all_vacancies:
        avg_salary = predict_rub_salary_for_superJob(vacancy)
        print(f"{vacancy['profession']}', {vacancy['town']['title']}', {avg_salary}")

    """
    python_vacancies = spec_vacancy(search_text='Программист Python')
    python_average_salary, python_vacancies_processed = predict_rub_salary(python_vacancies)
    python_total_vacancies = python_vacancies[0]['found']
    python_stat = {
        "vacancies_found": python_total_vacancies,
        "vacancies_processed": python_vacancies_processed,
        "average_salary": python_average_salary
    }

    java_vacancies = spec_vacancy(search_text='программист java')
    java_average_salary, java_vacancies_processed = predict_rub_salary(java_vacancies)
    java_total_vacancies = java_vacancies[0]['found']
    java_stat = {
        "vacancies_found": java_total_vacancies,
        "vacancies_processed": java_vacancies_processed,
        "average_salary": java_average_salary
    }

    javascript_vacancies = spec_vacancy(search_text='Программист JavaScript')
    javascript_average_salary, javascript_vacancies_processed = predict_rub_salary(javascript_vacancies)
    javascript_total_vacancies = java_vacancies[0]['found']
    javascript_stat = {
        "vacancies_found": javascript_total_vacancies,
        "vacancies_processed": javascript_vacancies_processed,
        "average_salary": javascript_average_salary
    }

    vacancy_statistic = {
        'Python': python_stat,
        'Java': java_stat,
        'Javascript': javascript_stat
    }

    pprint(vacancy_statistic)
    """


if __name__ == '__main__':
    main()
