import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="이미지 + 텍스트 결합기", layout="centered")
st.title("🖼️ 이미지 + 텍스트 결합기")

st.markdown("""
1. 이미지를 업로드 해주세요.  
2. 텍스트 입력 후 `Ctrl + Enter` 를 누르면 이미지가 생성됩니다.
""")

# 📂 이미지 업로드
uploaded_image = st.file_uploader("이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

# 📝 텍스트 입력
input_text = st.text_area("텍스트 입력 (Ctrl + Enter로 적용)", height=150)

# 💾 저장할 파일명
file_name = st.text_input("저장할 파일 이름 (확장자 제외)", value="merged_image")

# 🔤 글씨 크기 선택 (0이면 자동 조정)
custom_font_size = st.number_input("글씨 크기 (0 = 자동)", min_value=0, max_value=100, value=0)

# 📐 정렬 선택
alignment = st.selectbox("텍스트 정렬 방식", ["left", "center", "right"], index=0)

# 폰트
font_path = "NanumGothic.ttf"  # 폰트는 함께 업로드

def wrap_text_by_pixel(draw, text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split()
        line = ""
        for word in words:
            test_line = line + (' ' if line else '') + word
            width = draw.textlength(test_line, font=font)
            if width <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        elif not words:
            lines.append("")  # 빈 줄 유지
    return lines

# 실행 조건
if uploaded_image and input_text and file_name:
    image = Image.open(uploaded_image).convert("RGB")
    img_width, img_height = image.size
    font_size = custom_font_size if custom_font_size > 0 else max(20, img_height // 20)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    lines = wrap_text_by_pixel(draw, input_text, font, img_width - 40)

    line_spacing = int(font_size * 0.5)
    text_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    total_text_height = sum(text_heights) + line_spacing * (len(lines) - 1)
    padding = int(font_size * 1.5)

    total_height = img_height + total_text_height + 2 * padding
    new_image = Image.new("RGB", (img_width, total_height), "white")
    new_image.paste(image, (0, 0))

    draw = ImageDraw.Draw(new_image)
    y = img_height + padding
    for i, line in enumerate(lines):
        line_width = draw.textlength(line, font=font)
        if alignment == "center":
            x = (img_width - line_width) // 2
        elif alignment == "right":
            x = img_width - line_width - 20
        else:  # left
            x = 20
        draw.text((x, y), line, fill="black", font=font)
        y += text_heights[i] + line_spacing

    st.image(new_image, caption="결과 이미지", use_column_width=True)

    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    safe_file_name = file_name.strip().replace(" ", "_")
    if not safe_file_name.lower().endswith(".png"):
        safe_file_name += ".png"

    st.download_button("📥 이미지 다운로드", data=img_buffer, file_name=safe_file_name, mime="image/png")
else:
    st.info("이미지, 텍스트, 파일명을 모두 입력하세요.")

