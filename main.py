import streamlit as st


pages = [
    st.Page("src/poetize.py", title="Poetize", icon="📜"),
    st.Page(
        "src/configure_openai_api_key.py", title="Configure OpenAI API Key", icon="🔑"
    ),
    st.Page(
        "src/configure_vector_database.py", title="Configure Vector Database", icon="🗄"
    ),
]

pg = st.navigation(pages, position="hidden")
pg.run()
