from setuptools import setup, find_packages

setup(
    name='ubiquity-performance-test',
    version='1.0',
    packages=["."] + find_packages(),
    entry_points={
        "console_scripts": (
            "populate-db=cli.commands:populate_db",
            "upload-tsv=cli.commands:upload_tsv",
        )
    },
)
