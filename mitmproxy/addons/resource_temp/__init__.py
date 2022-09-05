import os

current_path = os.path.dirname(__file__)


class ResourceTemp:
    flag = 'mitmres'
    response_flag = 'response'

    class tname:
        public_rewrite = 'public_rewrite.yaml'
        readme = 'readme.md'
        rewrite = 'rewrite.yaml'

    def public_rewrite(self):
        with open(os.path.join(current_path, self.tname.public_rewrite), encoding='u8') as f:
            return f.read()

    def readme(self):
        with open(os.path.join(current_path, self.tname.readme), encoding='u8') as f:
            return f.read()

    def rewrite(self):
        with open(os.path.join(current_path, self.tname.rewrite), encoding='u8') as f:
            return f.read()
