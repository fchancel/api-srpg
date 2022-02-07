from typing import Optional
from api.schemas import Response400, Response401, Response403, Response404, Response409, Response500


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


# -------------------------------------------------#
#                                                  #
#               1.User                             #
#                                                  #
# -------------------------------------------------#


def open_api_response_login():
    return {
        400: {
            "model": Response400,
            "description": "Inactive User / User Email Not Verified"
        },
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
