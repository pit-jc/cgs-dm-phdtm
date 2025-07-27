from sanic import Blueprint
from sanic.response import json
from sanic_ext import render

from utils.reader import read_models_yml, get_model_by_name
from utils.services import GoogleDriveService, sort_by_name

bp_programs = Blueprint("programs", url_prefix="/programs")


@bp_programs.get("/", name="programs_list")  # Name the endpoint for easy routing)
async def get_programs(request):
    programs = read_models_yml()
    return json({"programs": programs})


@bp_programs.get("/<program_id:str>", name="program_detail")
async def get_program(request, program_id: str):
    programs = get_model_by_name("programs")  # Example usage
    program = programs.get(program_id)

    drive_service = GoogleDriveService("./credentials.json")
    files = drive_service.list_files(program.get("id"))
    sorted_files = sort_by_name(files)
    return await render(
        "programs.html",
        context={
            "program": program,
            "files": sorted_files,
        },
    )
