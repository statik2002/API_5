from pprint import pprint
from statistics import mean

import requests


def spec_vacancy(search_text):
    url = 'https://api.hh.ru/vacancies'

    headers = {
        'User - Agent': 'hh_client / 1.0(hh_client - statik2002@gmail.com)',
    }

    params = {
        'text': search_text,
        'search_field': 'description',
        'specialization': '1.221',
        'area': 1,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


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

    for vacancy in vacancies:
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


def main():

    vacancy_id = '1.221'

    """
    url = 'https://api.hh.ru/vacancies'

    headers = {
        'User - Agent': 'hh_client / 1.0(hh_client - statik2002@gmail.com)',
    }

    params = {
        'specialization': vacancy_id,
        'area': 1,
        'period': 30,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    """

    params = {

    }

    python_vacancies = spec_vacancy(search_text='Программист Python')
    python_average_salary, python_vacancies_processed = predict_rub_salary(python_vacancies['items'])
    python_total_vacancies = python_vacancies['found']
    python_stat = {
        "vacancies_found": python_total_vacancies,
        "vacancies_processed": python_vacancies_processed,
        "average_salary": python_average_salary
    }

    java_vacancies = spec_vacancy(search_text='программист java')
    java_average_salary, java_vacancies_processed = predict_rub_salary(java_vacancies['items'])
    java_total_vacancies = java_vacancies['found']
    java_stat = {
        "vacancies_found": java_total_vacancies,
        "vacancies_processed": java_vacancies_processed,
        "average_salary": java_average_salary
    }

    javascript_vacancies = spec_vacancy(search_text='Программист JavaScript')
    javascript_average_salary, javascript_vacancies_processed = predict_rub_salary(javascript_vacancies['items'])
    javascript_total_vacancies = java_vacancies['found']
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


if __name__ == '__main__':
    main()
