import os
from datetime import datetime, timedelta

import httpx
from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

EDAP_BASE_URL = "https://api.edap.com.pk"
EDAP_TOKEN = os.getenv("EDAP_TOKEN")

CAMPUS_ID = 8865


# =========================================================
# COMMON HEADERS
# =========================================================

def get_headers():
    return {
        "Authorization": f"Bearer {EDAP_TOKEN}",
        "Accept": "application/json",
    }


# =========================================================
# GET COURSES + SECTIONS
# =========================================================

async def get_courses_and_sections():
    """
    EDAP se campus ki classes aur sections retrieve karta hai.
    """

    url = (
        f"{EDAP_BASE_URL}"
        f"/portal/api/hdr_SMCourse/v2/CourseList/{CAMPUS_ID}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=get_headers(),
            timeout=30,
        )

    response.raise_for_status()

    result = response.json()

    courses = []

    for course_type in result.get("Data", []):

        for course in course_type.get("CourseList", []):

            course_data = {
                "course_id": course.get("CourseId"),
                "course": course.get("Course"),
                "sections": [],
            }

            for section in course.get("Sections", []):

                course_data["sections"].append({
                    "section_id": section.get("SectionId"),
                    "section": section.get("Section"),
                })

            courses.append(course_data)

    return courses


# =========================================================
# FIND COURSE + SECTION
# =========================================================

def normalize_text(value):
    """
    Text ko comparison ke liye normalize karta hai.
    """

    if not value:
        return ""

    return (
        " ".join(str(value).strip().upper().split())
        .replace(" - ", "-")
        .replace(" ", "")
    )


def find_course_section(
    courses: list,
    course_name: str,
    section_name: str,
):
    """
    Example:

    CLASS FIVE + BLUE-A
    """

    target_course = normalize_text(course_name)
    target_section = normalize_text(section_name)

    for course in courses:

        if normalize_text(course["course"]) == target_course:

            for section in course["sections"]:

                if normalize_text(section["section"]) == target_section:

                    return (
                        course["course_id"],
                        section["section_id"],
                    )

    return None


# =========================================================
# FORMAT DATE
# =========================================================

def format_edap_date(date_text: str) -> str:
    """
    User ki date ko EDAP format mein convert karta hai.

    Examples:

    today
    aaj
    aj

    24 September 2026
    24 Sep 2026
    24-09-2026
    24/09/2026
    """

    if not date_text:
        raise ValueError("Date provide nahi ki gayi.")

    text = date_text.strip().lower()

    # Today's date
    if text in ["today", "aaj", "aj"]:

        return datetime.now().strftime("%d-%b-%Y")

    formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d %B, %Y",
        "%d %b, %Y",
    ]

    for fmt in formats:

        try:

            date_obj = datetime.strptime(
                date_text.strip(),
                fmt,
            )

            return date_obj.strftime("%d-%b-%Y")

        except ValueError:
            continue

    raise ValueError(
        f"Date samajh nahi aayi: {date_text}"
    )


# =========================================================
# GET RAW ATTENDANCE
# =========================================================

async def get_attendance(
    course_id: int,
    section_id: int,
    date: str,
):
    """
    EDAP se specific class + section ki
    specific date ki attendance retrieve karta hai.
    """

    url = (
        f"{EDAP_BASE_URL}"
        f"/portal/api/SMStuAttendance/v2/"
        f"AttendanceActivitySectionWise/"
        f"{CAMPUS_ID}/"
        f"{course_id}/"
        f"{section_id}/"
        f"{date}"
    )

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            headers=get_headers(),
            timeout=30,
        )

    response.raise_for_status()

    return response.json()


# =========================================================
# PARSE DAILY ATTENDANCE
# =========================================================

