import os
from jinja2 import FileSystemLoader, TemplateNotFound

# Permet de trouver les sous-dossiers à "templates"
# pour ne pas avoir à spécifier le nom du dossier dans un appel à "render_template"
class RecursiveFileSystemLoader(FileSystemLoader):
    def get_source(self, environment, template):
        for searchpath in self.searchpath:
            for root, _, files in os.walk(searchpath):
                if template in files:
                    template_path = os.path.join(root, template)
                    with open(template_path, 'r') as f:
                        contents = f.read()
                    mtime = os.path.getmtime(template_path)
                    def uptodate():
                        try:
                            return os.path.getmtime(template_path) == mtime
                        except OSError:
                            return False
                    return contents, template_path, uptodate
        raise TemplateNotFound(template)
