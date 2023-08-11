from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich.text import Text

from constants import LIST_ERROR_OZON


def create_table(report, numb_shipment_countries):
    if report:
        table = Table(
            title="Data sell OZON", title_style="#00ab98",
            expand=True, show_lines=True, style="#f6c42d"
            )

        table.add_column("posting_number", justify="center", overflow='fold', max_width=7)
        table.add_column("shipment_date", justify="center", overflow='fold', max_width=10)
        table.add_column("price", justify="center", overflow='fold', max_width=6)
        table.add_column("name", justify="left",  overflow='fold', min_width=15)
        table.add_column("quantity", overflow='fold', justify="center", max_width=7)
        table.add_column("cluster_delivery",  overflow='fold', justify="left", max_width=10)

        for item in report:
            item_out = edit_item(item)
            table.add_row(
                item_out['posting_number'], item_out['shipment_date'],
                item_out['price'], item_out['name'], item_out['quantity'],
                item_out['cluster_delivery']
                )

        console = Console()
        console.print(table)
        print_sum_post(numb_shipment_countries)
    else:
        get_color_message('Отчет не содержит данных', 'info')


def edit_item(item):
    item['shipment_date'] = item.get('shipment_date')[:10]
    item['price'] = '%.2f' % float(item.get('price'))
    item['quantity'] = str(item['quantity'])
    text = Text(item['cluster_delivery'])

    if item['cluster_delivery'] == 'Армения':
        text.stylize("magenta")
    elif item['cluster_delivery'] == 'Беларусь':
        text.stylize("#009ce9")
    elif item['cluster_delivery'] == 'Киргизия':
        text.stylize("yellow")
    elif item['cluster_delivery'] == 'Казахстан':
        text.stylize("green")
    else:
        text.stylize("red")

    item['cluster_delivery'] = text
    return item


def print_sum_post(report):
    if report:
        get_color_message('\nВсего отправлений по странам\n', 'info')
        for country in report:
            print(f'{country[0]} - {country[1]} шт.')


def get_color_message(message, tag):
    custom_theme = Theme({
        'info': 'yellow',
        'error': 'red'
    })

    console = Console(theme=custom_theme)
    console.print(message, style=tag)


def output_error(code):
    if code in LIST_ERROR_OZON:
        text = f'{code}: {LIST_ERROR_OZON.get(code)}'
    else:
        text = 'Ошибка не идентифицирована'
    get_color_message(text, 'info')
