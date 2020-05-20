from syntext.utils.utils import dynamic_load
from syntext.text.text_generator import TextGenerator

module_name = "syntext.text.generator"
modules = dynamic_load(module_name, TextGenerator)
for module in modules:
    print(module)

# RUN: python -m syntext.test.test_dynamical_load_classes