import asyncio

from edap_client import get_student_attendance


async def main():

    result = await get_student_attendance(
        student_name="RAHIB",
        course_name="CLASS FIVE",
        section_name="BLUE-A",
        start_date="1 September 2026",
        end_date="24 September 2026"
    )

    print("\n========== STUDENT ATTENDANCE ==========\n")
    print(result)
    print("\n=========================================\n")


if __name__ == "__main__":
    asyncio.run(main())