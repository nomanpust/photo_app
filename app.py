import streamlit as st
from PIL import Image, ImageOps
from rembg import remove as rembg_remove
import io
import numpy as np

st.set_page_config(page_title="Photo Tools", layout="centered")

# --- Helper Functions ---
def resize_passport(img, target_width=531, target_height=649, border=20):
    resized = img.resize((target_width, target_height))
    bordered = Image.new("RGB", (target_width + 2 * border, target_height + 2 * border), "white")
    bordered.paste(resized, (border, border))
    return bordered

def create_4x6_layout(passport_img_with_border):
    gap = 10
    canvas_w, canvas_h = 1200, 1800
    cols, rows = 2, 3
    photo_w = (canvas_w - (cols - 1) * gap) // cols
    photo_h = (canvas_h - (rows - 1) * gap) // rows

    img = passport_img_with_border.copy().resize((photo_w, photo_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")

    for row in range(rows):
        for col in range(cols):
            x = col * (photo_w + gap)
            y = row * (photo_h + gap)
            canvas.paste(img, (x, y))

    return canvas

def remove_background_strong(image):
    image = image.convert("RGBA")
    image_np = np.array(image)
    result = rembg_remove(image_np)
    image_out = Image.fromarray(result)
    return image_out

def add_background_color(fg_img, color):
    fg_img = remove_background_strong(fg_img).convert("RGBA")
    bg = Image.new("RGBA", fg_img.size, color)
    combined = Image.alpha_composite(bg, fg_img)
    return combined.convert("RGB")

def resize_image_for_display(image, max_width=500):
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        return image.resize(new_size)
    return image

# --- App State ---
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home():
    st.session_state.page = "home"

# --- UI Header ---
st.title("📸 Photo Tools Web App")
cols = st.columns(6)

if cols[0].button("🏠 Home"):
    go_home()
if cols[1].button("🆔 Passport Size"):
    st.session_state.page = "passport"
if cols[2].button("🔄 Remove Background"):
    st.session_state.page = "bg"
if cols[3].button("🖼️ 4X6 Photos Layout"):
    st.session_state.page = "layout"
if cols[4].button("🌈 Add Background Color"):
    st.session_state.page = "bg_color"
if cols[5].button("❌ Clear"):
    st.session_state.page = "home"

# --- File Upload ---
if st.session_state.page != "home":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
else:
    st.write("Welcome! Select an option above and upload a photo.")

# --- Page: Remove Background ---
if st.session_state.page == "bg" and uploaded_file:
    image = Image.open(uploaded_file)
    st.image(resize_image_for_display(image), caption="Original Image", use_container_width=False)
    if st.button("Remove Background"):
        output = remove_background_strong(image)
        st.image(resize_image_for_display(output), caption="Background Removed", use_container_width=False)
        buf = io.BytesIO()
        output.save(buf, format="PNG")
        st.download_button("Download Image", data=buf.getvalue(), file_name="no_bg.png", mime="image/png")

# --- Page: Add Background Color ---
elif st.session_state.page == "bg_color" and uploaded_file:
    image = Image.open(uploaded_file)
    st.image(resize_image_for_display(image), caption="Original Image", use_container_width=False)

    st.markdown("### 🎨 Choose a Background Color")
    use_picker = st.checkbox("Use color picker instead of preset", value=True)

    if use_picker:
        bg_color = st.color_picker("Pick a background color", "#ffffff")
        color_tuple = Image.new("RGBA", (1, 1), bg_color).getpixel((0, 0))
    else:
        color_choice = st.selectbox("Choose Preset Color", ["white", "black", "red", "green", "blue", "gray", "yellow"])
        color_map = {
            "white": (255, 255, 255, 255),
            "black": (0, 0, 0, 255),
            "red": (255, 0, 0, 255),
            "green": (0, 255, 0, 255),
            "blue": (0, 0, 255, 255),
            "gray": (128, 128, 128, 255),
            "yellow": (255, 255, 0, 255)
        }
        color_tuple = color_map[color_choice]

    if st.button("Apply Background Color"):
        output = add_background_color(image, color_tuple)
        st.image(resize_image_for_display(output), caption="Image with Background Color", use_container_width=False)
        buf = io.BytesIO()
        output.save(buf, format="JPEG")
        st.download_button("Download Image", data=buf.getvalue(), file_name="bg_colored.jpg", mime="image/jpeg")

# --- Page: Passport Size ---
elif st.session_state.page == "passport" and uploaded_file:
    image = Image.open(uploaded_file)
    st.image(resize_image_for_display(image), caption="Original Image", use_container_width=False)
    if st.button("Make Passport Size Photo"):
        passport_img = resize_passport(image)
        st.image(passport_img, caption="Passport Size", use_container_width=False)
        buf = io.BytesIO()
        passport_img.save(buf, format="JPEG")
        st.download_button("Download Passport", data=buf.getvalue(), file_name="passport.jpg", mime="image/jpeg")

# --- Page: 4x6 Layout ---
elif st.session_state.page == "layout" and uploaded_file:
    image = Image.open(uploaded_file)
    st.image(resize_image_for_display(image), caption="Original Image", use_container_width=False)
    if st.button("Create 4x6 Layout"):
        passport_img = resize_passport(image)
        layout_img = create_4x6_layout(passport_img)
        st.image(layout_img, caption="4x6 Layout", use_container_width=False)
        buf = io.BytesIO()
        layout_img.save(buf, format="JPEG", dpi=(300, 300))
        st.download_button("Download 4x6 Image with 6 Photos", data=buf.getvalue(), file_name="4x6_layout.jpg", mime="image/jpeg")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='position: fixed; bottom: 10px; right: 10px; color: gray; text-align: right; font-size: 14px;'>
        <div>App is developed by Noman</div>
        <div>Thanks for using this App.</div>
    </div>
    """,
    unsafe_allow_html=True
)
