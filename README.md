# Running Performance Tests:
### On Sandbox:
* Make sure your kube config is pointing towards the performance sandbox:
  * Context: `uksouth-sandbox`
  * Namespace: `perf-api-v1` or `perf-api-v2`
* Port forward to sandbox locust web ui:
  * `kubectl port-forward <locust master pod name> 8089`
* Open up web ui by going to below link:
  * `localhost:8089`
* Enter required users and push `Start swarming`
  * `Total users`: How many users you want running the test at once
  * `Spawn rate`: How many users are spun up per second until it reaches
                 total users


### Local:
*  **Note: The above setup works by sending a request from OUTSIDE our systems, which will result in a slower performance.
   For more accurate performance measurements, the locust_files should be run directly from the performance sandbox
   (as above).**
* You will need to have your .env file set up correctly in order to run locust locally:
  * `VAULT_URL=https://bink-uksouth-perf-com.vault.azure.net `
  * `CHANNEL_VAULT_PATH=channels`
  * `HERMES_URL=https://performance.sandbox.gb.bink.com`
  * `DB_CONNECTION_URI=***`
  * `LOCAL_SECRETS=False`

* If running data population, the `DB_CONNECTION_URI` env variable will need to be set to the current Postgres flexible server db connection string.
  * To get this, run `kubectl port-forward deploy/proxy-postgres 5432`
  * Then `echo $(kubectl get secret azure-pgfs -o json | jq -r .data.common_postgres | base64 --decode)`
  * set the `DB_CONNECTION_URI` env variable to the echoed value.
  * (N.b. This is a rolling variable, so you may need to update this variable later on)

* Run locust web ui pointing at sandbox:
  * `poetry run locust --host=https://performance.sandbox.gb.bink.com --locustfile=PATH_TO_FILE` (where PATH_TO_FILE is
    the path to the locustfile you would like to run (e.g. `locust_angelia/locustfile_peak_hour.py`))
* Open up web ui by going to below link:
  * `localhost:8089`
* Enter required users and push `Start swarming`
  * `Total users`: How many users you want running the test at once
  * `Spawn rate`: How many users are spun up per second until it reaches
                 total users


# Database Population:
To populate the Hermes and Hades database with test data, you can run the below CLI commands.
They will create TSV files, then upload those to the correct postgres tables.

Commands can take two arguments (except `upload-tsv` which only takes one, see below)
* `--group-config`: Defaults to `all`, defines what type of data will be created and / or uploaded.
This allows us to spin up multiple uploader pods and perform multiple uploads at once (e.g. one pod
uploading hermes data, one pod uploading hermes history data, one pod uploading hades transactions).
See below for options:
  * `hermes`
  * `hermeshistory`
  * `hades`
  * `all`

* `--size-config`: Defaults to `test`, defines how many test data is going to be generate.
See `data_populdate/data_population_config.py` for how much data each option creates. See below
for options:
  * `test`
  * `benchmark`
  * `barclays_2021`
  * `barclays_2022`
  * `barclays_2023`
  * `barclays_2024`
  * `barclays_internal_test`

**data-population populate-db:**
Used to both create and upload the tsv files.
```
populate-db -g <group config> -s <size config>
populate-db --group-config <group config> -size-config <size config>

example:
populate-db -g all -s benchmark
```

**data-population create-tsv:**
Used to only create the TSV files
```
create-tsv -g <group config> -s <size config>
create-tsv --group-config <group config> -size-config <size config>

example:
create-tsv --group-config hermes -size-config barclays_2021
```

**data-population upload-tsv:**
Used to only upload existing TSV files for a given group-config, allows us to retry if an upload fails
without having to regenerate the TSV files
```
upload-tsv -g <group config>
upload-tsv --group-config <group config>

example:
upload-tsv -g hades
```

# More Information:

* For more on this, including how to configure locust files in-code, see: https://hellobink.atlassian.net/wiki/spaces/BD/pages/1666056320/Ubiquity+Angelia+Performance+Testing
