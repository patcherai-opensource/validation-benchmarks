import os
import sys

if __name__ == "__main__":
    os.execvp(
        sys.executable,
        [sys.executable, "-m", "gunicorn",
         "--bind", "0.0.0.0:80",
         "--workers", "2",
         "--timeout", "120",
         "--access-logfile", "-",
         "--error-logfile", "-",
         "app:app"]
    )
