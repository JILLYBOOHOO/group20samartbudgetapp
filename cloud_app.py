"""Community Cloud entry point; local app.py retains durable laptop storage."""
# Bring the listed helpers from pathlib into this file.
from pathlib import Path
# Import runpy so this file can use its functions and classes.
import runpy

runpy.run_path(str(Path(__file__).with_name('app.py')),init_globals={'CLOUD_DEMO':True},run_name='__main__')
