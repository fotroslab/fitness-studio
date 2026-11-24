"""Single-process, single-domain deployment for Streamlit Community Cloud."""
from pathlib import Path
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
st.navigation([
    st.Page('pages/home.py', title='Fitness Studio', icon='🏠', default=True),
    st.Page('pages/members.py', title='Member Intelligence', icon='📊', url_path='members'),
    st.Page('pages/training.py', title='Personal Training', icon='💪', url_path='training'),
]).run()
