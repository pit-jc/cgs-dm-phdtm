from sanic import Blueprint, exceptions
from sanic.response import json
from sanic_ext import render

from utils.reader import read_models_yml, get_model_by_name
from utils.services import (
    GoogleDriveService,
    extract_area_and_title,
    slugify,
    sort_by_name,
    unslugify,
)

bp_programs = Blueprint("programs", url_prefix="/colleges")


@bp_programs.get(
    "/<college_id:str>",
    name="programs_list",
)
async def get_college(request, college_id: str):
    colleges = get_model_by_name("colleges")
    from pprint import pprint

    print(f"COLLEGES --> {colleges}")
    college = colleges.get(college_id)
    if college is None:
        raise exceptions.NotFound("College not found")

    return await render(
        "home.html",
        context={
            "colleges": colleges,
            "data": college,
            "college": college,
            "college_id": college_id,
        },
    )


@bp_programs.get(
    "/<college_id:str>/<program_id:str>",
    name="program_areas",
)
async def get_program_areas(request, college_id: str, program_id: str):
    colleges = get_model_by_name("colleges")
    college = colleges.get(college_id)
    print(f"COLLEGES --> {college} ")
    if college is None:
        raise exceptions.NotFound("College not found")

    programs = college.get("programs")
    program = None
    for _program in programs:
        if _program["tag"] == program_id:
            program = _program
            break
    if program is None:
        raise exceptions.NotFound("Program not found")
    print(f"PROGRAM --> {program}")

    drive_service = GoogleDriveService("./credentials.json")
    files = drive_service.list_files(program.get("id"), type="folder")
    print(f"AREAS Files -> {files}")
    sorted_files = sort_by_name(files)
    for file in sorted_files:
        file["slug"] = slugify(file["name"])

    # Check if request wants JSON response
    if request.headers.get("Accept") == "application/json":
        return json({"files": sorted_files, "program": program, "college": college})

    return await render(
        "areas.html",
        context={
            "colleges": colleges,
            "college_id": college_id,
            "college": college,
            "data": program,
            "files": sorted_files,
        },
    )


@bp_programs.get(
    "/<college_id:str>/<program_id:str>/<area_id:str>/<drive_id:str>",
    name="area_parameters",
)
async def get_area_parameters(
    request,
    college_id: str,
    program_id: str,
    area_id: str,
    drive_id: str,
):
    colleges = get_model_by_name("colleges")
    college = colleges.get(college_id)
    if college is None:
        raise exceptions.NotFound("College not found")

    programs = college.get("programs")
    program = []
    for _program in programs:
        if _program["tag"] == program_id:
            program = _program
            break
    if not program:
        raise exceptions.NotFound("Program not found")

    drive_service = GoogleDriveService("./credentials.json")

    # program_areas = drive_service.list_files(program.get("id"))
    files = drive_service.list_files(drive_id, type="folder")
    print(f"FILES -> {files}")
    sorted_files = sort_by_name(files)
    area_title = extract_area_and_title(area_id)
    return await render(
        "parameters.html",
        context={
            # "areas": program_areas,
            "colleges": colleges,
            "college_id": college_id,
            "college": college,
            "files": sorted_files,
            "data": program,
            "area_title": area_title,
        },
    )


@bp_programs.get(
    "/<college_id:str>/<program_id:str>/parameters/<drive_id:str>",
    name="parameter_details",
)
async def get_parameter_details(
    request,
    college_id: str,
    drive_id: str,
    program_id: str,
):
    colleges = get_model_by_name("colleges")
    college = colleges.get(college_id)
    if college is None:
        raise exceptions.NotFound("College not found")

    programs = college.get("programs")
    program = []
    for _program in programs:
        if _program["tag"] == program_id:
            program = _program
            break
    if not program:
        raise exceptions.NotFound("Program not found")

    drive_service = GoogleDriveService("./credentials.json")
    # files_list = drive_service.list_files(drive_id, type="pdf")
    files_list = drive_service.list_files(drive_id)
    from pprint import pprint

    print("GET PARAMETER DETAILS")
    pprint(f"Files List -> {files_list}")
    for file in files_list:
        _files = drive_service.list_files(file["id"], type="pdf")
        sorted_files = sort_by_name(_files)
        file["files"] = sorted_files
    sorted_files = sort_by_name(files_list)
    return json({"files": sorted_files, "program": program})
