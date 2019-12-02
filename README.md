# DB Setup:

#### Initial setup
* If using a new database:
  * Create the database in postgres if it doesn't exist: 
  `psql -h 127.0.0.1 -p 5432 --user postgres -c "CREATE DATABASE hermes"`
* If using an existing database:
  * Take a back-up which we will restore to after the test is complete: 
  `pg_dump -h 127.0.0.1 -p 5432 --user postgres hermes > hermes.bak`

#### Data population
* Run tsv generation scrips: `pipenv run python db/hermes/create_tsv.py`
* Import each of the tsv files into the postgres database

#### Performance testing:
* Connect to locust:
  * Local:
    * `pipenv install`
    * `pipenv run locust --host=http://127.0.0.1:8081/ubiquity`
  * Deployed:
    * Port forward locust pod: `kubectl port-forward <pod name> 8089`
* Open locust web ui: `https://localhost:8089`
* Enter total number of users and hatch rate and click "Start swarming"
  * Hatch rate is how many users spawn per second until total number of users is reached
 
#### Post performance test
* After running performance test, use the initial backup to restore
  the database: `psql -h 127.0.0.1 -p 5432 --user postgres hermes < hermes.bak`

# TODO
* Finish PUT and PATCH endpoints 
* Fix script running bug
* Finish readme on how to import tsv files
* Add test performance scripts to allowed schemes for endpoints
* Set up midas performance-test slug agent to always return balance
* Get CI changes from infrastructure to build
* Have error scenarios (try adding a fully restricted test 
  scheme (added by data population script)) tested + adding 
  already existed cards

## Environment variables:
* JWT_SECRET - Secret used in authentication token generation
