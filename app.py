import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64

st.set_page_config(page_title="이미지 + 텍스트 결합기", layout="centered")
st.title("🖼️ 이미지 + 텍스트 결합기")

st.markdown("""
- 이미지를 업로드하거나 클립보드에서 붙여넣으세요.
- 텍스트를 입력하고, 글씨 크기를 조절하거나 비워두면 자동으로 조정됩니다.
""")

# 📂 이미지 업로드 or 클립보드 붙여넣기
uploaded_image = st.file_uploader("이미지를 업로드하세요 (또는 클립보드에 복사 후 붙여넣기)", type=["png", "jpg", "jpeg"])

clipboard_image_base64 = st.text_area("📋 클립보드 이미지 (base64로 붙여넣기)", placeholder="data:image/png;base64,...", height=100)

image = None
if uploaded_image:
    image = Image.open(uploaded_image).convert("RGB")
elif clipboard_image_base64.startswith("data:image"):
    try:
        header, encoded = clipboard_image_base64.split(",", 1)
        decoded = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(decoded)).convert("RGB")
    except Exception as e:
        st.error("클립보드 이미지 불러오기 실패. base64 형식을 확인하세요.")

# 입력 영역
input_text = st.text_area("📝 아래 텍스트를 입력하세요", height=150)

file_name = st.text_input("💾 저장할 파일 이름 (확장자 제외)", value="merged_image")

# 글씨 크기
custom_font_size = st.number_input("🔤 글씨 크기 (0이면 자동)", min_value=0, max_value=100, value=0)

font_path = "NanumGothic.ttf"  # 프로젝트 내 한글 폰트

# 실행 조건
if image and input_text and file_name:
    img_width, img_height = image.size

    # 글씨 크기 자동 설정
    font_size = custom_font_size if custom_font_size > 0 else max(20, img_height // 20)

    # 폰트 설정
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 텍스트 줄별 처리
    lines = input_text.strip().split('\n')
    line_spacing = int(font_size * 0.5)
    text_heights = [font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines]
    total_text_height = sum(text_heights) + line_spacing * (len(lines) - 1)
    padding = int(font_size * 1.5)

    # 새 캔버스
    total_height = img_height + total_text_height + 2 * padding
    new_image = Image.new("RGB", (img_width, total_height), "white")
    new_image.paste(image, (0, 0))

    # 텍스트 추가
    draw = ImageDraw.Draw(new_image)
    y = img_height + padding
    for i, line in enumerate(lines):
        w = font.getlength(line)
        x = (img_width - w) // 2
        draw.text((x, y), line, fill="black", font=font)
        y += text_heights[i] + line_spacing

    # 이미지 표시
    st.image(new_image, caption="결과 이미지", use_column_width=True)

    # 다운로드 준비
    img_buffer = io.BytesIO()
    new_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    safe_file_name = file_name.strip().replace(" ", "_")
    if not safe_file_name.lower().endswith(".png"):
        safe_file_name += ".png"

    st.download_button("📥 이미지 다운로드", data=img_buffer, file_name=safe_file_name, mime="image/png")
else:
    st.info("이미지, 텍스트, 파일명을 모두 입력해주세요.")
