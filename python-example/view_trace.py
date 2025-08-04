#!/usr/bin/env python3
"""
MCP Trace Viewer - Analyzes and displays MCP trace logs
"""
import json
import sys
import os
from datetime import datetime
from collections import defaultdict

def analyze_trace(filename):
    """Analyze MCP trace file and display summary"""
    print(f"=== MCP Trace Analysis ===")
    print(f"File: {filename}")
    print()
    
    requests = []
    responses = []
    errors = []
    methods = defaultdict(int)
    
    with open(filename, 'r') as f:
        for line_no, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())
                level = entry.get('level', '')
                
                if level == 'TRANSPORT_IN':
                    data = entry.get('data', {})
                    raw = data.get('raw', '')
                    if raw:
                        try:
                            msg = json.loads(raw.strip())
                            if 'method' in msg:
                                methods[msg['method']] += 1
                                requests.append({
                                    'line': line_no,
                                    'time': entry.get('timestamp'),
                                    'method': msg['method'],
                                    'id': msg.get('id'),
                                    'params': msg.get('params', {})
                                })
                        except:
                            pass
                
                elif level == 'TRANSPORT_OUT':
                    data = entry.get('data', {})
                    if data.get('has_error'):
                        errors.append({
                            'line': line_no,
                            'time': entry.get('timestamp'),
                            'id': data.get('id')
                        })
                    else:
                        responses.append({
                            'line': line_no,
                            'time': entry.get('timestamp'),
                            'id': data.get('id')
                        })
                
                elif level == 'ERROR':
                    errors.append({
                        'line': line_no,
                        'time': entry.get('timestamp'),
                        'message': entry.get('message'),
                        'data': entry.get('data')
                    })
                    
            except json.JSONDecodeError:
                print(f"Warning: Invalid JSON at line {line_no}")
    
    # Display summary
    print("📊 Summary:")
    print(f"  Total requests: {len(requests)}")
    print(f"  Total responses: {len(responses)}")
    print(f"  Total errors: {len([e for e in errors if 'message' in e])}")
    print()
    
    print("📨 Methods called:")
    for method, count in sorted(methods.items()):
        print(f"  {method}: {count}")
    print()
    
    print("📋 Request sequence:")
    for req in requests:
        print(f"  Line {req['line']}: {req['method']} (id: {req['id']})")
        if req['method'] == 'initialize':
            params = req.get('params', {})
            client = params.get('clientInfo', {})
            if client:
                print(f"    Client: {client.get('name')} v{client.get('version')}")
            caps = params.get('capabilities', {})
            if caps:
                print(f"    Capabilities: {', '.join(caps.keys())}")
    print()
    
    if errors:
        print("❌ Errors found:")
        for err in errors:
            if 'message' in err:
                print(f"  Line {err['line']}: {err.get('message')}")
                if err.get('data'):
                    print(f"    Details: {err['data']}")
    else:
        print("✅ No errors found")
    
    # Check for potential issues
    print("\n🔍 Potential issues:")
    issues = []
    
    # Check if all requests got responses
    req_ids = {r['id'] for r in requests if r['id'] is not None}
    resp_ids = {r['id'] for r in responses}
    missing = req_ids - resp_ids
    if missing:
        issues.append(f"Requests without responses: {missing}")
    
    # Check for unknown methods
    known_methods = {'initialize', 'initialized', 'tools/list', 'resources/list', 
                     'prompts/list', 'tools/call', 'ping'}
    unknown = set(methods.keys()) - known_methods - {''}
    if unknown:
        issues.append(f"Unknown methods: {unknown}")
    
    if issues:
        for issue in issues:
            print(f"  ⚠️  {issue}")
    else:
        print("  None detected")

if __name__ == "__main__":
    # Find latest trace file if not specified
    if len(sys.argv) > 1:
        trace_file = sys.argv[1]
    else:
        # Find latest in /tmp
        import glob
        files = glob.glob('/tmp/mcp_trace_*.log')
        if not files:
            print("No trace files found in /tmp/")
            sys.exit(1)
        trace_file = max(files, key=os.path.getmtime)
    
    if os.path.exists(trace_file):
        analyze_trace(trace_file)
    else:
        print(f"Error: File not found: {trace_file}")
        sys.exit(1)