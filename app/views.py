import json

import tornado.web
from tornado.escape import json_encode

from app.models import get_task, get_tasks_by_status
from app.offline import download


class BaseHandler(tornado.web.RequestHandler):
    def render_json(self, value):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json_encode(value))

    def write_error(self, status_code, **kwargs):
        try:
            self.set_status(status_code)
            self.write(kwargs)
            self.finish()
        except Exception:
            super(BaseHandler, self).write_error(status_code, **kwargs)


class DownloaderHandler(BaseHandler):
    def post(self):
        capture_url = json.loads(self.request.body).get('url', '')
        download.delay(json.dumps({'url': capture_url}))
        self.set_status(201)


class BatchDownloaderHandler(BaseHandler):
    def post(self):
        capture_urls = json.loads(self.request.body).get('urls', [])
        for url in capture_urls:
            download.delay(json.dumps({'url': url}))
        self.set_status(201)


class ResourceHandler(BaseHandler):
    def get(self, url=None):
        if not url:
            status = self.get_argument('status', 'done')
            task_urls = get_tasks_by_status(status)
            res = []
            for url in task_urls:
                res.append(get_task(url))
            self.render_json(res)
        else:
            self.render_json(get_task(url))
