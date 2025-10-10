import streamlit as st
import os
from dotenv import load_dotenv
from src.ui.main_interface import ManualQAInterface

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="Musical Instrument Manual Q&A",
        page_icon="🎹",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎹 Musical Instrument Manual Q&A System")
    st.markdown("Ask questions about your synthesizer, keyboard, and mixer manuals!")

    # Initialize the main interface
    interface = ManualQAInterface()
    interface.render()

if __name__ == "__main__":
    main()