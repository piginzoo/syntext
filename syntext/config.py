import yaml


class Config():

    def __init__(self):
        f = open(r'config.yml', encoding='utf-8')
        y = yaml.load(f)
        for (k, v) in y.items():
            self.__dict__[k] = v
        f.close()
