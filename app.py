import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

st.title("🖼️ 이미지 + 텍스트 결합기")

# 📂 이미지 업로드
uploaded_image = st.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

# 📝 텍스트 입력
input_text = st.text_area("텍스트를 입력하세요")

# 🗂️ 저장할 파일 이름 입력
file_name = st.text_input("저장할 파일 이름 (확장자 제외)", value="merged_image")

# ⚙️ 설정
font_size = 24
font_path = "NanumGothic.ttf"  # 📌 프로젝트 내 폰트 파일을 사용할 경우

# ▶️ 실행 조건
if uploaded_image and input_text and file_name:
    # 이미지 열기
    image = Image.open(uploaded_image).convert("RGB")
    img_width, img_height = image.size

    # 폰트 설정
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 텍스트 처리
    lines = input_text.split('\n')
    line_spacing = 10
    text_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    total_text_height = sum(text_heights) + line_spacing * (len(lines) - 1)
    padding = 40

    # 새 이미지 생성 (원본 이미지 + 텍스트 공간)
    total_height = img_height + total_text_height + 2 * padding
    new_image = Image.new("RGB", (img_width, total_height), "white")
    new_image.paste(image, (0, 0))

    # 텍스트 그리기
    draw = ImageDraw.Draw(new_image)
    y = img_height + padding
    for i, line in enumerate(lines):
        w = font.getlength(line)
        x = (img_width - w) // 2
        draw.text((x, y), line, fill="black", font=font)
        y += text_heights[i] + line_spacing

    # 결과 이미지 보여주기
    st.image(new_image, caption="결과 이미지", use_column_width=True)

    # 다운로드용 버퍼 저장
    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # 파일명 확장자 자동 추가
    safe_file_name = file_name.strip().replace(" ", "_")
    if not safe_file_name.lower().endswith(".png"):
        safe_file_name += ".png"

    # 다운로드 버튼
    st.download_button("📥 이미지 다운로드", data=img_buffer, file_name=safe_file_name, mime="image/png")
else:
    st.info("이미지, 텍스트, 파일명을 모두 입력해주세요.")
