from syntext.contour_generator import ContourGenerator



def __load_background():
    pass

# 提前生成所有字体的不同字号的字体
def __load_fonts():
    fonts = []
    for font_name in font_files:
        # 字号随机
        font_size = random_font_size()
        # 随机选取字体大小、颜色、字体
        font_name = random_font(font_dir)

        font = ImageFont.truetype(font_name, font_size)
        fonts.append(font)

if __name__=="__main__":
    fonts = __load_fonts()
    backgrounds = __load_background()
    generator = ContourGenerator(fonts, backgrounds)

    generator.execute()