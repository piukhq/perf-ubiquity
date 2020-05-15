import click

from data_population.create_tsv import create_tsv_files
from data_population.upload_tsv import upload_all_tsv_files, upload_single_tsv_file


@click.command()
def create_tsv():
    create_tsv_files()


@click.command()
def populate_db():
    create_tsv_files()
    upload_all_tsv_files()


@click.command()
def upload_tsv_files():
    upload_all_tsv_files()


@click.command()
@click.argument('db_name')
@click.argument('table_name')
def upload_tsv_file(db_name, table_name):
    if db_name not in ['hermes', 'hades']:
        raise ValueError('Please choose db_name from "hermes" or "hades"')

    upload_single_tsv_file(db_name, table_name)
