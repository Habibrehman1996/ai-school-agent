from langchain.tools import tool

from edap_client import (
    get_class_attendance,
    get_student_attendance,
    get_student_details,
)


# =========================================================
# CLASS ATTENDANCE TOOL
# =========================================================

@tool
async def get_attendance_tool(
    course_name: str,
    section_name: str,
    date_text: str,
) -> dict:
    """
    EDAP se kisi class aur section ki
    specific date ki attendance retrieve karta hai.

    Example:

    course_name:
        CLASS FIVE

    section_name:
        BLUE-A

    date_text:
        24 September 2026

    Use this tool for class-level attendance questions.
    """

    return await get_class_attendance(
        course_name=course_name,
        section_name=section_name,
        date_text=date_text,
    )


# =========================================================
# STUDENT ATTENDANCE TOOL
# =========================================================

@tool
async def get_student_attendance_tool(
    student_name: str,
    course_name: str,
    section_name: str,
    start_date: str,
    end_date: str,
) -> dict:
    """
    EDAP se kisi specific student ki
    date-range attendance retrieve karta hai.

    Example:

    student_name:
        Rahib

    course_name:
        CLASS FIVE

    section_name:
        BLUE-A

    start_date:
        1 September 2026

    end_date:
        24 September 2026

    Use this tool for questions such as:

    - Rahib September mein kitne din present tha?
    - Rahib kitne din absent tha?
    - Rahib ki attendance percentage kya hai?
    """

    return await get_student_attendance(
        student_name=student_name,
        course_name=course_name,
        section_name=section_name,
        start_date=start_date,
        end_date=end_date,
    )


# =========================================================
# STUDENT DETAILS TOOL
# =========================================================

@tool
async def get_student_details_tool(
    student_name: str,
    course_name: str,
    section_name: str,
    date_text: str = "today",
) -> dict:
    """
    EDAP se student ki basic details retrieve karta hai.

    Available information may include:

    - Name
    - Student number
    - GR number
    - Father name
    - Father contact
    - Mother name
    - Mother contact
    - Attendance status
    - Attendance time

    Use this tool when authorized school staff
    asks for a student's details.
    """

    return await get_student_details(
        student_name=student_name,
        course_name=course_name,
        section_name=section_name,
        date_text=date_text,
    )


# =========================================================
# ALL TOOLS
# =========================================================

tools = [
    get_attendance_tool,
    get_student_attendance_tool,
    get_student_details_tool,
]