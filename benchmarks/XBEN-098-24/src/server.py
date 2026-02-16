#!/usr/bin/env python3
# filehost - lightweight file hosting server
# version 0.9.4 "neon"

import os
import sys
import time
import mimetypes
import hashlib
import json
import stat
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, urlparse, parse_qs
from pathlib import Path

VERSION = "0.9.4"
CODENAME = "neon"
BUILD_DT = "2023-07-05"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
SHARED_DIR = os.path.join(BASE_DIR, "shared")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

NO_CACHE = {"Cache-Control": "no-store, max-age=0"}


def format_size(size):
    for unit in ["B", "KiB", "MiB", "GiB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TiB"


def format_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def guess_mime(path):
    mt, _ = mimetypes.guess_type(path)
    return mt or "application/octet-stream"


def load_template(name):
    tpl_path = os.path.join(TEMPLATE_DIR, name)
    with open(tpl_path, "r") as f:
        return f.read()


def render_template(name, **kwargs):
    tpl = load_template(name)
    for key, val in kwargs.items():
        tpl = tpl.replace("{{" + key + "}}", str(val))
    return tpl


class FileHostHandler(BaseHTTPRequestHandler):
    server_version = "filehost/" + VERSION
    sys_version = ""

    def log_message(self, format, *args):
        pass

    def send_error_page(self, code, message=""):
        body = render_template("msg.html",
            title=f"{code}",
            heading=f"{code}",
            message=message or self._default_msg(code),
            version=VERSION
        )
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode())))
        for k, v in NO_CACHE.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def _default_msg(self, code):
        msgs = {
            400: "bad request",
            403: "access denied",
            404: "the requested resource was not found",
            405: "method not allowed",
            500: "internal server error",
        }
        return msgs.get(code, "error")

    def send_file(self, file_path):
        try:
            st = os.stat(file_path)
            if stat.S_ISDIR(st.st_mode):
                self.send_error_page(404)
                return

            file_size = st.st_size
            mime_type = guess_mime(file_path)
            last_modified = format_time(st.st_mtime)

            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Last-Modified", last_modified)
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(32768)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except FileNotFoundError:
            self.send_error_page(404)
        except PermissionError:
            self.send_error_page(403)
        except Exception:
            self.send_error_page(500)

    def do_GET(self):
        parsed = urlparse(self.path)
        raw_path = unquote(parsed.path)
        query = parse_qs(parsed.query)

        # strip leading slash and normalize
        vpath = raw_path.lstrip("/")

        # embedded static resources
        if vpath.startswith(".res"):
            if vpath == ".res" or vpath == ".res/":
                self.send_error_page(404)
                return
            resource_path = os.path.join(BASE_DIR, "web/", vpath[5:])
            self.send_file(resource_path)
            return

        # health check
        if raw_path == "/ping":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # root / splash page
        if raw_path == "/" or raw_path == "":
            self._serve_splash(query)
            return

        # browse shared directory
        if vpath.startswith("shared"):
            self._serve_browse(vpath, query)
            return

        # upload listing
        if vpath.startswith("uploads"):
            self._serve_browse(vpath, query)
            return

        # login handler
        if vpath == "login":
            self._serve_login_page(query)
            return

        # settings page
        if vpath == "settings":
            self._serve_settings(query)
            return

        self.send_error_page(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        raw_path = unquote(parsed.path)
        vpath = raw_path.lstrip("/")

        content_length = int(self.headers.get("Content-Length", 0))

        if vpath == "login":
            body = self.rfile.read(content_length).decode("utf-8", errors="replace")
            params = parse_qs(body)
            pwd = params.get("password", [""])[0]

            if pwd:
                # always reject - no valid accounts configured
                self._serve_login_page({}, error="incorrect password")
            else:
                self._serve_login_page({}, error="password required")
            return

        if vpath == "contact":
            self._handle_contact(content_length)
            return

        self.send_error_page(405)

    def do_HEAD(self):
        # HEAD responses should not include body
        # For simplicity, just handle health check
        parsed = urlparse(self.path)
        raw_path = unquote(parsed.path)
        if raw_path == "/ping" or raw_path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

    def _serve_splash(self, query):
        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(SHARED_DIR):
            file_count += len(files)
            for f in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, f))
                except:
                    pass

        body = render_template("splash.html",
            version=VERSION,
            codename=CODENAME,
            build_date=BUILD_DT,
            file_count=str(file_count),
            total_size=format_size(total_size),
            uptime=self._get_uptime(),
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode())))
        for k, v in NO_CACHE.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def _serve_browse(self, vpath, query):
        rel = vpath
        abs_base = os.path.join(BASE_DIR, rel)
        abs_path = os.path.realpath(abs_base)

        # ensure we stay within appropriate dirs
        allowed_roots = [
            os.path.realpath(SHARED_DIR),
            os.path.realpath(UPLOAD_DIR),
        ]

        if not any(abs_path.startswith(root) for root in allowed_roots):
            self.send_error_page(403)
            return

        if not os.path.isdir(abs_path):
            if os.path.isfile(abs_path):
                self.send_file(abs_path)
                return
            self.send_error_page(404)
            return

        entries = []
        try:
            for name in sorted(os.listdir(abs_path)):
                if name.startswith("."):
                    continue
                full = os.path.join(abs_path, name)
                try:
                    st = os.stat(full)
                    is_dir = stat.S_ISDIR(st.st_mode)
                    entries.append({
                        "name": name + ("/" if is_dir else ""),
                        "size": format_size(st.st_size) if not is_dir else "-",
                        "modified": format_time(st.st_mtime),
                        "href": "/" + rel.rstrip("/") + "/" + name + ("/" if is_dir else ""),
                    })
                except:
                    continue
        except PermissionError:
            self.send_error_page(403)
            return

        rows = ""
        for e in entries:
            rows += f'<tr><td><a href="{e["href"]}">{e["name"]}</a></td>'
            rows += f'<td>{e["size"]}</td><td>{e["modified"]}</td></tr>\n'

        parent = "/" + "/".join(rel.rstrip("/").split("/")[:-1])
        if parent == "/":
            parent_link = ""
        else:
            parent_link = f'<tr><td><a href="{parent}/">..</a></td><td>-</td><td>-</td></tr>'

        body = render_template("browser.html",
            title=rel,
            path="/" + rel,
            rows=parent_link + rows,
            count=str(len(entries)),
            version=VERSION,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode())))
        for k, v in NO_CACHE.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def _serve_login_page(self, query, error=""):
        error_html = f'<p class="err">{error}</p>' if error else ""
        body = render_template("login.html",
            version=VERSION,
            error=error_html,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode())))
        for k, v in NO_CACHE.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def _serve_settings(self, query):
        body = render_template("settings.html",
            version=VERSION,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode())))
        for k, v in NO_CACHE.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body.encode())

    def _handle_contact(self, content_length):
        body_data = self.rfile.read(content_length).decode("utf-8", errors="replace")
        resp_body = render_template("msg.html",
            title="Message Sent",
            heading="Thank you",
            message="Your message has been received. We will get back to you shortly.",
            version=VERSION,
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(resp_body.encode())))
        self.end_headers()
        self.wfile.write(resp_body.encode())

    def _get_uptime(self):
        try:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        except:
            return "unknown"


def main():
    host = "0.0.0.0"
    port = 80

    # ensure directories exist
    os.makedirs(SHARED_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    server = HTTPServer((host, port), FileHostHandler)
    print(f"filehost v{VERSION} \"{CODENAME}\" listening on {host}:{port}")
    print(f"  web dir: {WEB_DIR}")
    print(f"  shared:  {SHARED_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
