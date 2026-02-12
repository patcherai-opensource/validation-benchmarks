"""copyparty HTTP client handler"""

import html
import json
import mimetypes
import os
import posixpath
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler

import jinja2


def unquotep(s):
    """URL-decode a path component"""
    return urllib.parse.unquote(s)


def humansize(nbytes):
    suffixes = ["B", "KiB", "MiB", "GiB", "TiB"]
    i = 0
    while nbytes >= 1024 and i < len(suffixes) - 1:
        nbytes /= 1024.0
        i += 1
    f = ("%.1f" % nbytes).rstrip("0").rstrip(".")
    return "%s %s" % (f, suffixes[i])


def fmt_mtime(ts):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))


class CopypartyHandler(BaseHTTPRequestHandler):
    mod_dir = ""
    srv_dir = ""
    version = "1.8.1"
    volumes = {}

    server_version = "copyparty"
    sys_version = ""

    def version_string(self):
        return "copyparty"

    def log_message(self, format, *args):
        ts = time.strftime("%H:%M:%S")
        msg = format % args
        print("[%s] %s %s" % (ts, self.address_string(), msg))

    def do_GET(self):
        self.handle_request("GET")

    def do_HEAD(self):
        self.handle_request("HEAD")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length else b""
        self.handle_request("POST", post_data)

    def handle_request(self, method, post_data=None):
        parsed = urllib.parse.urlparse(self.path)
        raw_path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # URL-decode the path
        vpath = unquotep(raw_path)

        # Normalize leading slash
        if vpath.startswith("/"):
            vpath = vpath[1:]

        # Handle embedded resources (.cpr/ prefix)
        if vpath.startswith(".cpr"):
            return self.handle_cpr(vpath)

        # Handle API endpoints
        if vpath.startswith(".api/"):
            return self.handle_api(vpath, query)

        # Handle file browser / directory listing
        return self.handle_browse(vpath, query, method)

    def handle_cpr(self, vpath):
        """Serve embedded/static resources from the web/ directory"""

        if vpath == ".cpr" or vpath == ".cpr/":
            self.send_error_page(404, "not found")
            return

        # Serve the static resource from web/ subdirectory
        res_suffix = vpath[5:]  # strip ".cpr/" prefix
        static_path = os.path.join(self.mod_dir, "web", res_suffix)

        if os.path.isfile(static_path):
            return self.tx_file(static_path)

        self.send_error_page(404, "not found")
        return

    def handle_api(self, vpath, query):
        """Handle API requests"""
        endpoint = vpath[5:]

        if endpoint == "status":
            data = {
                "version": self.version,
                "uptime": int(time.time()),
                "volumes": len(self.volumes),
            }
            self.send_json(data)
            return

        if endpoint == "ls":
            path = query.get("path", ["/"])[0]
            vol_path = self.resolve_vol_path(path)
            if vol_path and os.path.isdir(vol_path):
                entries = []
                try:
                    for name in sorted(os.listdir(vol_path)):
                        fp = os.path.join(vol_path, name)
                        if name.startswith("."):
                            continue
                        st = os.stat(fp)
                        entries.append(
                            {
                                "name": name,
                                "sz": st.st_size if os.path.isfile(fp) else 0,
                                "ts": int(st.st_mtime),
                                "is_dir": os.path.isdir(fp),
                            }
                        )
                except OSError:
                    pass
                self.send_json({"entries": entries, "path": path})
            else:
                self.send_json({"error": "path not found"}, 404)
            return

        self.send_json({"error": "unknown endpoint"}, 404)

    def handle_browse(self, vpath, query, method):
        """Handle directory browsing and file downloads"""

        # Root redirect
        if not vpath or vpath == "/":
            vpath = ""

        vol_path = self.resolve_vol_path("/" + vpath)

        if vol_path is None:
            # Show splash page for root
            if not vpath:
                return self.tx_splash()
            self.send_error_page(404, "not found")
            return

        if os.path.isdir(vol_path):
            return self.tx_dir_listing(vpath, vol_path)

        if os.path.isfile(vol_path):
            return self.tx_file(vol_path)

        self.send_error_page(404, "not found")

    def resolve_vol_path(self, url_path):
        """Resolve a URL path to a filesystem path through volumes"""
        url_path = url_path.rstrip("/")
        if not url_path:
            url_path = "/"

        best_match = None
        best_len = -1

        for vpath, fspath in self.volumes.items():
            vpath_norm = vpath.rstrip("/")
            if not vpath_norm:
                vpath_norm = "/"

            if url_path == vpath_norm or url_path.startswith(vpath_norm + "/"):
                if len(vpath_norm) > best_len:
                    best_match = (vpath_norm, fspath)
                    best_len = len(vpath_norm)

        if best_match is None:
            return None

        vpath_norm, fspath = best_match
        remainder = url_path[len(vpath_norm) :].lstrip("/")

        if remainder:
            full_path = os.path.join(fspath, remainder)
        else:
            full_path = fspath

        # Basic sanitization - prevent traversal outside volume
        real_path = os.path.realpath(full_path)
        real_base = os.path.realpath(fspath)
        if not real_path.startswith(real_base):
            return None

        return full_path

    def tx_splash(self):
        """Render the copyparty splash page"""
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(self.mod_dir, "web")
            ),
            autoescape=True,
        )
        try:
            tpl = env.get_template("splash.html")
            volumes_info = []
            for vpath, fspath in self.volumes.items():
                try:
                    nfiles = len(
                        [
                            f
                            for f in os.listdir(fspath)
                            if not f.startswith(".")
                        ]
                    )
                except OSError:
                    nfiles = 0
                volumes_info.append(
                    {"path": vpath, "nfiles": nfiles}
                )

            body = tpl.render(
                version=self.version,
                volumes=volumes_info,
                uname="*",
            )
            self.send_html(body)
        except Exception:
            self.send_error_page(500, "internal error")

    def tx_dir_listing(self, vpath, fs_path):
        """Render a directory listing"""
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                os.path.join(self.mod_dir, "web")
            ),
            autoescape=True,
        )
        try:
            tpl = env.get_template("browser.html")
            entries = []
            try:
                for name in sorted(os.listdir(fs_path)):
                    if name.startswith("."):
                        continue
                    fp = os.path.join(fs_path, name)
                    try:
                        st = os.stat(fp)
                    except OSError:
                        continue
                    entries.append(
                        {
                            "name": name,
                            "href": urllib.parse.quote(name)
                            + ("/" if os.path.isdir(fp) else ""),
                            "sz": humansize(st.st_size)
                            if os.path.isfile(fp)
                            else "-",
                            "raw_sz": st.st_size
                            if os.path.isfile(fp)
                            else 0,
                            "ts": fmt_mtime(st.st_mtime),
                            "is_dir": os.path.isdir(fp),
                        }
                    )
            except OSError:
                pass

            breadcrumbs = []
            parts = vpath.split("/") if vpath else []
            for i, part in enumerate(parts):
                breadcrumbs.append(
                    {
                        "name": part,
                        "href": "/" + "/".join(parts[: i + 1]) + "/",
                    }
                )

            body = tpl.render(
                version=self.version,
                path="/" + vpath,
                breadcrumbs=breadcrumbs,
                entries=entries,
                nfiles=len([e for e in entries if not e["is_dir"]]),
                ndirs=len([e for e in entries if e["is_dir"]]),
            )
            self.send_html(body)
        except Exception:
            self.send_error_page(500, "internal error")

    def tx_file(self, filepath):
        """Send a file to the client"""
        try:
            ct, _ = mimetypes.guess_type(filepath)
            if ct is None:
                ct = "application/octet-stream"

            st = os.stat(filepath)
            with open(filepath, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(data)))
            self.send_header(
                "Last-Modified",
                self.date_time_string(int(st.st_mtime)),
            )
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error_page(404, "not found")
        except PermissionError:
            self.send_error_page(403, "forbidden")
        except Exception:
            self.send_error_page(500, "internal error")

    def send_html(self, body, code=200):
        data = body.encode("utf-8", "replace")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_error_page(self, code, message):
        body = """<!DOCTYPE html>
<html><head><title>%d %s</title>
<style>body{font-family:sans-serif;color:#333;background:#f7f7f7;max-width:40em;margin:2em auto;padding:0 1em}
h1{color:#900;border-bottom:1px solid #ccc}a{color:#047}</style>
</head><body><h1>%d %s</h1>
<p><a href="/">go home</a></p>
<hr><p><small>copyparty/%s</small></p>
</body></html>""" % (
            code,
            html.escape(message),
            code,
            html.escape(message),
            self.version,
        )
        self.send_html(body, code)
