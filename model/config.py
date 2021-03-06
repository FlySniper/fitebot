from time import sleep
import yaml

import model


def openConfig():
    with open("config.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


config = openConfig()


def refreshConfig():
    while True:
        sleep(60 * 60 * 1)  # One hour
        model.config.config = openConfig()
