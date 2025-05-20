import streamlit as st
from PIL import Image, ImageOps
from rembg import remove as rembg_remove
import io
import cv2
import numpy as np

st.set_page_config(page_title="Photo Tools", layout="centered")

# Helpers
def resize_passport(img, target_width=531, target_height=649, border=20):
    resized = img.resize((target_width, target_height))
    bordered = Image.new("RGB", (target_width + 2 * border, target_height + 2 * border), "white")
    bordered.paste(resized, (border, border))
    return bordered

from PIL import Image

def create_4x6_layout(passport_img_with_border):
    gap = 10  # Gap between photos
    canvas_w, canvas_h = 1200, 1800  # 4x6 inches at 300 DPI
    cols, rows = 2, 3

    # Calculate exact photo size to evenly fill canvas
    photo_w = (canvas_w - (cols - 1) * gap) // cols
    photo_h = (canvas_h - (rows - 1) * gap) // rows

    # Resize passport image with border to fit this slot
    img = passport_img_with_border.copy()
    img = img.resize((photo_w, photo_h), Image.Resampling.LANCZOS)

    # Create white canvas
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")

    # Paste images in 2x3 grid
    for row in range(rows):
        for col in range(cols):
            x = col * (photo_w + gap)
            y = row * (photo_h + gap)
            canvas.paste(img, (x, y))

    return canvas

def remove_background_strong(image):
    image = image.convert("RGBA")
    image_np = np.array(image)
    result = rembg_remove(image_np)  # RGBA output
    image_out = Image.fromarray(result)  # Keep alpha channel
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

# Page state
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home():
    st.session_state.page = "home"

# TITLE - always visible
st.title("📸 Photo Tools Web App")

cols = st.columns(6)  # column 3 (Add BG Color) is wider

if cols[0].button("🏠 Home"):
    go_home()
if cols[2].button("🔄 Remove Background"):
    st.session_state.page = "bg"
if cols[4].button("🎨 Add Background Color"):
    st.session_state.page = "bg"
if cols[1].button("🪪 Passport Size"):
    st.session_state.page = "passport"
if cols[3].button("🖼️ 4x6 Layout"):
    st.session_state.page = "layout"
if cols[5].button("❌ Clear"):
    st.session_state.page = "home"

# FILE UPLOADER
if st.session_state.page != "home":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
else:
    st.write("Welcome! Select an option above and upload a photo.")

# PAGES
if st.session_state.page == "bg" and uploaded_file:
    image = Image.open(uploaded_file)
    image_disp = resize_image_for_display(image)
    st.image(image_disp, caption="Original Image", use_container_width=False)
    if st.button("Remove Background"):
        output = remove_background_strong(image)
        output_disp = resize_image_for_display(output)
        st.image(output_disp, caption="Background Removed", use_container_width=False)
        buf = io.BytesIO()
        output.save(buf, format="PNG")
        st.download_button("Download Image", data=buf.getvalue(), file_name="no_bg.png", mime="image/png")

elif st.session_state.page == "bg_color" and uploaded_file:
    image = Image.open(uploaded_file)
    image_disp = resize_image_for_display(image)
    st.image(image_disp, caption="Original Image", use_container_width=False)

    color_choice = st.selectbox("Choose Background Color", ["white", "black", "red", "green", "blue", "gray", "yellow"])
    color_map = {
        "white": (255, 255, 255, 255),
        "black": (0, 0, 0, 255),
        "red": (255, 0, 0, 255),
        "green": (0, 255, 0, 255),
        "blue": (0, 0, 255, 255),
        "gray": (128, 128, 128, 255),
        "yellow": (255, 255, 0, 255)
    }

    if st.button("Apply Background Color"):
        output = add_background_color(image, color_map[color_choice])
        output_disp = resize_image_for_display(output)
        st.image(output_disp, caption=f"{color_choice.capitalize()} Background", use_container_width=False)
        buf = io.BytesIO()
        output.save(buf, format="JPEG")
        st.download_button(f"Download {color_choice} BG", data=buf.getvalue(), file_name=f"bg_{color_choice}.jpg", mime="image/jpeg")

elif st.session_state.page == "passport" and uploaded_file:
    image = Image.open(uploaded_file)
    image_disp = resize_image_for_display(image)
    st.image(image_disp, caption="Original Image", use_container_width=False)
    if st.button("Make Passport Size Photo"):
        passport_img = resize_passport(image)
        st.image(passport_img, caption="Passport Size", use_container_width=False)
        buf = io.BytesIO()
        passport_img.save(buf, format="JPEG")
        st.download_button("Download Passport", data=buf.getvalue(), file_name="passport.jpg", mime="image/jpeg")

elif st.session_state.page == "layout" and uploaded_file:
    image = Image.open(uploaded_file)
    image_disp = resize_image_for_display(image)
    st.image(image_disp, caption="Original Image", use_container_width=False)
    if st.button("Create 4x6 Layout"):
        passport_img = resize_passport(image)
        layout_img = create_4x6_layout(passport_img)
        st.image(layout_img, caption="4x6 Layout", use_container_width=False)
        buf = io.BytesIO()
        layout_img.save(buf, format="JPEG", dpi=(300, 300))
        st.download_button("Download 4x6 Image with 6 Photos", data=buf.getvalue(), file_name="4x6_layout.jpg", mime="image/jpeg")
# Footer - always visible and at the bottom thanks by Noman 
# st.markdown("---")
import streamlit as st

# Divider line
import streamlit as st

# Divider line
st.markdown("---")

# Bottom-right aligned messages
st.markdown(
    """
    <div style='position: fixed; bottom: 10px; right: 10px; color: gray; text-align: right; font-size: 14px;'>
        <div>App is developed by Noman</div>
        <div>Thanks for using this App.</div>
    </div>
    """,
    unsafe_allow_html=True
)

