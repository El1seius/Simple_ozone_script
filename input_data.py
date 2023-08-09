import argparse
import sys

from dateutil.parser import parse

from constants import STATUS_CATALOGUE
from output import get_color_message


def get_input_data():
    parser = argparse.ArgumentParser(description='Get data for report OZON')

    parser.add_argument(
        'date_start', help='Date from which the report starts, format: day/month/year'
        )
    parser.add_argument(
        'date_finish', help='Date on which the report ends, format: day/month/year'
        )
    parser.add_argument('status', help='Departure status')

    args = parser.parse_args()
    date_start, date_finish = process_date(args.date_start, args.date_finish)
    status_send = check_status(args.status)

    return date_start, date_finish, status_send


def process_date(date_start_row, date_finish_row):
    date_start = parse(date_start_row, dayfirst=True)
    date_finish = parse(date_finish_row, dayfirst=True)
    if date_start >= date_finish:
        get_color_message(
            ('Некорректные даты. Дата начала отчета должна быть раньше даты окончания.'), 'error'
            )
        get_color_message(f'Дата начала отчета: {date_start.date()}', 'info')
        get_color_message(f'Дата окончания отчета: {date_finish.date()}', 'info')
        sys.exit()
    else:
        return date_start, date_finish


def check_status(status):
    if status in STATUS_CATALOGUE:
        return status
    else:
        get_color_message(('Не правильно указан статус отправления.'), 'error')
        sys.exit()
