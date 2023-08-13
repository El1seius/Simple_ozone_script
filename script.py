import json
import os
import requests
import sys

from collections import Counter
from datetime import datetime as dt

from constants import LIMIT, URL_OZON, COUNTRIES_SHIPMENT
from input_data import get_input_data
from output import create_table, get_color_message, output_error


def get_sales_data(date_start, date_finish, status):
    offset = 0
    str_dt_start = dt.strftime(date_start, '%Y-%m-%dT%H:%M:%S.%fZ')
    str_dt_finish = dt.strftime(date_finish, '%Y-%m-%dT%H:%M:%S.%fZ')

    report = get_report_with_all_page(str_dt_start, str_dt_finish, offset, status)
    report_with_filter,  numb_shipment_countries = filter_by_shipment_countries(report)
    return report_with_filter, numb_shipment_countries


def get_report_with_all_page(str_dt_start, str_dt_finish, offset, status):
    report_pagination = []
    while True:
        sales_report = get_raw_sales_data(str_dt_start, str_dt_finish, offset, status)
        if sales_report is not None:
            short_report = make_short_report(sales_report)
            report_pagination.extend(short_report)
            if sales_report['result']['has_next']:
                offset += LIMIT
            else:
                break
        else:
            break
    return report_pagination


def get_raw_sales_data(datetime_start, datetime_finish, offset, status):
    headers = {
        'Client-Id': os.environ['OZON_CLIENT_ID'],
        'Api-Key': os.environ['OZON_API_KEY'],
        'Content-Type': 'application/json'
        }

    params = {
        'dir': 'asc',
        'filter': {
            'since': datetime_start,
            'status': status,
            'to': datetime_finish
        },
        'limit': LIMIT,
        'offset': offset,
        'translit': True,
        'with': {
            'analytics_data': True,
            'financial_data': True,
        }
    }

    params = json.dumps(params)
    response = requests.post(URL_OZON, headers=headers, data=params)
    if response:
        try:
            sales_report = response.json()
            return sales_report
        except ValueError:
            get_color_message(('Ошибка сформированных данных'), 'error')
            sys.exit()
    else:
        get_color_message(('Сетевая ошибка'), 'error')
        code = response.status_code
        output_error(code)
        sys.exit()


def make_short_report(sales_report):
    all_item_sold = sales_report['result']['postings']
    short_report = []
    for one_item_sold in all_item_sold:
        inform_every_item_sold = {
            'posting_number': one_item_sold['posting_number'],
            'shipment_date': one_item_sold['shipment_date'],
            'price': one_item_sold['products'][0]['price'],
            'name': one_item_sold['products'][0]['name'],
            'quantity': one_item_sold['products'][0]['quantity'],
            'cluster_delivery': one_item_sold['financial_data']['cluster_to']
        }

        short_report.append(inform_every_item_sold)
    return short_report


def filter_by_shipment_countries(short_report):
    report_with_filter_city = []
    for item_sold in short_report:
        for one_cou in COUNTRIES_SHIPMENT:
            cluster = set(item_sold['cluster_delivery'].split())
            if cluster & COUNTRIES_SHIPMENT[one_cou]:
                item_sold['cluster_delivery'] = one_cou
                report_with_filter_city.append(item_sold)

    numb_shipment_countries = get_numb_shipment_in_countries(report_with_filter_city)
    sorted_report = get_sorted_report(report_with_filter_city, numb_shipment_countries)

    return sorted_report, numb_shipment_countries


def get_numb_shipment_in_countries(report):
    clusters_delivery = []
    for posit in report:
        clusters_delivery.append(posit['cluster_delivery'])
    numb_shipment_countries = Counter(clusters_delivery).most_common()
    return numb_shipment_countries


def get_sorted_report(report, numb_shipment_countries):
    sorted_report = []
    for one_country in numb_shipment_countries:
        for item in report:
            if one_country[0] in item['cluster_delivery']:
                sorted_report.append(item)
    return sorted_report


if __name__ == '__main__':
    date_start, date_finish, status = get_input_data()
    report, sum_post_in_city = get_sales_data(date_start, date_finish, status)
    create_table(report, sum_post_in_city)
