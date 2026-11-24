# Fitness Intelligence Studio — Cloud Edition

One Streamlit website, one server, one public URL. No Python or editor required for visitors.

## Free deployment (browser only)

1. Extract the supplied ZIP.
2. Sign in at https://github.com and create a repository, for example `fitness-studio`.
3. Use **Add file → Upload files**. Upload the CONTENTS of this folder, preserving `pages/`, `projects/`, and `.streamlit/`. The file `streamlit_app.py` must be at the repository root, not inside an extra folder. GitHub does not extract uploaded ZIP files.
4. Check that `projects/segmentation/data/` and `projects/training/data/` contain the CSV datasets. They are included in this package.
5. Sign in at https://share.streamlit.io using your own GitHub account. Choose **Create app → Yup, I have an app**.
6. Select the repository and branch (`main`). Set **Main file path** to `streamlit_app.py`.
7. Under Advanced settings choose Python 3.12 (or 3.13). No secrets/API keys are required.
8. Choose an available app subdomain, then deploy. Ensure sharing is public so visitors do not need an account.
9. Test the final URL in a private browser window before sending it to employers.

Do not send your passwords or login codes to anyone. Cloud publication must be completed in your own account. This package is prepared and locally tested; it is not itself a completed public deployment.

If `.streamlit/config.toml` is hidden in your file picker, create that file manually in GitHub using the included content. The app still has CSS styling without it, but native widget colors may differ.

## Presenting to employers

- Start at the home page, then open either application using the sidebar.
- Member Intelligence → Deployment → Connect to Personal Training: select a real dataset member, review and approve the transfer, prepare it, then continue.
- Personal Training: review prefilled values, choose goals, and generate the plan/PDF.
- Only supported in-range measurements are imported; other fields remain editable defaults.
- Personas are model-specific and recalculated in the training app, not reused as equivalent cluster IDs.
- Transfers use Streamlit session state, not shared local files or personal information in URLs. Refreshing/disconnecting can reset state. Nothing is a persistent user account.
- Free hosting can sleep or have resource limits. Open the URL before a live demonstration. No uptime guarantee is implied.

## Local development (optional, not needed by visitors)

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Contents

- `streamlit_app.py`: single website entrypoint and navigation.
- `pages/`: landing page and independent project runners.
- `projects/`: both original analytics/training implementations and bundled datasets.
- `bridge.py`: same-session cross-page profile handoff.
- `theme.py`, `.streamlit/config.toml`: Evergreen/Slate design system.

The cloud edition replaces the old three-port navigation. Run the ROOT entrypoint above, not the individual legacy app files. Old READMEs inside `projects/` describe their historical standalone versions; use this guide for deployment.

Dataset: https://www.kaggle.com/datasets/valakhorasani/gym-members-exercise-dataset
Deployment reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

Educational portfolio demo only. Training/nutrition estimates are not clinical advice. The real Kaggle dataset is bundled; the segmentation project also retains its separately labelled synthetic comparison data.
