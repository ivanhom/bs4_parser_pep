import csv
import datetime as dt
import logging
from argparse import Namespace

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, ENCODING_STANDART, OutputType


def control_output(results: list[tuple], cli_args: Namespace) -> None:
    """Определение метода вывода информации."""
    output = cli_args.output
    if output == OutputType.PRETTY:
        pretty_output(results)
    elif output == OutputType.FILE:
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results: list[tuple]) -> None:
    """Вывод информации в виде строк в терминал."""
    for row in results:
        print(*row)


def pretty_output(results: list[tuple]) -> None:
    """Вывод информации в виде таблицы в терминал."""
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results: list[tuple], cli_args: Namespace) -> None:
    """Вывод информации в виде файла csv."""
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding=ENCODING_STANDART) as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
