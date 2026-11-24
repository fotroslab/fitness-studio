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
        st.link_button('Home · Fitness Studio', app_url(8500), use_container_width=True)
        st.link_button('01 · Member Intelligence', app_url(8501), use_container_width=True)
        st.link_button('02 · Personal Training', app_url(8502), use_container_width=True)
        st.divider()

def export_profile(profile):
    STORE.mkdir(exist_ok=True, parents=True, mode=0o700)
    for p in STORE.glob('*.json'):
        if time.time() - p.stat().st_mtime > 1800:
            p.unlink(missing_ok=True)
    token = secrets.token_urlsafe(32)
    (STORE / f'{token}.json').write_text(json.dumps({'created':time.time(), 'profile':profile}), encoding='utf-8')
    return token

def receive_profile():
    token = st.query_params.get('transfer', '')
    if not token or token == st.session_state.get('_received_token'):
        return
    if not re.fullmatch(r'[A-Za-z0-9_-]{40,60}', token):
        st.warning('Invalid transfer link. Export your profile again.')
        return
    path = STORE / f'{token}.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if time.time() - data['created'] > 1800:
            raise ValueError('expired')
        profile = data['profile']
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
        st.session_state['_received_token'] = token
        st.session_state['step'] = 1
        st.session_state['plan'] = None
        st.session_state['pdf_bytes'] = None
        st.query_params.clear()
    except (OSError, ValueError, KeyError, TypeError):
        st.warning('Transfer unavailable or expired (30 minutes). Please export again.')

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
        consent = st.checkbox('Transfer these measurements to the training app (link expires in 30 minutes).')
        if st.button('Prepare profile transfer', disabled=not consent):
            token = export_profile(profile)
            st.session_state['transfer_link'] = app_url(8502) + '/?transfer=' + token
        if st.session_state.get('transfer_link'):
            st.link_button('Continue with this profile →', st.session_state['transfer_link'], type='primary')