def parse_attendance(data: dict) -> dict:

    attendance_data = data.get(
        "Data",
        {},
    )

    result = {

        "class": attendance_data.get(
            "coursestxt"
        ),

        "section": attendance_data.get(
            "sectionstxt"
        ),

        "total": attendance_data.get(
            "total",
            0,
        ),

        "holiday": attendance_data.get(
            "isholiday",
            False,
        ),

        "present": 0,

        "absent": 0,

        "tardy": 0,

        "attendance_percentage": None,
    }

    # Holiday
    if result["holiday"]:

        return result

    result["present"] = attendance_data.get(
        "activitypresentcount",
        0,
    )

    result["absent"] = attendance_data.get(
        "activityabsentcount",
        0,
    )

    result["tardy"] = attendance_data.get(
        "activitytardycount",
        0,
    )

    result["attendance_percentage"] = (
        attendance_data.get(
            "activitypresent"
        )
    )

    return result


# =========================================================
# DAILY CLASS ATTENDANCE
# =========================================================

async def get_class_attendance(
    course_name: str,
    section_name: str,
    date_text: str,
):
    """
    Specific class ki specific date ki attendance.
    """

    courses = await get_courses_and_sections()

    result = find_course_section(
        courses,
        course_name,
        section_name,
    )

    if result is None:

        return {
            "success": False,
            "message": (
                f"Class '{course_name}' "
                f"ya section '{section_name}' nahi mila."
            ),
        }

    course_id, section_id = result

    try:

        edap_date = format_edap_date(
            date_text
        )

    except ValueError as e:

        return {
            "success": False,
            "message": str(e),
        }

    data = await get_attendance(
        course_id=course_id,
        section_id=section_id,
        date=edap_date,
    )

    attendance = parse_attendance(data)

    return {
        "success": True,
        "date": edap_date,
        **attendance,
    }


# =========================================================
# FIND STUDENT CANDIDATES
# =========================================================

def find_student_candidates(
    activities: list,
    target_name: str,
):
    """
    AttendanceActivity mein student ko search karta hai.

    Exact match ko priority milti hai.

    Example:

    Target:
        RAHIB

    EDAP:
        RAHIB AHMED

    Match ho jayega.
    """

    target = " ".join(
        target_name.strip().upper().split()
    )

    exact_matches = []
    partial_matches = []

    for activity in activities:

        status = activity.get(
            "stxt",
            ""
        )

        students = activity.get(
            "AttendanceDetail",
            []
        )

        for student in students:

            raw_name = student.get(
                "name",
                ""
            )

            name = " ".join(
                raw_name.strip().upper().split()
            )

            if not name:
                continue

            student_info = {
                "student_id": student.get("Id"),
                "student_no": student.get("studentno"),
                "gr_no": student.get("grno"),
                "name": raw_name.strip(),
                "status": status,
            }

            # Exact
            if name == target:

                exact_matches.append(
                    student_info
                )

            # Partial
            elif target in name:

                partial_matches.append(
                    student_info
                )

    if exact_matches:

        # Remove duplicates
        unique = {}

        for student in exact_matches:

            key = (
                student["student_id"],
                student["name"],
            )

            unique[key] = student

        return list(unique.values())

    unique = {}

    for student in partial_matches:

        key = (
            student["student_id"],
            student["name"],
        )

        unique[key] = student

    return list(unique.values())


# =========================================================
# FIND STUDENT IN A DATE
# =========================================================

async def find_student_on_date(
    course_id: int,
    section_id: int,
    date_text: str,
    student_name: str,
):
    """
    Ek specific date par student search karta hai.
    """

    data = await get_attendance(
        course_id=course_id,
        section_id=section_id,
        date=date_text,
    )

    attendance_data = data.get(
        "Data",
        {},
    )

    if attendance_data.get(
        "isholiday"
    ):

        return {
            "holiday": True,
            "students": [],
        }

    activities = attendance_data.get(
        "AttendanceActivity",
        []
    )

    students = find_student_candidates(
        activities,
        student_name,
    )

    return {
        "holiday": False,
        "students": students,
    }


# =========================================================
# STUDENT ATTENDANCE
# =========================================================

