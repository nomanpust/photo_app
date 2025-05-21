import streamlit as st
from PIL import Image, ImageOps
from rembg import remove as rembg_remove
import io
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="Noman Photo Studio", layout="wide")

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
    return Image.fromarray(result)

def add_background_color(fg_img, color):
    fg_img = remove_background_strong(fg_img).convert("RGBA")
    bg = Image.new("RGBA", fg_img.size, color)
    combined = Image.alpha_composite(bg, fg_img)
    return combined.convert("RGB")

def resize_image_for_display(image, max_width=350):
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

# --- Title and Layout ---
st.title(" :rainbow[Noman Photo App]")

sidebar_col, display_col = st.columns([1, 3])

# --- Sidebar Menu ---
with sidebar_col:
    st.markdown("### 📂 Menu")
    if st.button(":rainbow[🏠 Home]"):
        go_home()
    if st.button(":rainbow[🆔 Passport Size]"):
        st.session_state.page = "passport"
    if st.button(":rainbow[🔄 Remove Background]"):
        st.session_state.page = "bg"
    if st.button(":rainbow[🖼️ 4X6 Layout (6 Photos)]"):
        st.session_state.page = "layout"
    if st.button(":rainbow[🌈 Add Background Color]"):
        st.session_state.page = "bg_color"
    if st.button(":rainbow[❌ Clear]"):
        st.session_state.page = "home"
    st.markdown("---")

# --- Display Area ---
with display_col:
    if st.session_state.page != "home":
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(resize_image_for_display(image), caption="Original Image", use_container_width=False)

            if st.session_state.page == "bg":
                if st.button("Remove Background"):
                    output = remove_background_strong(image)
                    st.image(resize_image_for_display(output), caption="Background Removed", use_container_width=False)
                    buf = io.BytesIO()
                    output.save(buf, format="PNG")
                    st.download_button("Download Image", data=buf.getvalue(), file_name="no_bg.png", mime="image/png")

            elif st.session_state.page == "bg_color":
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

            elif st.session_state.page == "passport":
                if st.button("Make Passport Size Photo"):
                    passport_img = resize_passport(image)
                    st.image(passport_img, caption="Passport Size", use_container_width=False)
                    buf = io.BytesIO()
                    passport_img.save(buf, format="JPEG")
                    st.download_button("Download Passport", data=buf.getvalue(), file_name="passport.jpg", mime="image/jpeg")

            elif st.session_state.page == "layout":
                if st.button("Create 4x6 Layout with 6 photos"):
                    passport_img = resize_passport(image)
                    layout_img = create_4x6_layout(passport_img)
                    st.image(layout_img, caption="4x6 Layout", use_container_width=False)
                    buf = io.BytesIO()
                    layout_img.save(buf, format="JPEG", dpi=(300, 300))
                    st.download_button("Download 4x6 Image with 6 Photos", data=buf.getvalue(), file_name="4x6_layout.jpg", mime="image/jpeg")

    else:
        # st.write("👈 Select an option from the menu and upload a photo.")
  
        st.markdown(
    """
    <style>
    @keyframes rotate-scale {
        0% {
            transform: rotate(0deg) scale(1);
            text-shadow: 0 0 5px #ff4b4b;
        }
        25% {
            transform: rotate(-3deg) scale(1.03);
            text-shadow: 0 0 10px #ff7f50;
        }
        50% {
            transform: rotate(3deg) scale(1.05);
            text-shadow: 0 0 15px #ffa500;
        }
        75% {
            transform: rotate(-3deg) scale(1.03);
            text-shadow: 0 0 10px #ff7f50;
        }
        100% {
            transform: rotate(0deg) scale(1);
            text-shadow: 0 0 5px #ff4b4b;
        }
    }

    @keyframes rainbow-background {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .animated-note {
        display: inline-block;
        animation: rotate-scale 1.5s infinite ease-in-out, rainbow-background 4s ease infinite;
        font-weight: 900;
        font-size: 22px;
        padding: 14px 24px;
        border-radius: 12px;
        background: linear-gradient(270deg, #ADFF2F, #32CD32, #228B22, #006400, #ADFF2F);
        background-size: 400% 400%;
        color: white;
        box-shadow: 0 0 25px #32CD32;
        transition: all 0.3s ease-in-out;
    }
    </style>

    <div class="animated-note">
        👈 Select an option from the menu and upload a photo.
    </div>
    """,
    unsafe_allow_html=True
)




# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='position: fixed; bottom: 10px; right: 10px; color: #facc15; text-align: right; font-size: 14px;'>
        <div>App developed by <b>Noman</b></div>
        <div>Thanks for using this App 🚀</div>
    </div>
    """,
    unsafe_allow_html=True
)
