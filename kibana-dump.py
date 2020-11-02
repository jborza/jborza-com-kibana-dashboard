#!/usr/bin/python3
import requests
import ndjson
import sys
import os
import json
import string

if(len(sys.argv) < 2):
    print("Usage: export.py http://KIBANA_URL:PORT")
    exit(1)

server = sys.argv[1]

output_directory = 'data'
api_url = server+'/api'
export_url = api_url+'/saved_objects/_export'

print(f'Exporting objects from Kibana instance at {server}')

def get_title_attribute(object):
    if object['type'] in ['url','config']:
        return object['id']
    elif object['type'] in ['canvas-workpad','canvas-element']:
        return object['attributes']['name']
    else:
        return object['attributes']['title']

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def sanitize_filename(filename):
    # https://stackoverflow.com/a/295146
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars)

def export_item(type, item_title, item):
    directory = os.path.join(output_directory, type)
    create_directory_if_not_exists(directory)
    item_name = sanitize_filename(item_title+'.json')
    file_name = os.path.join(directory, item_name)
    print(f'  dumping {file_name}')
    with open(file_name, 'w') as output_file:
        output_file.write(json.dumps(item, indent=2))

def export_item_kibana_7(item):
    type = item['type']
    title = get_title_attribute(item)
    export_item(type, title, item)

def dump_type(object_type):
    print(f'Dumping objects of type {object_type}')
    payload = {'type': object_type, 'excludeExportDetails': True}
    r = requests.post(export_url,
                  json=payload,
                  headers={'kbn-xsrf': 'true'})
    data = ndjson.loads(r.text)
    for item in data:
        export_item_kibana_7(item)

def dump_all_kibana_7():
    types = ['index-pattern', 'search', 'query', 'url', 'visualization', 'dashboard']
    for t in types:
        dump_type(t)

dump_all_kibana_7()