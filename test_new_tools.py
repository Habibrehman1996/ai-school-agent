import unittest

from tools import tools


class TestNewTools(unittest.TestCase):
    def test_required_tool_names_present(self):
        tool_names = {getattr(tool, "name", "") for tool in tools}

        self.assertIn("get_class_student_list_tool", tool_names)
        self.assertIn("get_student_attendance_summary_tool", tool_names)
        self.assertIn("get_class_attendance_summary_tool", tool_names)


if __name__ == "__main__":
    unittest.main()
