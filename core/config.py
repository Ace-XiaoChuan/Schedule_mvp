from pathlib import Path
import configparser


class Appconfig:
    def __init__(self):
        # 实例化一个配置解析器对象，用来以后读、写、修ini
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # 路径配置
        self.BASE_DIR = Path(__file__).parent.parent  # schedule
        self.DB_PATH = self.BASE_DIR / self.config['PATHS']['database']  # 后半：读取配置文件中 [PATHS] 节下 database 键对应的相对路径
        self.MODEL_DIR = self.BASE_DIR / self.config['PATHS']['models']

        # 模型参数
        self.MAX_FEATURES = int(self.config['MODEL']['max_features'])  # 5000/100先这么多
        self.N_ESTIMATORS = int(self.config['MODEL']['n_estimators'])
