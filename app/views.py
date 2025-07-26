from sanic import Blueprint
from sanic.response import json
from sanic_ext import render

bp_programs = Blueprint("programs", url_prefix="/programs")


@bp_programs.get("/", name="programs_list")  # Name the endpoint for easy routing)
async def get_programs(request):
    return json({"programs": ["Program 1", "Program 2", "Program 3"]})


@bp_programs.get("/<program_id:str>", name="program_detail")
async def get_program(request, program_id: str):
    return await render("programs.html", context={"program_id": program_id})
