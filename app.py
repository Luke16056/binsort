"""Start BinSort: python app.py, then open http://127.0.0.1:5000"""
import os

from dotenv import load_dotenv

load_dotenv()  # reads BINSORT_AI and GEMINI_API_KEY from .env (never committed)

from binsort.api import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    # Debug mode (auto-reload + in-browser debugger) only when asked for: BINSORT_DEBUG=1
    app.run(debug=os.environ.get("BINSORT_DEBUG") == "1")
