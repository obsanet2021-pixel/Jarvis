import json
d = json.loads(open('graphify-out/.graphify_detect.json').read())
print('Files:')
for cat, files in d.get('files', {}).items():
    print(f'  {cat}: {len(files)}')
    for f in files:
        print(f'    {f}')
print(f'Total: {d["total_files"]}')