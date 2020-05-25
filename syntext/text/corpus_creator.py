from syntext.text.creator import TextCreator
import random,logging

logger = logging.getLogger(__name__)

class CorpusTextCreator(TextCreator):
    """
    基于语料的文本生成器
    """
    def __init__(self,config):
        self.config = config
        file = open(config.CORPUS['FILE'])
        self.content = file.read(config.CORPUS['MAX_LENGHT'])
        self.length = len(self.content)
        logger.info("加载了语料文件[%s] %d 行", config.CORPUS['FILE'], self.length)
        file.close()

    def generate(self):
        len = random.randint(self.config.MIN_LENGTH,self.config.MAX_LENGTH)
        pos = random.randint(0,self.length-len-1)
        data = self.content[pos:(pos+len)]
        data = data.replace("\n","")
        return data