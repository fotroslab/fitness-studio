import runpy
import sys
from pathlib import Path
folder = Path(__file__).resolve().parents[1] / 'projects' / 'training'
if str(folder) not in sys.path:
    sys.path.append(str(folder))
runpy.run_path(str(folder / 'workout_recommender_app.py'), run_name='__main__')
