#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import OrderedDict
from datetime import date
from dateutil.relativedelta import relativedelta
from jinja2 import Environment, FileSystemLoader
from os.path import abspath, dirname, join
from tempfile import TemporaryDirectory
from shutil import copyfile
from subprocess import run, PIPE
import yaml


# Load YAML dicts ordered
# Thanks http://stackoverflow.com/a/21912744/2729168
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def soft_space(value):
    return value.replace('. ', '.~')


TEMPLATE_DIR = join(abspath(dirname(__file__)), 'templates')
EXTRA_FILES = ['res.cls', 'photo.png']
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR),
                  block_start_string=r'\BLOCK{',
                  block_end_string=r'}',
                  variable_start_string=r'\VAR{',
                  variable_end_string=r'}',
                  comment_start_string=r'\#{',
                  comment_end_string=r'}',
                  line_statement_prefix=r'%%',
                  line_comment_prefix=r'%#')
env.filters['soft_space'] = soft_space

parser = ArgumentParser()
parser.add_argument('--debug', action='store_true')
parser.add_argument('--brief', dest='type', action='store_const', const='brief')
parser.add_argument('--full', dest='type', action='store_const', const='full')
parser.add_argument('--publist', dest='type', action='store_const', const='publist')
parser.add_argument('--out', '-o', type=str, default='resume.pdf')
args = parser.parse_args()
args.type = args.type or 'full'

context = {
    'name': 'Eivind Fonn',
    'author': 'E. Fonn',
    'age': relativedelta(date.today(), date(1984, 11, 2)).years,
}

if args.type != 'publist':
    context.update({
        'address': 'Høgreina 394, NO-7079 Flatåsen',
        'phone': '+47 41 44 98 89',
        'email': 'evfonn@gmail.com'
    })

with open('data.yaml', 'r') as f:
    context.update(ordered_load(f))


blocks = [
    'personalia',
    'education',
    'experience',
    'skills',
    'awards',
    'assorted',
    'trust',
    'social',
    'projects',
    'publications',
    'presentations',
    'posters',
]

if args.type == 'brief':
    for b in ['projects', 'publications', 'presentations', 'posters']:
        blocks.remove(b)
elif args.type == 'publist':
    blocks = ['projects', 'publications', 'presentations', 'posters']
    context['name'] = 'Projects and publication list'


with TemporaryDirectory() as tmp:
    template = env.get_template('resume')
    with open(join(tmp, 'resume.tex'), 'w') as f:
        f.write(template.render(blocks=blocks, **context))

    for fn in EXTRA_FILES:
        copyfile(fn, join(tmp, fn))

    additional_args = {}
    if not args.debug:
        additional_args['stdout'] = PIPE
        additional_args['stderr'] = PIPE

    run(['latexmk', '-pdf', 'resume.tex'], cwd=tmp, **additional_args)

    copyfile(join(tmp, 'resume.pdf'), args.out)
