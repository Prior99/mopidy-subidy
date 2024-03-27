import os
import logging

import tornado.web
import tornado.httpclient

from urllib.parse import urlparse

logger = logging.getLogger('subidy-web')


def image_proxy_factory(config, core):
    return [
        (r"/coverart/(?P<id>.+)", ImageProxyHandler, {"core": core, "config": config})
    ]

class ImageProxyHandler(tornado.web.RequestHandler):
    def initialize(self, core, config):
        self.core = core

        subidy_config = config["subidy"]
        self._subsonic_url=subidy_config["url"]
        self._subsonic_username=subidy_config["username"]
        self._subsonic_password=subidy_config["password"]

    async def get(self, **kwargs):
        id = kwargs.get('id')

        logger.debug('Handle coverart %s request', id)

        def handle_response(response):
            if (response.error and not
                    isinstance(response.error, tornado.httpclient.HTTPError)):
                self.set_status(500)
                self.write('Internal server error:\n' + str(response.error))
            else:
                self.set_status(response.code, response.reason)
                self._headers = tornado.httputil.HTTPHeaders() # clear tornado default header

                for header, v in response.headers.get_all():
                    if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                        self.add_header(header, v) # some header appear multiple times, eg 'Set-Cookie'

                if response.body:                   
                    self.set_header('Content-Length', len(response.body))
                    self.write(response.body)
            self.finish()

        try:
            if 'Proxy-Connection' in self.request.headers:
                del self.request.headers['Proxy-Connection'] 
            resp = await fetch_request(
                f"{self._subsonic_url}/rest/getCoverArt?id={id}",
                method=self.request.method, headers=self.request.headers,
                auth_username=self._subsonic_username,
                auth_password=self._subsonic_password,
                follow_redirects=False, allow_nonstandard_methods=False)
            handle_response(resp)
        except tornado.httpclient.HTTPError as e:
            if hasattr(e, 'response') and e.response:
                handle_response(e.response)
            else:
                self.set_status(500)
                self.write('Internal server error:\n' + str(e))
                self.finish()

def get_proxy(url):
    url_parsed = urlparse(url, scheme='http')
    proxy_key = '%s_proxy' % url_parsed.scheme
    return os.environ.get(proxy_key)


def parse_proxy(proxy):
    proxy_parsed = urlparse(proxy, scheme='http')
    return proxy_parsed.hostname, proxy_parsed.port


def fetch_request(url, **kwargs):
    proxy = get_proxy(url)
    if proxy:
        logger.debug('Forward request via upstream proxy %s', proxy)
        tornado.httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient')
        host, port = parse_proxy(proxy)
        kwargs['proxy_host'] = host
        kwargs['proxy_port'] = port

    req = tornado.httpclient.HTTPRequest(url, **kwargs)
    client = tornado.httpclient.AsyncHTTPClient()
    return client.fetch(req, raise_error=False)
