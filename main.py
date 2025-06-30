import streamlit as st
from text_extractor import save_file, initialize, ppt_to_img, generate_summary
import os


if "imgaes_of_ppt" not in st.session_state:
    st.session_state['images_of_ppt']="imgaes/"
    os.makedirs(st.session_state["images_of_ppt"], exist_ok=True)

if "upload_dir" not in st.session_state:
    st.session_state["upload_dir"] =  "uploads/"
    print(st.session_state["upload_dir"])
    os.makedirs(st.session_state["upload_dir"],exist_ok=True)


def main(goole_api_key):

    uploaded_file = st.file_uploader("Upload a PPTX file", type=["pptx"])
    if uploaded_file is not None:
        # Save the uploaded file]
        with st.spinner('Saving file...'):
            pptx_path = save_file(uploaded_file,st.session_state["upload_dir"])

            # Initialize Gemini Vision model
            model = initialize(goole_api_key)

            # Convert PPT to images
            ppt_len = ppt_to_img(pptx_path,st.session_state['images_of_ppt'])

        st.success(f"File saved: {pptx_path}")
        # Generate summaries
        image_prefix = f"{st.session_state["images_of_ppt"]}uploads/{uploaded_file.name}/ToImage_"
        with st.spinner("Unlocking slides..."):
            summaries = generate_summary(model, ppt_len, image_prefix)

        st.header("Slides Unlocked")
        for slide, summary in summaries.items():
            st.subheader(slide)
            st.write(summary)

if __name__ == "__main__":
    st.title("📊 SlideText Unlocked 📖")
    st.set_page_config(initial_sidebar_state='collapsed', layout='wide')
    sub_title = st.subheader("Please provide your Google API key in the sidebar to extract text from the PPT.",divider=True)
    with st.sidebar:
        st.markdown(
                        """
                        ### How to use:
                        1. Enter your Google API key below 🔑  
                        2. Upload a PPT file 📊  
                        3. Get the extracted text from the presentation 📄  
                        """
                    )

        GOOGLE_API_KEY = st.text_input("GOOGLE_API_KEY", type="password")
    if GOOGLE_API_KEY:
        sub_title.empty()
        main(GOOGLE_API_KEY)