from enum import StrEnum
from typing import TYPE_CHECKING

import typer

from ubiquity_performance_test.config import settings
from ubiquity_performance_test.data_population import data_population_config
from ubiquity_performance_test.data_population.database_tables import HadesTables, HermesHistoryTables, HermesTables
from ubiquity_performance_test.data_population.generate_harmonia_data import write_token_slug_mapping_file
from ubiquity_performance_test.data_population.tsv_generation import hades, hermes, hermes_history
from ubiquity_performance_test.data_population.upload_tsv import upload_named_group_of_tsv_files

if TYPE_CHECKING:
    from typing import TypedDict

    class DataMappingPayloadType(TypedDict):
        data_creation_modules: list
        upload_lists: list[dict]


app = typer.Typer(no_args_is_help=True)


class DataGroups(StrEnum):
    ALL = "all"
    HERMES = "hermes"
    HERMESHISTORY = "hermeshistory"
    HADES = "hades"


GROUP_CONFIG_HELP = (
    f"Group of data you wish to interact with, defaults to 'all', "
    f"please choose from: {[group.value for group in DataGroups]}"
)
SIZE_CONFIG_HELP = (
    f"Size of data population, defaults to 'test', " f"please choose from: {data_population_config.all_config_names}"
)
BAD_GROUP_CONFIG_ERROR = f"Invalid group config entered, please enter one from: {[group.value for group in DataGroups]}"
BAD_SIZE_CONFIG_ERROR = f"Invalid size config entered, please enter one from {data_population_config.all_config_names}"


data_mapping: dict[DataGroups, "DataMappingPayloadType"] = {
    DataGroups.HERMES: {
        "data_creation_modules": [hermes],
        "upload_lists": [{"database": settings.HERMES_DB, "tables": HermesTables}],
    },
    DataGroups.HERMESHISTORY: {
        "data_creation_modules": [hermes_history],
        "upload_lists": [{"database": settings.HERMES_DB, "tables": HermesHistoryTables}],
    },
    DataGroups.HADES: {
        "data_creation_modules": [hades],
        "upload_lists": [{"database": settings.HADES_DB, "tables": HadesTables}],
    },
    DataGroups.ALL: {
        "data_creation_modules": [hermes, hermes_history, hades],
        "upload_lists": [
            {"database": settings.HERMES_DB, "tables": HermesTables},
            {"database": settings.HERMES_DB, "tables": HermesHistoryTables},
            {"database": settings.HADES_DB, "tables": HadesTables},
        ],
    },
}


@app.command()
def create_tsv(
    group_config: DataGroups = typer.Option("all", "-g", "--group-config", prompt=True, help=GROUP_CONFIG_HELP),
    size_config: str = typer.Option("test", "-s", "--size-config", prompt=True, help=SIZE_CONFIG_HELP),
) -> None:
    """Creates the requested tsv files"""
    if group_config not in list(DataGroups):
        raise ValueError(BAD_GROUP_CONFIG_ERROR)

    if size_config not in data_population_config.all_config_names:
        raise ValueError(BAD_SIZE_CONFIG_ERROR)

    size_config_class = getattr(data_population_config, size_config)

    data_creation_modules = data_mapping[group_config]["data_creation_modules"]
    for data_creation_module in data_creation_modules:
        data_creation_module.create_tsv_files(size_config_class)


@app.command()
def upload_tsv(
    group_config: DataGroups = typer.Option("all", "-g", "--group-config", prompt=True, help=GROUP_CONFIG_HELP)
) -> None:
    """Uploads the requested tsv files

    The 'create-tsv' command must have been previously run to ensure these files exist
    """
    if group_config not in list(DataGroups):
        raise ValueError(BAD_GROUP_CONFIG_ERROR)

    all_data_to_upload = data_mapping[group_config]["upload_lists"]
    for data_to_upload in all_data_to_upload:
        upload_named_group_of_tsv_files(data_to_upload["database"], data_to_upload["tables"])


@app.command()
def populate_db(
    group_config: DataGroups = typer.Option("all", "-g", "--group-config", prompt=True, help=GROUP_CONFIG_HELP),
    size_config: str = typer.Option("test", "-s", "--size-config", prompt=True, help=SIZE_CONFIG_HELP),
) -> None:
    """Creates and uploads the requested tsv files"""
    if group_config not in list(DataGroups):
        raise ValueError(BAD_GROUP_CONFIG_ERROR)
    if size_config not in data_population_config.all_config_names:
        raise ValueError(BAD_SIZE_CONFIG_ERROR)

    size_config_class: data_population_config.DataConfig = getattr(data_population_config, size_config)

    data_creation_modules = data_mapping[group_config]["data_creation_modules"]
    for data_creation_module in data_creation_modules:
        data_creation_module.create_tsv_files(size_config_class)

    all_data_to_upload = data_mapping[group_config]["upload_lists"]
    for data_to_upload in all_data_to_upload:
        upload_named_group_of_tsv_files(data_to_upload["database"], data_to_upload["tables"])
    if group_config not in ("hades", "hermeshistory") and size_config_class.real_plans:
        write_token_slug_mapping_file()


if __name__ == "__main__":
    app()
