from io import BytesIO
import streamlit as st
from text_extractor import save_file, initialize, ppt_to_img, generate_summary
from utlis.logger import Logger
import os
import pandas as pd


if "imgaes_of_ppt" not in st.session_state:
    st.session_state['images_of_ppt']="imgaes/"
    os.makedirs(st.session_state["images_of_ppt"], exist_ok=True)

if "upload_dir" not in st.session_state:
    st.session_state["upload_dir"] =  "uploads/"
    os.makedirs(st.session_state["upload_dir"],exist_ok=True)
# Use session state to persist file processing results and avoid re-running on download
if "pptx_path" not in st.session_state:
    st.session_state["pptx_path"] = None
if "ppt_len" not in st.session_state:
    st.session_state["ppt_len"] = None
if "summaries" not in st.session_state:
    st.session_state["summaries"] = None
if "uploaded_filename" not in st.session_state:
    st.session_state["uploaded_filename"] = None



def parse_text_to_dataframe(text_content: str) -> pd.DataFrame:
    lines = text_content.strip().split('\n')
    
    # Look for Markdown table
    table_lines = [line for line in lines if '|' in line and line.strip().startswith('|')]
    if table_lines:
        headers = []
        data_rows = []
        for line in table_lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if not headers:
                headers = cells
            elif not all(cell in ['', ':', '-', ':---', '---', ':---:'] or '-' in cell for cell in cells):
                data_rows.append(cells)
        if headers and data_rows:
            return pd.DataFrame(data_rows, columns=headers)
    
    # Fallback: line-by-line as one-column DataFrame
    return pd.DataFrame({'Line': [line for line in lines if line.strip()]})


def main(goole_api_key):
    

    uploaded_file = st.file_uploader("Upload a PPTX file", type=["pptx"])
    if uploaded_file is not None:
        # Only process if a new file is uploaded or filename changed
        if (
            st.session_state["uploaded_filename"] != uploaded_file.name
            or st.session_state["pptx_path"] is None
        ):
            with st.spinner('Saving file...'):
                pptx_path = save_file(uploaded_file, st.session_state["upload_dir"])
                model = initialize(goole_api_key)
                ppt_len = ppt_to_img(pptx_path, st.session_state['images_of_ppt'])
            st.session_state["pptx_path"] = pptx_path
            st.session_state["ppt_len"] = ppt_len
            st.session_state["uploaded_filename"] = uploaded_file.name

            st.success(f"File saved: {pptx_path}")

            image_prefix = f"{st.session_state['images_of_ppt']}uploads/{uploaded_file.name}/ToImage_"
            with st.spinner("Unlocking slides..."):
                summaries = generate_summary(model, ppt_len, image_prefix)
            st.session_state["summaries"] = summaries
        else:
            pptx_path = st.session_state["pptx_path"]
            ppt_len = st.session_state["ppt_len"]
            summaries = st.session_state["summaries"]
            st.success(f"File loaded from cache: {pptx_path}")

        if st.session_state.get("summaries"):
            st.header("Slides Unlocked")

            for slide, summary in st.session_state["summaries"].items():
                table_data = []
                try:
                    if "|" in summary:
                        lines = [line.strip() for line in summary.splitlines() if "|" in line and not line.startswith("| :")]
                        rows = [line.strip("|").split("|") for line in lines]
                        header = [cell.strip() for cell in rows[0]]
                        for row in rows[1:]:
                            table_data.append(dict(zip(header, [cell.strip() for cell in row])))
                except Exception as e:
                    st.warning(f"⚠️ Could not parse table for {slide}: {e}")

                # Create columns for subheader and download button
                col1, col2 = st.columns([6, 2])
                with col1:
                    st.subheader(slide)

                if table_data:
                    df = pd.DataFrame(table_data)
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Data")
                    output.seek(0)

                    with col2:
                        st.download_button(
                            label="📥 Download",
                            data=output,
                            file_name=f"{slide.replace(' ', '_').lower()}_summary.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    with col2:
                        st.info("No table data")

                # Show the full summary below
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