import os
from mitmproxy import exceptions
from mitmproxy.addons.resource_temp import ResourceTemp, RewriteMeta
from mitmproxy import ctx, http


class ResourceInfo:
    def __init__(self):
        self.temp = ResourceTemp()
        self._resource_path = os.path.join(ctx.options.resource_path, self.temp.flag)
        self.response_path = os.path.join(self._resource_path, self.temp.response_flag)
        self.rewrite_path = os.path.join(self._resource_path, self.temp.tname.rewrite)

    def enable(self):
        return os.path.exists(self._resource_path)

    def check_resource_path(self):
        if os.path.exists(self._resource_path):
            return
        try:
            os.mkdir(self._resource_path)
            os.mkdir(self.response_path)
            with open(os.path.join(self._resource_path, self.temp.tname.rewrite), 'w', encoding='u8') as f:
                f.write(self.temp.rewrite())
            with open(os.path.join(self._resource_path, self.temp.tname.readme), 'w', encoding='u8') as f:
                f.write(self.temp.readme())

        except ValueError as e:
            raise exceptions.OptionsError(e)


class ResourceAddon:
    res_info: ResourceInfo
    rewrite_meta: RewriteMeta

    def load(self, loader):
        loader.add_option(
            "resource_path", str, os.getcwd(), "rewrite资源根路径"
        )

    def _enable_resource(self):
        return ctx.options.enable_resource and self.res_info.enable()

    def running(self):
        self.res_info = ResourceInfo()
        if ctx.options.enable_resource:
            self.res_info.check_resource_path()
            self.rewrite_meta = RewriteMeta(self.res_info.rewrite_path, self.res_info.response_path)
            self.rewrite_meta.watch_file()

    def done(self):
        self.rewrite_meta.cancel_watch_file()

    def request(self, flow: http.HTTPFlow):
        if not self._enable_resource():
            return
        self.rewrite_meta.request(flow)

    def response(self, flow: http.HTTPFlow):
        if not self._enable_resource():
            return
        self.rewrite_meta.response(flow)

