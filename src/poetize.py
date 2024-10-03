# to deal with Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.
__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import streamlit as st
from chromadb import PersistentClient
from openai import OpenAI
import time
import os


EMBEDDING_MODEL_NAME = "text-embedding-3-small"
CHAT_MODEL_NAME = "gpt-3.5-turbo"
MAX_TOKENS = 300


@st.cache_resource(show_spinner=False)
def get_chromadb_collection():
    client = PersistentClient(path=os.path.join(os.getcwd(), "chroma_db"))
    try:
        collection = client.get_collection(name="lyrics")
        return collection
    except Exception as e:
        st.error(f"Error occurred while loading the collection")
        st.stop()


@st.cache_resource(show_spinner=False)
def get_openai_client():
    return OpenAI(api_key=st.session_state["OPENAI_API_KEY"])


def stream_data(stream):
    for chunk in stream:
        yield chunk.choices[0].delta.content or ""
        time.sleep(0.01)


def generate_response(prompt, temperature):
    prompt = "\n\nNext fragment:\n".join(
        [doc["lyrics_fragment"].replace("\n", ". ") for doc in prompt.values()]
    )

    client = get_openai_client()
    stream = client.chat.completions.create(
        model=CHAT_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are a talented poet.
                    Your task is to create a poem using as many phrases and words from the user's prompt as possible.
                    The user will provide fragments of some song lyrics, and you must transform them into a coherent, artistic poem.
                    Skip parts of the prompt that are not suitable for the poem (e.g., brackets, etc.).
                    At the end of each line place two spaces.
                    You should use a maximum of {MAX_TOKENS} tokens.
                    """,
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=MAX_TOKENS,
        n=1,
        stream=True,
    )
    with st.container(border=True):
        st.subheader("A poem for you!")
        st.write_stream(stream_data(stream))


st.title("Let's poetize your thoughts!")

if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = None
if "CHROMADB_PART" not in st.session_state:
    st.session_state["CHROMADB_PART"] = None

if st.session_state["OPENAI_API_KEY"] is None:
    st.switch_page("src/configure_openai_api_key.py")
elif st.session_state["CHROMADB_PART"] is None:
    st.switch_page("src/configure_vector_database.py")

with st.form("phrase_form"):
    text = st.text_area(
        "Share your thoughts!",
        placeholder="Year after year, the sun is the same, in a relative way, but you're older",
        max_chars=250,
    )
    temperature = st.slider(
        "Level of creativity", min_value=0.0, max_value=1.0, value=0.5, step=0.05
    )

    if st.form_submit_button("Submit", use_container_width=True):
        client = get_openai_client()
        embeddings = client.embeddings.create(input=text, model=EMBEDDING_MODEL_NAME)

        collection = get_chromadb_collection()
        query_results = collection.query(
            query_embeddings=embeddings.data[0].embedding, n_results=5
        )
        similar_documents = {}
        for i, id in enumerate(query_results["ids"][0]):
            similar_documents[id] = {
                "artist": query_results["metadatas"][0][i]["artist"],
                "title": query_results["metadatas"][0][i]["title"],
                "lyrics_fragment": query_results["documents"][0][i],
                "distance": query_results["distances"][0][i],
            }

        with st.expander("Display matched lyrics fragments"):
            for doc in similar_documents.values():
                text_to_display = f"""
                **Artist**: {doc["artist"]}  
                **Title**: {doc["title"]}  
                **Matched lyrics fragment**: {doc["lyrics_fragment"]}
                """
                st.markdown(text_to_display)

        generate_response(similar_documents, temperature)
