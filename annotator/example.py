import streamlit as st
import fitz
import base64
from tempfile import NamedTemporaryFile

from annotator import annotator

st.subheader("PDF Annotator")

# Upload the PDF
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    binary = uploaded_file.getvalue()

    # Encode the binary data as a base64 string and render the PDF
    base64_pdf = base64.b64encode(binary).decode("utf-8")

    num_clicks = annotator(base64_pdf)