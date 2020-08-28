TODO:
* Finish readme with below topics:
  * setting up local secrets

# Running Performance Tests:
### On Sandbox:
* Make sure your kube config is pointing towards the performance sandbox:
  * Context: `uksouth-sandbox`
  * Namespace: `performance`
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
  * `pipenv run locust --host=https://performance.sandbox.k8s.uksouth.bink.sh/ubiquity`
* Open up web ui by going to below link:
  * `localhost:8089`
* Enter required users and push `Start swarming`
  * `Total users`: How many users you want running the test at once
  * `Hate rate`: How many users are spun up per second until it reaches 
                 total users

# Environment Setup:
### Database Population:
* Set the correct fixture totals in `data_population/create_tsv.py`
* Run the data population script:
  * `pipenv run data_population/create_tsv.py`
* Make sure your kube config is pointing towards the performance sandbox:
  * Context: `uksouth-sandbox`
  * Namespace: `performance`
* Setup `.env` with sandbox db connection details
* Port forward to the sandbox db:
  * `kubectl port-forward <hermes api pod name> 5432`
* Upload the created data to the db (WARNING: this will start 
  by deleting all data in the environment):
  * `pipenv run data_population/upload_tsv.py`

### Vault Setup:
This only has to happen once per environment, unless you want to change 
the performance client secrets in an existing environment.
* Copy the vault secrets from 1password (`Performance Vault Secrets`)
* Paste these secrets to replace the examples in `data_population/fixtures/client.py`
* Port forward to the vault:
  * `kubectl port-forward vault-0 8200` 
* Make sure your `.env` has the `VAULT_URL` and `VAULT_TOKEN` env vars populated
* Run the vault setup script:
  * `pipenv run data_population/vault_setup.py`
