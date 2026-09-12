"""Use the established grader with this version's qualified fixture."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('adapter_grade', HERE.parent / 'grade.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)
grader.HERE = HERE

if __name__ == '__main__':
    raise SystemExit(grader.main())
