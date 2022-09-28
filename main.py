from pprint import pprint

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
        'specialization': '1.221',
        'area': 1,
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def predict_rub_salary(vacancy):

    salary = vacancy['salary']

    if not salary:
        return None

    if salary['currency'] != 'RUR':
        return None

    if salary['from'] and salary['to']:
        return (salary['from'] + salary['to'])//2

    if salary['from'] and not salary['to']:
        return int(salary['from']*1.2)
    else:
        return int(salary['to']*0.8)


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

    response = spec_vacancy(search_text='Программист Python')

    #pprint(response['items'][0]['salary'])

    for vacancy in response['items']:
        #print(vacancy['salary'])
        print(predict_rub_salary(vacancy))

    #response_python = vacancy_count(search_text='Программист Python')
    #response_java = vacancy_count(search_text='Программист Java')
    #response_javascript = vacancy_count(search_text='Программист JavaScript')

    #pprint(response_python)

    #vacancies_count = {
    #    'Python': response_python['found'],
    #    'Java': response_java['found'],
    #    'JavaScript': response_javascript['found'],
    #}

    #pprint(vacancies_count)


if __name__ == '__main__':
    main()
