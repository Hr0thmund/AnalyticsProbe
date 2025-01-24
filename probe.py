import configparser

def survey_ips(ip_list):



config = configparser.ConfigParser()
config.read('config.ini')

targets = dict(config['TARGETS'])

print(targets)
