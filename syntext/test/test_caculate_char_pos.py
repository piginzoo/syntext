from PIL import Image, ImageDraw, ImageFont

# 测试，是否坐标都正确？
# python test_caculate_char_pos.py && see debug/test.jpg

def size(text,font):
    return font.getsize(text)

def create_image(str):
    font = ImageFont.truetype("../../data/font/simsun.ttc", 20)

    image = Image.new('RGB', (256,64),color=(255,255,255))
    draw = ImageDraw.Draw(image)

    offset = 20
    height = 20

    draw.text((offset, height), str, fill=(0, 0, 0), font=font)

    for c in str:
        w,h = size(c,font)
        _w = w - 3
        if c == " ":
            offset += w
            continue

        draw.rectangle([(offset,height),(offset+ _w,height+h)],outline ="red")
        offset += w

    image.save("debug/test.jpg")

if __name__=="__main__":
    # python test_caculate_char_pos.py && see debug/test.jpg
    create_image("  12   一 二  三四；;，,")