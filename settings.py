import utils

settings = {}

def save(filename):
    utils.savejson(filename,settings)

def load(defaultsettings,filename):
    global settings
    filename = filename
    settings = {**defaultsettings,**utils.loadjson(filename)}
    save(filename)

def get(set):
    return settings[set]