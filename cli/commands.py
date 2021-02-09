from enum import Enum

import click

from data_population import data_population_config
from data_population.database_tables import HermesTables, HermesHistoryTables, HadesTables
from data_population.tsv_generation import hermes, hermes_history, hades
from data_population.upload_tsv import upload_named_group_of_tsv_files
from settings import HADES_DB, HERMES_DB


class DataGroups(str, Enum):
    ALL = "all"
    HERMES = "hermes"
    HERMESHISTORY = "hermeshistory"
    HADES = "hades"


GROUP_CONFIG_HELP = (f"Group of data you wish to interact with, defaults to 'all', "
                     f"please choose from: {[group.value for group in DataGroups]}")
SIZE_CONFIG_HELP = (f"Size of data population, defaults to 'test', "
                    f"please choose from: {data_population_config.all_config_names}")
BAD_GROUP_CONFIG_ERROR = f"Invalid group config entered, please enter one from: {[group.value for group in DataGroups]}"
BAD_SIZE_CONFIG_ERROR = f"Invalid size config entered, please enter one from {data_population_config.all_config_names}"


data_mapping = {
    DataGroups.HERMES: {
        "data_creation_modules": [hermes],
        "upload_lists": [
            {"database": HERMES_DB, "tables": HermesTables}
        ]
    },
    DataGroups.HERMESHISTORY: {
        "data_creation_modules": [hermes_history],
        "upload_lists": [
            {"database": HERMES_DB, "tables": HermesHistoryTables}
        ]
    },
    DataGroups.HADES: {
        "data_creation_modules": [hades],
        "upload_lists": [
            {"database": HADES_DB, "tables": HadesTables}
        ]
    },
    DataGroups.ALL:
        {
            "data_creation_modules": [hermes, hermes_history, hades],
            "upload_lists": [
                {"database": HERMES_DB, "tables": HermesTables},
                {"database": HERMES_DB, "tables": HermesHistoryTables},
                {"database": HADES_DB, "tables": HadesTables}
            ]
        }
}


@click.command()
@click.option("-g", "--group-config", default="all", help=GROUP_CONFIG_HELP)
@click.option("-s", "--size-config", default="test", help=SIZE_CONFIG_HELP)
def create_tsv(group_config: str, size_config:str):
    """Creates the requested tsv files

    """
    if group_config not in list(DataGroups):
        raise ValueError(BAD_GROUP_CONFIG_ERROR)
    if size_config not in data_population_config.all_config_names:
        raise ValueError(BAD_SIZE_CONFIG_ERROR)

    size_config = getattr(data_population_config, size_config)

    data_creation_modules = data_mapping[group_config]["data_creation_modules"]
    for data_creation_module in data_creation_modules:
        data_creation_module.create_tsv_files(size_config)


@click.command()
@click.option("-g", "--group-config", default="all", help=GROUP_CONFIG_HELP)
def upload_tsv(group_config: str):
    """Uploads the requested tsv files

    The 'create-tsv' command must have been previously run to ensure these files exist
    """
    if group_config not in list(DataGroups):
        raise ValueError(BAD_GROUP_CONFIG_ERROR)

    all_data_to_upload = data_mapping[group_config]["upload_lists"]
    for data_to_upload in all_data_to_upload:
        upload_named_group_of_tsv_files(data_to_upload["database"], data_to_upload["tables"])


@click.command()
@click.option("-g", "--group-config", default="all", help=GROUP_CONFIG_HELP)
@click.option("-s", "--size-config", default="test", help=SIZE_CONFIG_HELP)
def populate_db(group_config: str, size_config: str):
    """Creates and uploads the requested tsv files"""
    if group_config not in list(DataGroups):
        raise ValueError(BAD_GROUP_CONFIG_ERROR)
    if size_config not in data_population_config.all_config_names:
        raise ValueError(BAD_SIZE_CONFIG_ERROR)

    size_config = getattr(data_population_config, size_config)

    data_creation_modules = data_mapping[group_config]["data_creation_modules"]
    for data_creation_module in data_creation_modules:
        data_creation_module.create_tsv_files(size_config)

    all_data_to_upload = data_mapping[group_config]["upload_lists"]
    for data_to_upload in all_data_to_upload:
        upload_named_group_of_tsv_files(data_to_upload["database"], data_to_upload["tables"])
