import streamlit as st
import hashlib
import openai
import time


def stream_data(text):
    for letter in text.split(" "):
        yield letter + " "
        time.sleep(0.01)


def validate_api_key(api_key):
    try:
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        client.models.list()
        return True
    except openai.AuthenticationError:
        return False


st.title("Welcome to the Poetize app!")

first_welcome_text = """
    To get started, please enter your OpenAI API key below.
    This key will allow the app to connect with OpenAI's services to generate embeddings from the phrases you enter, as well as to create unique text based on those embeddings.
    """

if "first_welcome_text_stream_executed" not in st.session_state:
    st.session_state["first_welcome_text_stream_executed"] = False

if not st.session_state["first_welcome_text_stream_executed"]:
    st.write_stream(stream_data(first_welcome_text))
    st.session_state["first_welcome_text_stream_executed"] = True
else:
    st.write(first_welcome_text)

openai_api_key = st.text_input(
    "OpenAI API Key",
    type="password",
    autocomplete="off",
)
if st.button(
    "Submit",
    use_container_width=True,
):
    if hashlib.sha512(openai_api_key.encode()).hexdigest() == st.secrets["PASSWORD"]:
        openai_api_key = st.secrets["OPENAI_API_KEY"]

    if openai_api_key != "" and not validate_api_key(openai_api_key):
        st.warning("Please enter your valid OpenAI API key!", icon="⚠")
    else:
        st.session_state["OPENAI_API_KEY"] = openai_api_key
        st.success("OpenAI API Key has been entered!")
        time.sleep(1)
        st.switch_page("src/configure_vector_database.py")
