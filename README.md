# 项目概述

这个项目用于生成训练过程中的样本。

实现了以下功能：
- 可以基于字库随机生成，并且可以配置数字、日期、汉字、混英文等各自的生成概率
- 可以基于语料生成，从语料中随机截取片段文字进行生成
- 可以支持多种效果进行增强：变形、剪切、噪音、模糊等
- 可以支持多种字体和多种背景（可定制）
- 可以支持只产生文本样本，也支持带有每个字坐标标注的样本

## 参考

此项目参考了以下的开源项目：

- <https://github.com/mdbloice/Augmentor>
- <https://github.com/wang-tf/Chinese_OCR_synthetic_data>
- <https://github.com/JarveeLee/SynthText_Chinese_version>
- <https://github.com/Belval/TextRecognitionDataGenerator.git>
- <https://github.com/Sanster/text_renderer>

## 设计思路

样本生成主要需要做一下工作：

- 加载资源，如（字体、背景图）
- 支持多进程，提高效率
- 各种策略来生成文字
- 各种策略来增强生成的图片

所以，实现的大抵思路也是如此：

1、先加载字体、背景、字符集、字库

2、生成一个串文本

3、画文本到背景上，并确定bbox

4、使用开源项目[imgaug](https://imgaug.readthedocs.io/en/latest/)做增强

5、保存图片、标签、和bbox


# 两种生成方式

目前，项目实现了两种样本的生成：

1、仅生成图片和对应的文字标签

2、生成图片和对应的文字标签，还要包含每个字的bbox信息

## 生成识别样本（仅有字符标注）

这种标注，对每个文件，仅提供其对应的字符串，不靠谱中文中的全角半角，需要程序自己进行转换。

标注文件只有一个，如train.txt。文件分为2列：文件路径、对应文字。

样例：

```text
data/train/abc.jpg 你好，世界
data/train/bcd.jpg 毁灭吧，世界！累了~
......
```

## 生成带位置信息的识别样本

这种样本，是标注了每个字符的轮廓的，每个字的轮廓采用4点标注。
第一行是样本对应的字符串，第2行至最后一行，是每个汉字的4点标注，和对应的汉字。

**样例：**

所有样例存放在一个文件夹里，每张图片有唯一的名字，而标注的文件名字一样，只是后缀为.txt。

图像文件名：abc.jpg

标注文件名：abc.txt

标注文件样例：
```text
你好，世界                      <---- 第1行，标注结果
11,12,21,22,31,32,41,42 你     <---- 第2行-最后一行，标注每个文字的框
11,12,21,22,31,32,41,42 好
11,12,21,22,31,32,41,42 ，
11,12,21,22,31,32,41,42 世
11,12,21,22,31,32,41,42 界
```

# 使用

## 运行程序
运行[bin/run.sh](bin/run.sh)可以生成图像，格式如下：
```text
bin/run.sh --dir output_dir --num number --config config/config.yml <--debug>
```
- dir：样本生成目录
- num：生成多个张
- debug：是否显示更多的运行信息
- config: 使用的配置文件

【三种默认配置】

目前提供了3种默认配置，方便各类样本生成：

- config/config.contour.yml: 生成带有轮廓标注的随机文本
- config/config.corpus.yml:  生成基于语料的，仅有文本标注的样本
- config/config.captcha.yml: 生成仅包含数字和字母的用于验证码识别的样本

你还可以根据给出的配置，微调你的生成参数。

## 配置

为了控制运行细节，需要配置[config.yml](config.yml)：

- 做随机生成
```text
COMMON:
    TEXT_GENERATOR : random     # 随机生成:random, 语料生成:corpus
```

- 基于语料生成
```text
COMMON:
    TEXT_GENERATOR : corpus     # 随机生成:random, 语料生成:corpus
```

- 只生成文本
```text
COMMON:
    GENERATOR : text         # 保存轮廓的:contour, 只保存标签: text
```

- 生成文本，和每个字的坐标
```text
COMMON:
    GENERATOR : contour         # 保存轮廓的:contour, 只保存标签: text
```

以上配置都可以组合使用，更详细的配置，可直接参考配置文件中的注释。

## 相关资源

**运行前，需要先下载背景（各类白纸）和字体资源**：

[百度云盘下载](https://pan.baidu.com/s/1RU-JAnz7mP6w0REIXby0Zg)  提取码: 2rbd

并放置到 data/目录下。
