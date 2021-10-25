#!/usr/bin/env python3

""" HTTP server and launcher for Winnow """

import argparse
import logging
import http.server
import socketserver
import os

PORT = 8001

BUNDLE_DIR = os.path.abspath(os.path.dirname(__file__))


class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "www-data/index.html"
        else:
            self.path = "www-data" + self.path

        logging.debug(self.path)
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def main():
    """ Command-line entry-point. """

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Increase verbosity"
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    handler = HttpRequestHandler

    socketserver.TCPServer.allow_reuse_address = True

    os.chdir(BUNDLE_DIR)
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        logging.info("Server started at localhost:" + str(PORT))
        httpd.serve_forever()


if __name__ == "__main__":
    main()
