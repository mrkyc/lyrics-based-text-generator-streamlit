import streamlit as st
import tarfile
import shutil
import gdown
import time
import os


def stream_data(text):
    for letter in text.split(" "):
        yield letter + " "
        time.sleep(0.01)


st.title("Welcome to the Poetize app!")

second_welcome_text = """
    Please select one of the available vector databases from which you would like to retrieve information.

    This database will be used to retrieve song fragments that are meaningfully similar to the phrase you enter.
    Using the Retrieval-Augmented Generation (RAG) method, the app will craft a unique, creative poem for you.
    
    Due to resource limitations on the Streamlit Cloud, there isn't a single, comprehensive vector database.
    Instead, there is a curated selection of databases to ensure optimal performance and responsiveness.
    Basically, you can randomly choose one and let's start the creativity flow!
    """

if "second_welcome_text_stream_executed" not in st.session_state:
    st.session_state["second_welcome_text_stream_executed"] = False

if not st.session_state["second_welcome_text_stream_executed"]:
    st.write_stream(stream_data(second_welcome_text))
    st.session_state["second_welcome_text_stream_executed"] = True
else:
    st.write(second_welcome_text)

options = [
    "Vector database number 1",
    "Vector database number 2",
    "Vector database number 3",
    "Vector database number 4",
    "Vector database number 5",
]

if "CHROMADB_PART" not in st.session_state:
    st.session_state["CHROMADB_PART"] = None

index = (
    None
    if st.session_state["CHROMADB_PART"] is None
    else options.index(st.session_state["CHROMADB_PART"])
)
st.session_state["CHROMADB_PART"] = st.selectbox(
    "Select a vector database to use",
    options=options,
    index=index,
)

if st.button("START!", use_container_width=True):
    chromadb_part_number = options.index(st.session_state["CHROMADB_PART"]) + 1
    url = st.secrets[f"CHROMA_DB_PART{chromadb_part_number}_LINK"]
    destination = "chroma_db.tar.gz"
    with st.spinner("Downloading the database..."):
        gdown.download(url, destination, quiet=True)
    with st.spinner("Extracting the database..."):
        with tarfile.open(destination, "r:gz") as tar:
            tar.extractall()

    if os.path.exists("chroma_db"):
        shutil.rmtree("chroma_db")
    os.rename(f"chroma_db_part{chromadb_part_number}", "chroma_db")
    os.remove(destination)

    st.switch_page("src/poetize.py")
