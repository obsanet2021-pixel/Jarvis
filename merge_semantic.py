import json
import re
from pathlib import Path

# Read and fix chunk 0
with open('graphify-out/.graphify_chunk_00.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the file_path backslashes by replacing with raw string style
# or just escape them properly
content = content.replace(r'C:\Users\Free user\Jarvis\platform-tools-extracted\platform-tools\NOTICE.txt', r'C:\\Users\\Free user\\Jarvis\\platform-tools-extracted\\platform-tools\\NOTICE.txt')

# Parse the JSON
chunk0 = json.loads(content)
kg = chunk0.get('knowledge_graph_fragment', chunk0)

# Convert chunk0 format to standard format
nodes0 = []
edges0 = []

# Add license nodes
for lic in kg.get('licenses', []):
    nodes0.append({
        'id': f'license_{lic["name"].lower().replace(" ", "_").replace("/", "_")}',
        'label': lic['name'],
        'file_type': 'license',
        'source_file': r'C:\\Users\\Free user\\Jarvis\\platform-tools-extracted\\platform-tools\\NOTICE.txt'
    })

# Add copyright holder nodes
for holder in kg.get('copyright_holders', []):
    nodes0.append({
        'id': f'org_{holder["name"].lower().replace(" ", "_").replace(".", "_").replace(",", "").replace("&", "and")}',
        'label': holder['name'],
        'file_type': 'organization',
        'source_file': r'C:\\Users\\Free user\\Jarvis\\platform-tools-extracted\\platform-tools\\NOTICE.txt'
    })

# Add component nodes
for comp in kg.get('components', []):
    nodes0.append({
        'id': f'component_{comp["name"].lower().replace(" ", "_").replace("/", "_").replace("-", "_").replace("{", "").replace("}", "").replace(".", "_")}',
        'label': comp['name'],
        'file_type': 'software',
        'source_file': r'C:\\Users\\Free user\\Jarvis\\platform-tools-extracted\\platform-tools\\NOTICE.txt'
    })

print(f'Chunk 0: {len(nodes0)} nodes')

# Process chunk 1
chunk1 = json.loads(Path('graphify-out/.graphify_chunk_01.json').read_text(encoding='utf-8'))
all_nodes = nodes0 + chunk1.get('nodes', [])
all_edges = chunk1.get('edges', [])
all_hyperedges = []

print(f'Chunk 1: {len(chunk1.get("nodes", []))} nodes, {len(chunk1.get("edges", []))} edges')

# Process chunk 2
chunk2 = json.loads(Path('graphify-out/.graphify_chunk_02.json').read_text(encoding='utf-8'))
all_nodes.extend(chunk2.get('nodes', []))
all_edges.extend(chunk2.get('edges', []))
all_hyperedges.extend(chunk2.get('hyperedges', []))
print(f'Chunk 2: {len(chunk2.get("nodes", []))} nodes, {len(chunk2.get("edges", []))} edges, {len(chunk2.get("hyperedges", []))} hyperedges')

# Process chunk 3
chunk3 = json.loads(Path('graphify-out/.graphify_chunk_03.json').read_text(encoding='utf-8'))
entities = chunk3.get('entities', {})
relationships = chunk3.get('relationships', {})

nodes3 = []
for entity_id, entity_data in entities.items():
    nodes3.append({
        'id': entity_id.lower().replace(' ', '_'),
        'label': entity_id,
        'file_type': 'document',
        'source_file': 'multiple_files_chunk_3',
        'source_location': None
    })

edges3 = []
for rel_id, rel_data in relationships.items():
    edges3.append({
        'source': rel_data['source'].lower().replace(' ', '_'),
        'target': rel_data['target'].lower().replace(' ', '_'),
        'relation': rel_data['relationship_type'].lower(),
        'confidence': 'EXTRACTED',
        'confidence_score': rel_data.get('strength', 0.8),
        'source_file': 'multiple_files_chunk_3',
        'source_location': None,
        'weight': 1.0
    })

all_nodes.extend(nodes3)
all_edges.extend(edges3)
print(f'Chunk 3: {len(nodes3)} nodes, {len(edges3)} edges')

# Deduplicate nodes by id
seen = set()
deduped_nodes = []
for n in all_nodes:
    if n['id'] not in seen:
        seen.add(n['id'])
        deduped_nodes.append(n)

# Ensure all nodes have required fields
for n in deduped_nodes:
    n.setdefault('file_type', 'document')
    n.setdefault('source_file', 'unknown')
    n.setdefault('source_location', None)
    n.setdefault('source_url', None)
    n.setdefault('captured_at', None)
    n.setdefault('author', None)
    n.setdefault('contributor', None)

# Ensure all edges have required fields
for e in all_edges:
    e.setdefault('confidence', 'EXTRACTED')
    e.setdefault('confidence_score', 1.0)
    e.setdefault('source_location', None)
    e.setdefault('weight', 1.0)

Path('graphify-out/.graphify_semantic.json').write_text(json.dumps({
    'nodes': deduped_nodes,
    'edges': all_edges,
    'hyperedges': all_hyperedges,
    'input_tokens': 0,
    'output_tokens': 0,
}, indent=2, ensure_ascii=False), encoding='utf-8')

print(f'Merged semantic: {len(deduped_nodes)} nodes, {len(all_edges)} edges, {len(all_hyperedges)} hyperedges')