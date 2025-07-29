from sanic import Blueprint, exceptions
from sanic.response import json
from sanic_ext import render

from utils.reader import read_models_yml, get_model_by_name
from utils.services import (
    GoogleDriveService,
    contains_pdf_or_folder,
    format_files_list,
    slugify,
    sort_by_name,
)

bp_programs = Blueprint("programs", url_prefix="/programs")


@bp_programs.get("/", name="programs_list")  # Name the endpoint for easy routing)
async def get_programs(request):
    programs = read_models_yml()
    return json({"programs": programs})


@bp_programs.get("/<program_id:str>", name="program_areas")
async def get_program(request, program_id: str):
    programs = get_model_by_name("programs")
    program = programs.get(program_id)
    if program is None:
        raise exceptions.NotFound("Program not found")

    drive_service = GoogleDriveService("./credentials.json")
    print(f"PROGRAM ---> {program.get('id'), program.get('name')}")
    print(f"Files for program {program.get("id")}:")
    files = drive_service.list_files(program.get("id"))
    from pprint import pprint

    # pprint(files)
    sorted_files = sort_by_name(files)
    for file in sorted_files:
        file["slug"] = slugify(file["name"])
    # return json({"files": sorted_files, "program": program})
    return await render(
        "programs.html",
        context={
            "program": program,
            "files": sorted_files,
        },
    )


@bp_programs.get(
    "/<program_id:str>/area/<area_id:str>/<drive_id:str>",
    name="area_parameters",
)
async def get_area_parameters(request, program_id: str, area_id: str, drive_id: str):

    programs = get_model_by_name("programs")
    program = programs.get(program_id)
    drive_service = GoogleDriveService("./credentials.json")
    files = drive_service.list_files(drive_id)
    sorted_files = sort_by_name(files)
    return await render(
        "parameters.html",
        context={"files": sorted_files, "program": program},
    )


@bp_programs.get("<program_id:str>/parameters/<drive_id:str>", name="parameter_details")
async def get_parameter_details(request, drive_id, program_id: str):
    programs = get_model_by_name("programs")
    program = programs.get(program_id)
    drive_service = GoogleDriveService("./credentials.json")

    files_list = drive_service.list_files(drive_id)

    # formatted_files_list = format_files_list(files_list)
    # print(f"Formatted list: {formatted_files_list}")
    for file in files_list:
        _files = drive_service.list_files(file["id"])
        sorted_files = sort_by_name(_files)
        file["files"] = sorted_files
    sorted_files = sort_by_name(files_list)
    return json({"files": sorted_files, "program": program})
