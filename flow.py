import runpy
import sys
import os
import subprocess
import so_api
import traceback

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def display_questions(qs, show_body=True, max_chars=100):
    dump = []
    for q in qs:
        dump.append("{} - \"{}\"".format(q["question_id"], q["title"]))
        if show_body:
            dump.append("\t : {}".format(q["body"]))
    for d in dump:
        print(d[:max_chars])

module_name = os.path.splitext(sys.argv[1])[0]
try:
    runpy.run_module(module_name, {}, "__main__")
except Exception as e:
    print("caught exception:", e)
    traceback.print_exc()
# pyargs = sys.argv[1:]
# result = subprocess.run(["python"] + pyargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# if result.returncode:
#     stderr = result.stderr.decode("utf-8")
#     stdout = result.stdout.decode("utf-8")
#     eprint("Python interpreter error: \n{}".format(stderr))
#     print("Stdout hints: \n{}".format(stdout))

api = so_api.SOApi()
print("Asking: ", "Python, {}".format(err))
res = api.query_questions("Python, {}".format(err))

print("I have found these questions:")
display_questions(res)
