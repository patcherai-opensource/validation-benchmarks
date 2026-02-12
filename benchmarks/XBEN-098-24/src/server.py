#!/usr/bin/env python3
"""copyparty - the party file server"""

import argparse
import os
import signal
import sys
import threading
from http.server import HTTPServer

from httpcli import CopypartyHandler

__version__ = "1.8.1"
__build_dt__ = "2023-06-20"


def main():
    parser = argparse.ArgumentParser(
        description="copyparty v%s (%s) - file server" % (__version__, __build_dt__)
    )
    parser.add_argument(
        "--port", "-p", type=int, default=3923, help="listening port (default: 3923)"
    )
    parser.add_argument(
        "--bind", "-i", default="0.0.0.0", help="bind address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--vol",
        "-v",
        action="append",
        default=None,
        help="volume definitions (src:dst:perm)",
    )
    parser.add_argument(
        "--no-dedup", action="store_true", help="disable deduplication"
    )
    parser.add_argument(
        "--no-thumb", action="store_true", help="disable thumbnails"
    )
    parser.add_argument(
        "--no-mtag", action="store_true", help="disable media tags"
    )
    parser.add_argument(
        "--ansi", action="store_true", default=True, help="enable ANSI colors in log"
    )
    args = parser.parse_args()

    mod_dir = os.path.dirname(os.path.abspath(__file__))
    srv_dir = os.path.join(mod_dir, "srv")

    if not os.path.isdir(srv_dir):
        os.makedirs(srv_dir, exist_ok=True)

    CopypartyHandler.mod_dir = mod_dir
    CopypartyHandler.srv_dir = srv_dir
    CopypartyHandler.version = __version__

    # Setup volumes
    vols = {}
    if args.vol:
        for vdef in args.vol:
            parts = vdef.split(":")
            if len(parts) >= 2:
                vols[parts[1]] = parts[0]
    if not vols:
        vols["/"] = srv_dir

    CopypartyHandler.volumes = vols

    server = HTTPServer((args.bind, args.port), CopypartyHandler)

    def shutdown_handler(signum, frame):
        print("\ncopyparty: shutting down...")
        threading.Thread(target=server.shutdown).start()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    print(
        "\033[1;32mcopyparty v%s (%s)\033[0m" % (__version__, __build_dt__)
    )
    print(
        "  listening on \033[36mhttp://%s:%d/\033[0m"
        % (args.bind, args.port)
    )
    for vpath, fspath in vols.items():
        print("  vol: \033[33m%s\033[0m => %s" % (vpath, fspath))
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("copyparty: stopped")


if __name__ == "__main__":
    main()
