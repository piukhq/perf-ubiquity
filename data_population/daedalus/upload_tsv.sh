#!/bin/bash
TSV_FOLDER="tsv"
psql -h 127.0.0.1 -p 5432 --user "postgres" -d daedalus -c "\copy membership_plan FROM '$TSV_FOLDER/membership_plan.tsv' DELIMITER E'\t'"
psql -h 127.0.0.1 -p 5432 --user "postgres" -d daedalus -c "\copy channel FROM '$TSV_FOLDER/channel.tsv' DELIMITER E'\t'"
psql -h 127.0.0.1 -p 5432 --user "postgres" -d daedalus -c "\copy channel_membership_plan_whitelist FROM '$TSV_FOLDER/channel_membership_plan_whitelist.tsv' DELIMITER E'\t'"

