import redis
import json

def read_json_file(file_name):
    with open(file_name, 'r') as file:
        dati_json = json.load(file)
    return dati_json

if __name__ == '__main__':
    # connessione al database
    database = redis.Redis(host='redis', port=6379, db=0)

    file_name = 'Configuration.json'
    configuration_data = read_json_file(file_name)
    database.set('Config_data', json.dumps(configuration_data))


