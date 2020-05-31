from PIL import Image, ImageFont

def word(c):
	font = ImageFont.truetype('data/fonts/simsun.ttc', 10)
	ascent, descent = font.getmetrics()
	(width, baseline), (offset_x, offset_y) = font.font.getsize(c)
	print("ascent:",ascent)
	print("descent:",descent)
	print("(width, baseline):",(width, baseline))
	print("(offset_x, offset_y):", (offset_x, offset_y))
	print("ascent-offset_y:",ascent-offset_y)


s = "我 a 对的）。.;(!... 12345"