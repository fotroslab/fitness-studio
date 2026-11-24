"""Fitness Intelligence Studio — unified entry point for both independent apps."""
import streamlit as st
import theme
import bridge

theme.apply('◈', 'Fitness Intelligence Studio')
bridge.navigation()
st.markdown('<p style="color:#5EE0B5;letter-spacing:.18em;font-size:.8rem;margin-top:1rem">FITNESS INTELLIGENCE / STUDIO</p>', unsafe_allow_html=True)
theme.hero('◈', 'Understand your members.\nBuild a better plan.',
           'One connected workspace for member analytics, personalized training and nutrition.',
           ['REAL DATA · 973 SESSIONS', 'MEMBER ANALYTICS', 'PERSONAL TRAINING'])
a,b,c=st.columns(3)
a.metric('Connected applications','02')
b.metric('Dataset observations','973')
c.metric('One workflow','Analyze → Train')
st.write('')
a,b=st.columns(2, gap='large')
with a:
    theme.section('01', 'Member Intelligence')
    st.markdown('Explore gym members, compare clustering models and discover data-driven fitness personas.')
    st.markdown('**Explore** · CRISP-DM analytics  \n**Compare** · Clustering and evaluation  \n**Connect** · Review and transfer a member profile')
    st.link_button('Open Member Intelligence →', bridge.app_url(8501), type='primary', use_container_width=True)
with b:
    theme.section('02', 'Personal Training')
    st.markdown('Turn a member profile into an editable weekly workout and nutrition plan.')
    st.markdown('**Personalize** · Three-step profile wizard  \n**Plan** · Training, macros and recovery  \n**Export** · Downloadable PDF report')
    st.link_button('Open Personal Training →', bridge.app_url(8502), type='primary', use_container_width=True)
st.divider()
theme.section('↗', 'From insight to action')
st.markdown('**1. Explore** the dataset in Member Intelligence. **2. Open Deployment**, select a member and approve the transfer. **3. Continue** in Personal Training, review the prefilled values and choose your goals.')
st.caption('Privacy by design: measurements are stored server-side for 30 minutes, not embedded in the URL. Links contain a random access token; treat them as private. Each app keeps its own model, so persona names may differ. Educational estimates, not medical advice.')
theme.footer('Fitness Intelligence Studio', 'Fotros')
