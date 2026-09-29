from langchain.tools import tool

from edap_client import (
    get_class_attendance,
    get_class_attendance_summary,
    get_class_student_list,
    get_student_attendance,
    get_student_attendance_summary,
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
    print(
    f"DEBUG DETAILS TOOL: "
    f"student={student_name}, "
    f"class={course_name}, "
    f"section={section_name}, "
    f"date={date_text}"
)

    return await get_student_details(
        student_name=student_name,
        course_name=course_name,
        section_name=section_name,
        date_text=date_text,
    )


# =========================================================
# CLASS STUDENT LIST TOOL
# =========================================================

@tool
async def get_class_student_list_tool(
    course_name: str,
    section_name: str,
    date_text: str = "today",
) -> dict:
    """
    Given a class and section, return the complete list
    of students in that class.

    Use this tool for questions such as:
    - Give me the list of all students in Class 6 Blue.
    - Show me the student roster for 5 Blue A.
    - List all students in Class Five A.
    """

    return await get_class_student_list(
        course_name=course_name,
        section_name=section_name,
        date_text=date_text,
    )


# =========================================================
# STUDENT ATTENDANCE SUMMARY TOOL
# =========================================================

@tool
async def get_student_attendance_summary_tool(
    student_name: str,
    course_name: str,
    section_name: str,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Given a student, class, section and date range,
    return total school days, present days, absent days,
    tardy days, and attendance percentage.

    Use this tool for questions such as:
    - How many days was Rahib Ahmed present and absent from 1 Sep to 30 Sep?
    - Rahib ki attendance summary from 1 September 2026 to 30 September 2026?
    - Was Rahib absent or late in Class Five Blue A between given dates?
    """

    return await get_student_attendance_summary(
        student_name=student_name,
        course_name=course_name,
        section_name=section_name,
        start_date=start_date,
        end_date=end_date,
    )


# =========================================================
# CLASS ATTENDANCE SUMMARY TOOL
# =========================================================

@tool
async def get_class_attendance_summary_tool(
    course_name: str,
    section_name: str,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Given a class and section, return attendance summary
    for all students in that class across the date range.

    Use this tool for questions such as:
    - Give me the attendance of all Class 6 Blue students from 1 Sep to 30 Sep.
    - Show class attendance summary for 5 Blue A between 1 September 2026 and 30 September 2026.
    - Summarize attendance for all students in Class 5 Blue A.
    """

    return await get_class_attendance_summary(
        course_name=course_name,
        section_name=section_name,
        start_date=start_date,
        end_date=end_date,
    )


# =========================================================
# ALL TOOLS
# =========================================================

tools = [
    get_attendance_tool,
    get_student_attendance_tool,
    get_student_details_tool,
    get_class_student_list_tool,
    get_student_attendance_summary_tool,
    get_class_attendance_summary_tool,
]
