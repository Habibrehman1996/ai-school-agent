import asyncio
from datetime import date

from langchain.agents import create_agent
from tools import tools


# =========================================================
# TODAY
# =========================================================

TODAY = date.today().strftime("%d %B %Y")


# =========================================================
# AI SCHOOL AGENT
# =========================================================

agent = create_agent(
    model="google_genai:gemini-flash-lite-latest",

    tools=tools,

    system_prompt=f"""
You are an AI School Operations Assistant connected
to the school's EDAP system.

Today's date is {TODAY}.

Your job is to retrieve school data using EDAP tools
and give the user a short, accurate answer.

IMPORTANT RULES:

- Never invent data.
- For actual school information, always use the
  appropriate EDAP tool.
- Only report information returned by the tool.
- Never expose tokens, passwords, API keys,
  authentication headers or internal URLs.
- Keep answers concise.

DATE:
- "today", "aaj", "aj" = today's date.
- Current date = {TODAY}.
- Specific dates must be passed exactly as the
  requested date.
- For a month such as "September", use the appropriate
  date range for that month when the tool requires it.

CLASS / SECTION:
Examples:
- Class Five Blue A = CLASS FIVE / BLUE-A
- 5 Blue A = CLASS FIVE / BLUE-A
- Class Five A Blue = CLASS FIVE / BLUE-A

CLASS ATTENDANCE:
Use the class attendance tool for whole-class questions.

Return when available:
- Total
- Present
- Absent
- Late/Tardy
- Attendance percentage

STUDENT ATTENDANCE:
Use the student attendance tool for questions about
one student's attendance.

Examples:
- Rahib September mein kitne din present tha?
- Rahib September mein kitne din absent tha?
- Rahib ki attendance percentage kya hai?

STUDENT DETAILS:
Use the student details tool for personal school
record questions.

Examples:
- Rahib ke father ka naam?
- Rahib ka father number?
- Rahib ki mother ka naam?
- Rahib ka GR number?
- Rahib ka student number?
- Rahib ki details?

PARTIAL STUDENT NAMES:
Partial names are allowed.

For example:
"Rahib" can match "RAHIB AHMED".

If the tool reports multiple matching students,
do not choose randomly. Ask the user to clarify.

ATTENDANCE STATUS:
EDAP may return:
- Present
- Absent
- Leave
- Late

Do not change the status.

If EDAP says Late, report Late.

HOLIDAYS:
If EDAP reports a holiday, do not count that day
as Present, Absent, Leave or Late.

STUDENT ATTENDANCE:
Use the attendance percentage returned/calculated
by the tool.

Never create your own attendance numbers.

If the tool cannot find the requested information,
tell the user clearly.

PRIVACY:
Only provide the information requested by the user.
Do not provide unrelated student information.

MOST IMPORTANT:
Use the correct tool.
Do not guess.
Do not invent.
"""
)


# =========================================================
# EXTRACT FINAL TEXT
# =========================================================

def get_final_text(content):
    """
    Gemini/LangChain newer versions can return content
    as either a string or a list of content blocks.
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for block in content:

            if isinstance(block, dict):

                if block.get("type") == "text":
                    text_parts.append(
                        block.get("text", "")
                    )

                elif "text" in block:
                    text_parts.append(
                        str(block["text"])
                    )

        return "\n".join(
            part for part in text_parts if part
        )

    return str(content)


# =========================================================
# CHAT LOOP
# =========================================================

async def main():

    print()
    print("=" * 55)
    print("          AI SCHOOL OPERATIONS AGENT")
    print("=" * 55)
    print()

    print("EDAP connected tools:")
    print("1. Class Attendance")
    print("2. Student Attendance")
    print("3. Student Details")

    print()
    print("Type 'exit' to quit.")
    print()

    while True:

        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":

            print()
            print("Agent closed.")
            break

        try:

            print("AI is processing...")

            response = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                },
                config={
                    "recursion_limit": 6
                }
            )

            final_message = response["messages"][-1]

            answer = get_final_text(
                final_message.content
            )

            print()
            print("Agent:")
            print(answer)
            print()

        except Exception as e:

            print()
            print("Error:")
            print(str(e))
            print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())