async def get_student_attendance(
    student_name: str,
    course_name: str,
    section_name: str,
    start_date: str,
    end_date: str,
):
    """
    Student ki date-range attendance.

    Example:

    Rahib
    CLASS FIVE
    BLUE-A
    1 September 2026
    24 September 2026
    """

    courses = await get_courses_and_sections()

    result = find_course_section(
        courses,
        course_name,
        section_name,
    )

    if result is None:

        return {
            "success": False,
            "message": (
                f"Class '{course_name}' "
                f"ya section '{section_name}' nahi mila."
            ),
        }

    course_id, section_id = result

    # -----------------------------------------------------
    # Parse dates
    # -----------------------------------------------------

    try:

        start = datetime.strptime(
            start_date.strip(),
            "%d %B %Y",
        )

        end = datetime.strptime(
            end_date.strip(),
            "%d %B %Y",
        )

    except ValueError:

        return {
            "success": False,
            "message": (
                "Date format example: "
                "1 September 2026"
            ),
        }

    if start > end:

        return {
            "success": False,
            "message": (
                "Start date end date se "
                "pehle honi chahiye."
            ),
        }

    # -----------------------------------------------------
    # First find the student's actual full name
    # -----------------------------------------------------

    resolved_student = None

    current_date = start

    while current_date <= end:

        date_text = current_date.strftime(
            "%d-%b-%Y"
        )

        try:

            data = await get_attendance(
                course_id=course_id,
                section_id=section_id,
                date=date_text,
            )

            attendance_data = data.get(
                "Data",
                {}
            )

            if attendance_data.get(
                "isholiday"
            ):

                current_date += timedelta(
                    days=1
                )

                continue

            activities = attendance_data.get(
                "AttendanceActivity",
                []
            )

            candidates = find_student_candidates(
                activities,
                student_name,
            )

            if len(candidates) == 1:

                resolved_student = candidates[0][
                    "name"
                ]

                break

            elif len(candidates) > 1:

                return {
                    "success": False,
                    "ambiguous": True,
                    "message": (
                        f"'{student_name}' naam ke "
                        f"multiple students mile hain."
                    ),
                    "students": [
                        {
                            "name": x["name"],
                            "student_no": x["student_no"],
                            "gr_no": x["gr_no"],
                        }
                        for x in candidates
                    ],
                }

        except Exception as e:

            print(
                f"Student lookup error "
                f"on {date_text}: {e}"
            )

        current_date += timedelta(
            days=1
        )

    if resolved_student is None:

        return {
            "success": False,
            "message": (
                f"Student '{student_name}' "
                f"class {course_name} "
                f"{section_name} mein nahi mila."
            ),
        }

    # -----------------------------------------------------
    # Get attendance for resolved student
    # -----------------------------------------------------

    records = []

    current_date = start

    while current_date <= end:

        date_text = current_date.strftime(
            "%d-%b-%Y"
        )

        try:

            data = await get_attendance(
                course_id=course_id,
                section_id=section_id,
                date=date_text,
            )

            attendance_data = data.get(
                "Data",
                {}
            )

            # Holiday skip
            if attendance_data.get(
                "isholiday"
            ):

                current_date += timedelta(
                    days=1
                )

                continue

            activities = attendance_data.get(
                "AttendanceActivity",
                []
            )

            student_found = False

            for activity in activities:

                status = activity.get(
                    "stxt",
                    ""
                )

                students = activity.get(
                    "AttendanceDetail",
                    []
                )

                for student in students:

                    raw_name = student.get(
                        "name",
                        ""
                    )

                    normalized_name = " ".join(
                        raw_name.strip().upper().split()
                    )

                    target_name = " ".join(
                        resolved_student.strip().upper().split()
                    )

                    if normalized_name == target_name:

                        records.append({
                            "date": current_date.strftime(
                                "%d-%b-%Y"
                            ),
                            "status": status,
                        })

                        student_found = True

                        break

                if student_found:
                    break

        except Exception as e:

            print(
                f"Attendance error "
                f"on {date_text}: {e}"
            )

        current_date += timedelta(
            days=1
        )

    # -----------------------------------------------------
    # Calculate summary
    # -----------------------------------------------------

    present = 0
    absent = 0
    leave = 0
    late = 0

    for record in records:

        status = record[
            "status"
        ].strip().lower()

        if status == "present":

            present += 1

        elif status == "absent":

            absent += 1

        elif status in [
            "leave",
            "on leave",
        ]:

            leave += 1

        elif status in [
            "late",
            "tardy",
        ]:

            late += 1

    total_recorded = len(records)

    attendance_percentage = None

    if total_recorded > 0:

        attendance_percentage = (
            present / total_recorded
        ) * 100

    return {

        "success": True,

        "student": resolved_student,

        "class": course_name,

        "section": section_name,

        "start_date": start_date,

        "end_date": end_date,

        "school_days_recorded": total_recorded,

        "present": present,

        "absent": absent,

        "leave": leave,

        "late": late,

        "attendance_percentage": (
            round(
                attendance_percentage,
                2
            )
            if attendance_percentage is not None
            else None
        ),

        "records": records,
    }


