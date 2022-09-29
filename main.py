import argparse
import os
from statistics import mean
from itertools import count
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_hh_vacancies(search_text):
    url = 'https://api.hh.ru/vacancies'

    result_vacancies = []
    total_vacancies_found = 0

    headers = {
        'User - Agent': 'hh_client / 1.0(hh_client - statik2002@gmail.com)',
    }

    for page in count(0):

        params = {
            'text': search_text,
            'search_field': 'name',
            'area': 1,
            'page': page,
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        vacancy_page = response.json()

        if page >= vacancy_page['pages']-1:
            break

        result_vacancies.append(vacancy_page)
        total_vacancies_found = vacancy_page['found']

    return result_vacancies, total_vacancies_found


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

    if len(average_salary) <= 0:
        return 0, 1

    return int(mean(average_salary)), len(average_salary)


def superjob_vacancies(token, keyword):

    url = 'https://api.superjob.ru/2.0/vacancies/'

    vacancy_pages = []

    headers = {
        'X-Api-App-Id': f'{token}',
        'Content-Type': 'application / x - www - form - urlencoded',
    }

    for page in count(0):
        params = {
            'town': 4,
            'keywords': {keyword},
            'page': page,
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        vacancy_page_json = response.json()

        vacancy_pages.append(vacancy_page_json)

        if page >= vacancy_page_json['total']/((page+1)*20):
            break

    return vacancy_pages, vacancy_page_json['total']


def predict_rub_salary_for_superJob(vacancy_pages):

    salary = []
    vacancy_proceeded_count = 0

    for vacancy_page in vacancy_pages:
        for vacancy in vacancy_page['objects']:
            if vacancy['currency'] != 'rub':
                continue

            payment_from = vacancy['payment_from']
            payment_to = vacancy['payment_to']
            if payment_from != 0 and payment_to != 0:
                salary.append((payment_from+payment_to)//2)
                vacancy_proceeded_count += 1
            elif payment_from != 0 and payment_to == 0:
                salary.append(payment_from*1.2)
                vacancy_proceeded_count += 1
            elif payment_from == 0 and payment_to != 0:
                salary.append(payment_to*0.8)
                vacancy_proceeded_count += 1
            else:
                continue

    if len(salary) <= 0:
        return 0, 1

    return int(mean(salary)), vacancy_proceeded_count


def print_vacancies_stat(vacancies_stat, table_title):

    data = list()
    data.append(
        [
            'Языки программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    )

    for profession, value in vacancies_stat.items():
        data.append(
            [profession,
             value['vacancies_found'],
             value['vacancies_processed'],
             value['average_salary']
             ]
        )

    table = AsciiTable(data)
    table.title = table_title
    print(table.table)


def main():

    parser = argparse.ArgumentParser(
        description='Скрипт для анализа вакансий по языкам'
                    ' программирования на hh.ru и superjob.ru',
    )
    parser.add_argument(
        '--p',
        help='список языков программирования для поиска через ,',
        default='Python,Java,Javascript,C#,Objective-C,c,C++,ruby,go,1c'
    )
    args = parser.parse_args()
    professions = args.p.split(',')

    load_dotenv()

    superjob_token = os.environ['SUPERJOB_TOKEN']

    superjob_vacancies_stat = {}
    hh_vacancies_stat = {}

    for profession in professions:
        superjob_all_vacancies, total_vacancies = superjob_vacancies(
            superjob_token, profession.strip()
        )
        avg_salary, vacancy_proceeded_count = predict_rub_salary_for_superJob(
            superjob_all_vacancies
        )
        vacancy_sat = {
            "vacancies_found": total_vacancies,
            "vacancies_processed": vacancy_proceeded_count,
            "average_salary": avg_salary,
        }
        superjob_vacancies_stat.update({profession: vacancy_sat})

    print_vacancies_stat(superjob_vacancies_stat, 'SuperJob Moscow')

    for profession in professions:
        profession_vacancies, profession_total_vacancies = get_hh_vacancies(
            search_text=profession.strip()
        )
        profession_average_salary, profession_vacancies_processed = predict_rub_salary(
            profession_vacancies
        )
        profession_stat = {
            "vacancies_found": profession_total_vacancies,
            "vacancies_processed": profession_vacancies_processed,
            "average_salary": profession_average_salary
        }
        hh_vacancies_stat.update({profession: profession_stat})

    print_vacancies_stat(hh_vacancies_stat, 'HeadHunter Moscow')


if __name__ == '__main__':
    main()
