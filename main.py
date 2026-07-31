from dualingo_logic import run_lesson
import traceback

try:
    print("Starting Duolingo lesson...")
    run_lesson("cookies/yorai.json", None)
    print("Lesson completed!")
except Exception as e:
    print(f"Error in main.py: {e}")
    traceback.print_exc()