class TextGenerator():
    """
    这个类是父类，用来定义某种类型的文本生成
    """

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def random_accept(accept_possibility):
        return np.random.choice([True,False], p = [accept_possibility,1 - accept_possibility])

    def generate(self):
        raise NotImplementedError("子类实现")