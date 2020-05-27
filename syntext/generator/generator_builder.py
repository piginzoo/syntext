from syntext.generator.contour_generator import ContourGenerator
from syntext.generator.text_generator import TextOnlyGenerator
from syntext.text.corpus_creator import CorpusTextCreator
from syntext.text.random_creator import RandomTextCreator
from syntext.augmentor import Augumentor
import logging

logger = logging.getLogger(__name__)

class GeneratorBuilder():

    def build(self, config, charset, fonts, backgrounds):
        logger.info("创建生成器：")
        logger.info("----------------------------------------")

        # 图像增强
        augmentor = Augumentor(config)
        logger.info("\t创建增强器\t：使用imgaug做图像增强")

        # 文本创建器
        if config.COMMON['TEXT_CREATOR'] == "random":
            logger.info("\t创建文本生成器\t：随机产生文本")
            text_creator = RandomTextCreator(config, charset)
        if config.COMMON['TEXT_CREATOR'] == "corpus":
            text_creator = CorpusTextCreator(config)
            logger.info("\t创建文本生成器\t：从语料中抽取文本")

        # 标签保存器
        if config.COMMON['GENERATOR'] == "contour":
            generator = ContourGenerator(config, charset, fonts, backgrounds, text_creator, augmentor)
            logger.info("\t创建样本保存器\t：保存每个字的坐标")
        if config.COMMON['GENERATOR'] == "text":
            generator = TextOnlyGenerator(config, charset, fonts, backgrounds, text_creator, augmentor)
            logger.info("\t创建样本保存器\t：仅保存字符串")

        logger.info("----------------------------------------")
        return generator