# =========================================================
# STUDENT DETAILS
# =========================================================

async def get_student_details(
    student_name: str,
    course_name: str,
    section_name: str,
    date_text: str = "today",
):
    """
    Student ki basic details retrieve karta hai.

    Includes:
        Name
        Student No
        GR No
        Father Name
        Father Contact
        Mother Name
        Mother Contact
        Attendance status
        Attendance time
    """

    courses = await get_courses_and_sections()

    result = find_course_section(
        courses,
        course_name,
        section_name,
    )

    if result is None:

        return {
            "success": False,
            "message": (
                f"Class '{course_name}' "
                f"ya section '{section_name}' nahi mila."
            ),
        }

    course_id, section_id = result

    try:

        edap_date = format_edap_date(
            date_text
        )

    except ValueError as e:

        return {
            "success": False,
            "message": str(e),
        }

    data = await get_attendance(
        course_id=course_id,
        section_id=section_id,
        date=edap_date,
    )

    attendance_data = data.get(
        "Data",
        {}
    )

    if attendance_data.get(
        "isholiday"
    ):

        return {
            "success": False,
            "holiday": True,
            "message": (
                f"{edap_date} ko school holiday hai."
            ),
        }

    activities = attendance_data.get(
        "AttendanceActivity",
        []
    )

    candidates = []

    for activity in activities:

        status = activity.get(
            "stxt",
            ""
        )

        students = activity.get(
            "AttendanceDetail",
            []
        )

        for student in students:

            raw_name = student.get(
                "name",
                ""
            )

            name = " ".join(
                raw_name.strip().upper().split()
            )

            target = " ".join(
                student_name.strip().upper().split()
            )

            if name == target or target in name:

                student_data = {
                    "name": raw_name.strip(),

                    "student_no": student.get(
                        "studentno"
                    ),

                    "gr_no": student.get(
                        "grno"
                    ),

                    "father_name": student.get(
                        "fathername"
                    ),

                    "father_contact": student.get(
                        "fatherContactNo"
                    ),

                    "mother_name": student.get(
                        "motherName"
                    ),

                    "mother_contact": student.get(
                        "motherContactNo"
                    ),

                    "attendance_status": status,

                    "attendance_time": student.get(
                        "attendancetime"
                    ),

                    "reason": student.get(
                        "reasonstxt"
                    ),
                }

                candidates.append(
                    student_data
                )

    # -----------------------------------------------------
    # No student
    # -----------------------------------------------------

    if not candidates:

        return {
            "success": False,
            "message": (
                f"Student '{student_name}' "
                f"class {course_name} "
                f"{section_name} mein nahi mila."
            ),
        }

    # -----------------------------------------------------
    # Multiple students
    # -----------------------------------------------------

    unique_students = {}

    for student in candidates:

        key = (
            student["student_no"],
            student["name"],
        )

        unique_students[key] = student

    candidates = list(
        unique_students.values()
    )

    if len(candidates) > 1:

        return {
            "success": False,
            "ambiguous": True,
            "message": (
                f"'{student_name}' se "
                f"multiple students mile hain."
            ),
            "students": [
                {
                    "name": x["name"],
                    "student_no": x["student_no"],
                    "gr_no": x["gr_no"],
                }
                for x in candidates
            ],
        }

    return {
        "success": True,
        "date": edap_date,
        "class": course_name,
        "section": section_name,
        **candidates[0],
    }