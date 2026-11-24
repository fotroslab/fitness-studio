"""Portable cross-app navigation and explicit, short-lived profile handoff."""
import json
import os
from pathlib import Path
import re
import secrets
import time
import streamlit as st

STORE = Path(os.environ.get('FITNESS_TRANSFER_DIR', str(Path(__file__).resolve().parent.parent / '.fitness-transfers')))

def app_url(port):
    override = os.environ.get(f'FITNESS_URL_{port}')
    if override:
        return override.rstrip('/')
    host = st.context.headers.get('X-Forwarded-Host') or st.context.headers.get('Host', '')
    if '.e2b.app' in host:
        return 'https://' + re.sub(r'^\d+-', str(port) + '-', host)
    return f'http://localhost:{port}'

def navigation():
    with st.sidebar:
        st.caption('FITNESS INTELLIGENCE / STUDIO')
        st.page_link('pages/home.py', label='Home · Fitness Studio')
        st.page_link('pages/members.py', label='01 · Member Intelligence')
        st.page_link('pages/training.py', label='02 · Personal Training')
        st.divider()


def receive_profile():
    # Same browser session, not shared disk or a personal-data URL.
    profile = st.session_state.pop('_pending_profile', None)
    if profile is None:
        return
    limits = {'age':(16,80,int), 'height_m':(1.4,2.1,float), 'weight_kg':(40,180,float),
              'body_fat_pct':(5,50,float), 'experience':(1,3,int),
              'water_liters':(1,6,float), 'resting_hr':(42,95,int)}
    clean = {}
    for key, (lo,hi,cast) in limits.items():
        if key in profile and lo <= float(profile[key]) <= hi:
            clean[key] = cast(profile[key])
    if profile.get('gender') in ('Male','Female'):
        clean['gender'] = profile['gender']
    st.session_state['imported_profile'] = clean
    st.session_state['step'] = 1
    st.session_state['plan'] = None
    st.session_state['pdf_bytes'] = None


def export_member_ui(df):
    with st.expander('Connect to Personal Training · Export a member profile', expanded=False):
        st.caption('Select an actual dataset member. Only their recorded measurements are transferred; cluster averages are never used as personal measurements.')
        idx = st.number_input('Dataset member row (1-based)', 1, len(df), 1, key='export_row')
        row = df.iloc[int(idx)-1]
        mapping = {'Age':'age','Gender':'gender','Height (m)':'height_m','Weight (kg)':'weight_kg',
                   'Fat_Percentage':'body_fat_pct','Experience_Level':'experience',
                   'Resting_BPM':'resting_hr','Water_Intake (liters)':'water_liters'}
        profile = {v: (row[k].item() if hasattr(row[k], 'item') else row[k]) for k,v in mapping.items() if k in row}
        result = st.session_state.get('result', {})
        labels = result.get('labels', [])
        if len(labels) == len(df):
            profile['source_cluster'] = int(labels[int(idx)-1])
            profile['source_model'] = str(result.get('algo', ''))
            st.caption(f"Source persona: Cluster {profile['source_cluster']} · {profile['source_model']} (not reused as a destination cluster ID)")
        st.json(profile, expanded=False)
        st.caption('The destination validates its supported ranges. Missing/out-of-range fields stay at editable defaults. Goals and availability remain your choice. Persona is recomputed by Project 2’s own model; cluster IDs are not interchangeable.')
        consent = st.checkbox('Transfer these measurements to the training app in this browser session.')
        if st.button('Prepare profile transfer', disabled=not consent):
            st.session_state['_pending_profile'] = profile
            st.success('Profile ready. Continue below to review it in the training app.')
        if st.session_state.get('_pending_profile'):
            st.page_link('pages/training.py', label='Continue with this profile →', icon='💪')
