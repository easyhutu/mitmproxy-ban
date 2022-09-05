import os
from cacheout import Cache
from mitmproxy import exceptions
from mitmproxy.addons.resource_temp import ResourceTemp
from mitmproxy import ctx, http
from urllib.parse import urlparse
from ruamel import yaml
from mitmproxy.utils.data import dict_to_value


class ResourceInfo:
    def __init__(self):
        self.temp = ResourceTemp()
        self.resource_cache = Cache(ttl=30)
        self._resource_path = os.path.join(ctx.options.resource_path, self.temp.flag)
        self._response_path = os.path.join(self._resource_path, self.temp.response_flag)

    def enable(self):
        return os.path.exists(self._resource_path)

    def check_resource_path(self):
        if os.path.exists(self._resource_path):
            return
        try:
            os.mkdir(self._resource_path)
            os.mkdir(self._response_path)
            with open(os.path.join(self._resource_path, self.temp.tname.public_rewrite), 'w', encoding='u8') as f:
                f.write(self.temp.public_rewrite())
            with open(os.path.join(self._resource_path, self.temp.tname.rewrite), 'w', encoding='u8') as f:
                f.write(self.temp.rewrite())
            with open(os.path.join(self._resource_path, self.temp.tname.readme), 'w', encoding='u8') as f:
                f.write(self.temp.readme())

        except ValueError as e:
            raise exceptions.OptionsError(e)

    def _public_rewrite_info(self):
        if self.resource_cache.get(self.temp.tname.public_rewrite):
            return self.resource_cache.get(self.temp.tname.public_rewrite)
        with open(os.path.join(self._resource_path, self.temp.tname.public_rewrite), encoding='u8') as f:
            info = yaml.safe_load(f)
            self.resource_cache.set(self.temp.tname.public_rewrite, info)
        return info

    def _rewrite_info(self):
        if self.resource_cache.get(self.temp.tname.rewrite):
            return self.resource_cache.get(self.temp.tname.rewrite)
        with open(os.path.join(self._resource_path, self.temp.tname.rewrite), encoding='u8') as f:
            info = yaml.safe_load(f)
        for key in info.keys():
            if info[key].get('reply') and info[key].get('reply').endswith('.json'):
                with open(os.path.join(self._response_path, info[key]['reply']), encoding='u8') as f:
                    info[key]['reply'] = f.read()
        self.resource_cache.set(self.temp.tname.rewrite, info)
        return info

    def headers(self, url, tp):
        public = dict_to_value(self._public_rewrite_info(), f'headers.{tp}') or {}
        path = urlparse(url).path
        if path in list(self._rewrite_info().keys()):
            public.update(dict_to_value(self._rewrite_info()[path], f'headers.{tp}') or {})
        return public

    def reply(self, url):
        path = urlparse(url).path
        if path in list(self._rewrite_info().keys()):
            return dict_to_value(self._rewrite_info()[path], 'reply')
        return None


class ResourceAddon:
    res_info: ResourceInfo

    def load(self, loader):
        loader.add_option(
            'enable_resource', bool, True, "是否启用rewrite资源配置"
        )
        loader.add_option(
            "resource_path", str, os.getcwd(), "rewrite资源根路径"
        )

    def _enable_resource(self):
        return ctx.options.enable_resource and self.res_info.enable()

    def running(self):
        self.res_info = ResourceInfo()
        if ctx.options.enable_resource:
            self.res_info.check_resource_path()

    def request(self, flow: http.HTTPFlow):
        if not self._enable_resource():
            return
        headers = self.res_info.headers(flow.request.url, 'request')
        if headers:
            for k, v in headers.items():
                flow.request.headers[k] = v

    def response(self, flow: http.HTTPFlow):
        if not self._enable_resource():
            return
        headers = self.res_info.headers(flow.request.url, 'response')
        if headers:
            for k, v in headers.items():
                flow.response.headers[k] = v
        reply = self.res_info.reply(flow.request.url)
        if reply:
            flow.response.text = reply
            flow.response.headers['mock-status'] = 'success'

