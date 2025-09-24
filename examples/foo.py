import sys
import os
print("cwd:", os.getcwd())
for p in sys.path:
    print(p)

import smartcity
print("import ok :", smartcity.__file__)