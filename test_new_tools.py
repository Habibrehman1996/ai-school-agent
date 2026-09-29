import asyncio
import unittest

from app import _run_in_fresh_loop
from tools import tools


class TestNewTools(unittest.TestCase):
    def test_required_tool_names_present(self):
        tool_names = {getattr(tool, "name", "") for tool in tools}

        self.assertIn("get_class_student_list_tool", tool_names)
        self.assertIn("get_student_attendance_summary_tool", tool_names)
        self.assertIn("get_class_attendance_summary_tool", tool_names)

    def test_five_consecutive_calls_do_not_reuse_closed_loop(self):
        async def fake_async_call(value):
            await asyncio.sleep(0.01)
            return value

        for index in range(5):
            result = _run_in_fresh_loop(lambda idx=index: fake_async_call(f"msg-{idx}"))
            self.assertEqual(result, f"msg-{index}")


if __name__ == "__main__":
    unittest.main()
