from typing import Optional
from api.schemas import Response204, Response400, Response401, Response403, Response404, Response409, Response500


# -------------------------------------------------#
#                   MENU                           #
#                                                  #
#               0.General                          #
#               1.User                             #
#               2.Character                        #
#               3.Mission                          #
# -------------------------------------------------#

# -------------------------------------------------#
#                                                  #
#               0.General                          #
#                                                  #
# -------------------------------------------------#


def open_api_response_error_server(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        500: {
            "model": Response500,
            "description": f"Server Error {split}{adding_message if adding_message else ''}"
        },
    }


def open_api_response_no_content(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        204: {
            "model": Response204,
            "description": f"No Content {split}{adding_message if adding_message else ''}"
        },
    }


# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#


def open_api_response_login():
    return {
        401: {
            "model": Response401,
            "description": "Not authenticated"
        }
    }


def open_api_response_target_user(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        404: {
            "model": Response404,
            "description": f"Targer user Not Found {split}{adding_message}"
        },
    }


def open_api_response_invalid_token(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        401: {
            "model": Response401,
            "description": f"Invalid Token {split}{adding_message}"
        },
    }


# -------------------------------------------------#
#                                                  #
#               2.Character                        #
#                                                  #
# -------------------------------------------------#


def open_api_response_not_found_character(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        404: {
            "model": Response404,
            "description": f"Character Not Found {split}{adding_message if adding_message else ''}"
        },
    }


def open_api_response_not_yours_character(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        403: {
            "model": Response403,
            "description": f"Character is not yours {split}{adding_message if adding_message else ''}"
        },
    }


# -------------------------------------------------#
#                                                  #
#               3.Mission                          #
#                                                  #
# -------------------------------------------------#


def open_api_response_already_exist_mission(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        409: {
            "model": Response409,
            "description": f"Mission Already Exist {split}{adding_message if adding_message else ''}"
        },
    }


def open_api_response_not_found_mission(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        404: {
            "model": Response404,
            "description": f"Mission Not Found {split}{adding_message if adding_message else ''}"
        },
    }


def open_api_response_not_found_choice(adding_message: Optional[str] = None):
    if adding_message:
        split = "/ "
    else:
        split = ""
    return {
        404: {
            "model": Response404,
            "description": f"Choice Not Found {split}{adding_message if adding_message else ''}"
        },
    }
