# Running Performance Tests:
### On Sandbox:
* Make sure your kube config is pointing towards the performance sandbox:
  * Context: `uksouth-perf0`
  * Namespace: `default`
* Port forward to sandbox locust web ui:
  * `kubectl port-forward <locust master pod name> 8089`
* Open up web ui by going to below link:
  * `localhost:8089`
* Enter required users and push `Start swarming`
  * `Total users`: How many users you want running the test at once
  * `Hate rate`: How many users are spun up per second until it reaches 
                 total users

### Local: 
* Run locust web ui pointing at sandbox:
  * `pipenv run locust --host=https://performance.sandbox.gb.bink.com/ubiquity`
* Open up web ui by going to below link:
  * `localhost:8089`
* Enter required users and push `Start swarming`
  * `Total users`: How many users you want running the test at once
  * `Hate rate`: How many users are spun up per second until it reaches 
                 total users

# Environment Setup:
### Database Population:
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

**populate-db:**  
Used to both create and upload the tsv files.  
```
populate-db -g <group config> -s <size config>
populate-db --group-config <group config> -size-config <size config>

example:
populate-db -g all -s benchmark
```

**create-tsv:**  
Used to only create the TSV files  
```
create-tsv -g <group config> -s <size config>
create-tsv --group-config <group config> -size-config <size config>

example:
create-tsv --group-config hermes -size-config barclays_2021
```

**upload-tsv:**  
Used to only upload existing TSV files for a given group-config, allows us to retry if an upload fails
without having to regenerate the TSV files
```
upload-tsv -g <group config>
upload-tsv --group-config <group config>

example:
upload-tsv -g hades
```
