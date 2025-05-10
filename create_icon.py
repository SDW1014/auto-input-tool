from PIL import Image, ImageDraw
import os

# 아이콘 크기
size = 256
image = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# 마우스 모양 그리기
# 마우스 본체
draw.rounded_rectangle([(60, 40), (196, 180)], radius=30, fill=(220, 220, 220, 255), outline=(50, 50, 50, 255), width=3)

# 마우스 버튼 구분선
draw.line([(128, 40), (128, 140)], fill=(120, 120, 120, 255), width=2)

# 마우스 휠
draw.ellipse([(113, 90), (143, 110)], fill=(100, 100, 100, 255), outline=(70, 70, 70, 255), width=2)

# 마우스 케이블
draw.line([(128, 180), (128, 216)], fill=(50, 50, 50, 255), width=4)

# 왼쪽 클릭 표시 (빨간색)
draw.ellipse([(95, 65), (115, 85)], fill=(255, 80, 80, 255), outline=(200, 30, 30, 255), width=2)

# 아이콘 저장
image.save('mouse_icon.png')

# ico 파일 생성 (윈도우용)
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
image.save('mouse_icon.ico', sizes=sizes)

print("아이콘이 생성되었습니다: mouse_icon.ico") 