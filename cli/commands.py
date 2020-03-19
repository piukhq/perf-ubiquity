import click

from data_population.create_tsv import create_tsv_files
from data_population.upload_tsv import upload_tsv_files


@click.command()
def populate_db():
    create_tsv_files()
    upload_tsv_files()


@click.command()
def upload_tsv():
    upload_tsv_files()
