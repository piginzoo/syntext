import yaml


class Config():

    def __init__(self,config_file_path):
        f = open(config_file_path, encoding='utf-8')
        y = yaml.load(f)
        for (k, v) in y.items():
            self.__dict__[k] = v
        f.close()
