from pprint import pprint

import requests


def main():

    vacancy_id = '1.221'

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

    with open('vacancy.txt', 'w') as f:
        print(response.json(), file=f)


if __name__ == '__main__':
    main()
