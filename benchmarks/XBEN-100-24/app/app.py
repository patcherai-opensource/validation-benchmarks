import os
import logging

import tornado.ioloop
import tornado.web

from handlers.main import MainHandler
from handlers.base import BaseHandler
from handlers.config import ConfigHandler
from handlers.login import LoginHandler
from handlers.cameras import CameraHandler
from handlers.log import LogHandler
import settings

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')


def make_app():
    return tornado.web.Application(
        [
            (r'^/$', MainHandler),
            (r'^/login/?$', LoginHandler),
            (r'^/config/(?P<op>add|list|backup|restore)/?$', ConfigHandler),
            (r'^/camera/(?P<camera_id>\d+)/(?P<op>current|snapshot)/?$', CameraHandler),
            (r'^/log/(?P<name>\w+)/?$', LogHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        cookie_secret=settings.COOKIE_SECRET,
        xsrf_cookies=False,
        debug=False,
    )


def main():
    app = make_app()
    port = int(os.environ.get('PORT', 5003))
    app.listen(port)
    logging.info('motionEye started on port %d', port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
