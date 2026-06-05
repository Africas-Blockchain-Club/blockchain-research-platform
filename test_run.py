import sys, os
sys.path.append(os.path.join(os.getcwd(), 'tools'))
from report_generator import generate_report

try:
    print('Testing generate_report for ADR...')
    path = generate_report('ADR')
    print('Generated Path:', path)
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            print('--- REPORT START ---')
            print(f.read()[:500])
except Exception as e:
    import traceback
    traceback.print_exc()
