from sanic import Blueprint, exceptions
from sanic.response import json
from sanic_ext import render

from utils.reader import read_models_yml, get_model_by_name
from utils.services import (
    GoogleDriveService,
    slugify,
    sort_by_name,
)

bp_programs = Blueprint("programs", url_prefix="/colleges")


@bp_programs.get(
    "/<college_id:str>",
    name="programs_list",
)
async def get_colleges(request, college_id: str):
    models = read_models_yml()
    colleges = models.get("colleges")
    college = colleges.get(college_id)
    if college is None:
        raise exceptions.NotFound("College not found")

    return await render(
        "home.html",
        context={
            "data": college,
        },
    )


@bp_programs.get(
    "/<college_id:str>/<program_id:str>/areas",
    name="program_areas",
)
async def get_program_areas(request, college_id: str, program_id: str):
    colleges = get_model_by_name("colleges")
    college = colleges.get(college_id)
    print(f"COLLEGES --> {college} ")
    if college is None:
        raise exceptions.NotFound("College not found")

    programs = college.get("programs")
    print(f"PROGRAMS --> {programs}, {college} ")
    program = None
    for _program in programs:
        if _program["tag"] == program_id:
            program = _program
    if program is None:
        raise exceptions.NotFound("Program not found")

    drive_service = GoogleDriveService("./credentials.json")
    # print(f"PROGRAM ---> {program.get('id'), program.get('name')}")
    # print(f"Files for program {program.get("id")}:")
    files = drive_service.list_files(program.get("id"))
    print(f"Files -> {files}")
    sorted_files = sort_by_name(files)
    for file in sorted_files:
        file["slug"] = slugify(file["name"])
    # return json({"files": sorted_files, "program": program})
    return await render(
        "areas.html",
        context={
            "data": program,
            "files": sorted_files,
        },
    )


@bp_programs.get(
    "/<program_id:str>/areas/<area_id:str>/<drive_id:str>/parameters",
    name="area_parameters",
)
async def get_area_parameters(request, program_id: str, area_id: str, drive_id: str):

    programs = get_model_by_name("programs")
    program = programs.get(program_id)
    drive_service = GoogleDriveService("./credentials.json")
    files = drive_service.list_files(drive_id)
    print(f"FILES -> {files}")
    print(f"AREA PARAMETERS ---> {area_id}, {program_id}")
    sorted_files = sort_by_name(files)
    area_num = None
    return await render(
        "parameters.html",
        context={
            "files": sorted_files,
            "program": program,
            "area_num": area_num,
        },
    )


# @bp_programs.get("<program_id:str>/parameters/<drive_id:str>", name="parameter_details")
# async def get_parameter_details(request, drive_id, program_id: str):
#     programs = get_model_by_name("programs")
#     program = programs.get(program_id)
#     drive_service = GoogleDriveService("./credentials.json")

#     files_list = drive_service.list_files(drive_id)

#     # formatted_files_list = format_files_list(files_list)
#     # print(f"Formatted list: {formatted_files_list}")
#     for file in files_list:
#         _files = drive_service.list_files(file["id"])
#         sorted_files = sort_by_name(_files)
#         file["files"] = sorted_files
#     sorted_files = sort_by_name(files_list)
#     return json({"files": sorted_files, "program": program})
