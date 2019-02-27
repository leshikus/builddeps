#!/usr/bin/python3

import sys, os, subprocess, shutil

pkg = set()
paths =  { 'dir': os.path.join(os.environ['HOME'], 'src/pkgs'),
  'order': 'order.pkg',
  'circ': 'circular.pkg' }
circ = []
order = []
bootstrap = set()

def get_default_log_name(name):
  if '.' in name: name = name.split('.')[0]
  return name + '.log'


def prepare_env():
  basepath, basename = os.path.split(__file__)
  paths['bootstrap'] = os.path.join(basepath, 'bootstrap.pkg')
  paths['log'] = get_default_log_name(basename)

  clean_flag = False
  if len(sys.argv) > 1:
    pos = 1
    while pos < len(sys.argv):
      cur = sys.argv[pos]
      pos += 1
      if cur[0] != '-':
        pkg.add(cur)
        continue

      opt = cur[2:]
      if opt == 'clean':
        clean_flag = True
        continue

      if opt in paths:
        paths[opt] = sys.argv[pos]
        pos += 1
        continue

      print("""Creates an ordered list of packages required to build specified packages
Usage:""", basename, """[OPTION] <package list>
Options:
  --dir DIR         use working directory (default""", paths['dir'] + """)
  --clean           clean working directory first
  --bootstrap FILE  read bootstrap packages from FILE (default""", paths['bootstrap'] + """)
  --order FILE      output build order to FILE (default""", paths['order'] + """)
  --circ FILE       output circular dependenies to FILE (default""", paths['circ'] + """)
  --log  FILE       log warnings to FILE (default""", paths['log'] + ')')
      sys.exit(-1)

  if not pkg:
    print('No packages given, exiting. Use', basename, '--help for help.')
    sys.exit(-1)
    
  wdir = paths['dir']
  if clean_flag:
    print('Removing ' + wdir)
    shutil.rmtree(wdir, ignore_errors = True)

  with open(paths['bootstrap']) as f:
    bootstrap.update(line.strip() for line in f)
  os.makedirs(wdir, exist_ok = True)
  os.chdir(wdir)

  paths['log'] = open(paths['log'], 'w')


def write_log(message):
  print(message)
  paths['log'].write(message + '\n')


def gen_list():
  BUILD_DEPENDS = 'Build-Depends:'
  pkg_queue = list(pkg)
  deps_dict = {}
  while pkg_queue:
    p = pkg_queue.pop()
    if p in deps_dict: continue

    write_log('Get dependecies for ' + p)
    result = subprocess.run(['apt-rdepends', '--build-depends', '--follow=DEPENDS', p], stdout = subprocess.PIPE)

    bd_flag = False
    deps = []
    for d in result.stdout.decode('utf-8').split():
      if bd_flag:
        deps.append(d)
        bd_flag = False
      else: bd_flag = d == BUILD_DEPENDS
      
    for dep in deps:
      if not dep in bootstrap: pkg_queue.append(dep)
          
    deps_dict[p] = deps

  print(deps_dict)

def flush_output():
  paths['log'].close()
  f = open(paths['circ'], 'w')
  f.write('\n'.join(circ))
  f.close()
  f = open(paths['order'], 'w')
  f.write('\n'.join(order))
  f.close()

prepare_env()
gen_list()
flush_output()

