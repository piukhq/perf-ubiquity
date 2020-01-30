#!/bin/bash
TSV_FOLDER="tsv"
psql -h 127.0.0.1 -p 5432 --user "laadmin@bink-dev-uksouth" -d mcwallet_hermes -c "\copy user_organisation FROM '$TSV_FOLDER/user_organisation.tsv' DELIMITER E'\t'"
psql -h 127.0.0.1 -p 5432 --user "laadmin@bink-dev-uksouth" -d mcwallet_hermes -c "\copy user_clientapplication FROM '$TSV_FOLDER/user_clientapplication.tsv' DELIMITER E'\t'"
psql -h 127.0.0.1 -p 5432 --user "laadmin@bink-dev-uksouth" -d mcwallet_hermes -c "\copy user_clientapplicationbundle FROM '$TSV_FOLDER/user_clientapplicationbundle.tsv' DELIMITER E'\t'"
psql -h 127.0.0.1 -p 5432 --user "laadmin@bink-dev-uksouth" -d mcwallet_hermes -c "\copy scheme_scheme FROM '$TSV_FOLDER/scheme_scheme.tsv' DELIMITER E'\t'"
psql -h 127.0.0.1 -p 5432 --user "laadmin@bink-dev-uksouth" -d mcwallet_hermes -c "\copy scheme_schemecredentialquestion FROM '$TSV_FOLDER/scheme_schemecredentialquestion.tsv' DELIMITER E'\t'"
psql -h 127.0.0.1 -p 5432 --user "laadmin@bink-dev-uksouth" -d mcwallet_hermes -c "\copy scheme_schemebundleassociation FROM '$TSV_FOLDER/scheme_schemebundleassociation.tsv' DELIMITER E'\t'"
