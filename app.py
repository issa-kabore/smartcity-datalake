import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app/Home.py", "--server.port=7860", "--server.address=0.0.0.0"])