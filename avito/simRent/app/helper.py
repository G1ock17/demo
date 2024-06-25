import configparser


def load_config(path: str, block: str):
    config = configparser.ConfigParser()
    config.read(path)

    return config[block]


if __name__ == '__main__':
    t = int(input('Minutes:'))
    print(t)
