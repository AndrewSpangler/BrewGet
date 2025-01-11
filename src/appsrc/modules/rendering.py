import os
from jinja2 import Environment, FileSystemLoader

class TemplateRenderer():
    def __init__(self, template_dir:os.PathLike, script_template:os.PathLike):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self._render = self.env.get_template(script_template).render

    def render(self, **kw) -> str:
        return self._render(kw)