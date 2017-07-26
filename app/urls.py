from app.views import DownloaderHandler, ResourceHandler, BatchDownloaderHandler

handlers = [
    (r'/capture', DownloaderHandler),
    (r'/batch/capture', BatchDownloaderHandler),
    (r'/resources', ResourceHandler),
    (r'/resources/(.+)', ResourceHandler),
]
