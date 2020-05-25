from syntext.generator.contour_generator import ContourGenerator
from syntext.generator.text_generator import TextOnlyGenerator
from syntext.text.corpus_creator import CorpusTextCreator
from syntext.text.random_creator import RandomTextCreator
from syntext.augmentor import Augumentor


class GeneratorBuilder():

    def build(self, config, charset, fonts, backgrounds):
        # 图像增强
        augmentor = Augumentor(config)

        # 文本创建器
        if config.COMMON['TEXT_CREATOR'] == "random":
            text_creator = RandomTextCreator(config, charset)
        if config.COMMON['TEXT_CREATOR'] == "corpus":
            text_creator = CorpusTextCreator(config)

        # 标签保存器
        if config.COMMON['GENERATOR'] == "contour":
            generator = ContourGenerator(config, charset, fonts, backgrounds, text_creator, augmentor)
        if config.COMMON['GENERATOR'] == "text":
            generator = TextOnlyGenerator(config, charset, fonts, backgrounds, text_creator, augmentor)

        return generator
