from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from sanic_ext import Extend, render

from views import bp_programs

app = Sanic(__name__)
Extend(app)
app.blueprint(bp_programs)
app.static("/static/", "static/", name="static")
app.static("/images/", "static/img/", name="images")


@app.get("", name="index")
async def index(request: Request):
    print(app.url_for("programs.programs_list"))  # Example URL
    return await render(
        "index.html",
        context={"message": "Hello, World!"},
    )


# def create_app(config=None) -> Sanic:
#     app = Sanic(__name__)
#     return app
