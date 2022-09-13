import asyncio
import json
import os
from mitmproxy.utils.data import dict_to_value
from mitmproxy.http import HTTPFlow
from urllib.parse import urlparse
from mitmproxy import ctx
from cacheout import Cache
from ruamel import yaml
from mitmproxy.utils import asyncio_utils

current_path = os.path.dirname(__file__)


class ResourceTemp:
    flag = 'mitmres'
    response_flag = 'response'

    class tname:
        readme = 'readme.md'
        rewrite = 'rewrite.yaml'

    def readme(self):
        with open(os.path.join(current_path, self.tname.readme), encoding='u8') as f:
            return f.read()

    def rewrite(self):
        with open(os.path.join(current_path, self.tname.rewrite), encoding='u8') as f:
            return f.read()


class RContent:
    def __init__(self, path):
        self.path = path
        self.files_info = {}
        self.f_mtimes = []
        self.contents = {}

    def _join_path(self, filename):
        return os.path.join(self.path, filename)

    def update(self):
        now_filenames = os.listdir(self.path)
        for filename in now_filenames:
            try:
                nmt = os.stat(self._join_path(filename)).st_mtime
            except FileNotFoundError:
                ctx.log.error(f'{self.path} not found ignore')
                continue
            if nmt == self.files_info.get(filename):
                break
            ctx.log.info(self._join_path(filename))
            self.files_info[filename] = nmt
            with open(self._join_path(filename), 'rb') as f:
                self.contents[filename] = f.read()

    def has_filename(self, filename):
        return filename in list(self.files_info.keys())

    def get(self, filename):
        if self.has_filename(filename):
            return self.contents[filename]
        return None


class RewriteMeta:
    all_flag = '@all'
    ReloadInterval = 3

    def __init__(self, filepath, r_path):
        self.files = RContent(r_path)
        self.path = filepath
        self.url_paths = []
        self._mtime = 0
        self.public = {}
        self.info = {}
        self.watch_task = None

    def watch_file(self):
        self.watch_task = asyncio_utils.create_task(
            self.watcher(), name="watch rewrite file running...")

    def cancel_watch_file(self):
        if self.watch_task:
            self.watch_task.cancel()

    async def watcher(self):
        while True:
            self.update()
            self.files.update()
            await asyncio.sleep(self.ReloadInterval)

    def update(self):
        try:
            now_mtime = os.stat(self.path).st_mtime
        except FileNotFoundError:
            ctx.log.error(f'{self.path} not found ignore')
            return
        if self._mtime == now_mtime:
            return
        self._mtime = now_mtime
        ctx.log.info(self.path)

        with open(self.path, encoding='u8') as f:
            try:
                self.info = yaml.safe_load(f.read())
            except ValueError as e:
                ctx.log.error(f'load yaml err: {e}')
                return
        for k, v in self.info.items():
            if k == self.all_flag:
                self.public = v
            else:
                self.url_paths.append(k)

    def request(self, flow: HTTPFlow):
        self._u_headers(flow, 'request')

    def response(self, flow: HTTPFlow):
        self._u_headers(flow, 'response')
        self._u_content(flow, 'response')

    def _u_headers(self, flow, ty: str):
        path = urlparse(flow.request.url).path
        if not self.has_path(path):
            return None
        headers = dict_to_value(self.info, f'{path}.{ty}.headers') or {}
        headers.update(dict_to_value(self.public, f'{ty}.headers') or {})

        r = getattr(flow, ty)
        for k, v in headers.items():
            if v:
                r.headers[k] = v

    def _u_content(self, flow, ty: str):
        path = urlparse(flow.request.url).path
        if not self.has_path(path):
            return None
        content = self._generator_content(path, ty)
        if content is not False:
            r = getattr(flow, ty)
            r.content = content
            r.headers['mock-status'] = 'ok'

    def _generator_content(self, path, ty):
        val = dict_to_value(self.info, f'{path}.{ty}.content')
        if isinstance(val, dict):
            return json.dumps(val, ensure_ascii=False, separators=(',', ':')).encode('u8')
        if isinstance(val, bytes):
            return val
        if isinstance(val, str):
            return self.files.get(val) or val.encode('u8')
        return False

    def has_path(self, path):
        return path in self.url_paths or self.public
