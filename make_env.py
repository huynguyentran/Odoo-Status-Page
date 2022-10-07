#!/usr/bin/env python3
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

file_loader = FileSystemLoader('/opt/odoo/customized_addons/')
env = Environment(loader=file_loader,
                  autoescape=select_autoescape(['html', 'htm', 'xml']))
template = env.get_template('odoo.conf.template')
config = {}
for env in os.environ:
    config[env] = os.environ[env]

# Database
db_info = json.loads(os.environ.get('Postgres_Database'))

config['db_info'] = {}
for info in db_info:
    config['db_info'][info] = db_info[info]


output = template.render(config=config)

with open('/etc/odoo/odoo.conf', 'w') as f:
    f.write(output)
