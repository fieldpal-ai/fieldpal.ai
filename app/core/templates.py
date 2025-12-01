from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from fastapi.responses import HTMLResponse

BASE_DIR = Path(__file__).resolve().parent.parent.parent
jinja_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))

def render_template(template_name: str, **context) -> HTMLResponse:
    """Render a Jinja2 template"""
    template = jinja_env.get_template(template_name)
    html_content = template.render(**context)
    return HTMLResponse(content=html_content)

