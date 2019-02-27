#!/usr/bin/python3

import sys, os, subprocess, shutil

pkg = set()
paths =  { 'dir': os.environ['HOME'] + '/src/pkgs',
  'order': 'order.pkg',
  'circ': 'circular.pkg' }
circ = []
order = []


def get_default_log_name(name):
  if '.' in name: name = name.split('.')[0]
  return name + '.log'


def prepare_env():
  basename = os.path.basename(__file__)
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
  --dir DIR     use working directory (default""", paths['dir'] + """)
  --clean       clean working directory first
  --order FILE  output build order to FILE (default""", paths['order'] + """)
  --circ FILE   output circular dependenies to FILE (default""", paths['circ'] + """)
  --log  FILE   log warnings to FILE (default""", paths['log'] + ')')
      sys.exit(-1)

  if not pkg:
    print('No packages given, exiting. Use', basename, '--help for help.')
    sys.exit(-1)
    
  wdir = paths['dir']
  if clean_flag:
    print('Removing ' + wdir)
    shutil.rmtree(wdir, ignore_errors = True)
  os.makedirs(wdir, exist_ok = True)
  os.chdir(wdir)

  paths['log'] = open(paths['log'], 'w')


def write_log(message):
  print(message)
  paths['log'].write(message + '\n')


def gen_list():
  BUILD_DEPENDS = 'Build-Depends: '
  L_BUILD_DEPENDS = len(BUILD_DEPENDS)
  pkg_queue = list(pkg)
  deps_dict = {}
  while pkg_queue:
    p = pkg_queue.pop()
    if p in deps_dict: continue

    try:
      os.mkdir(p)
      os.chdir(p)
      write_log('Installing ' + p)
      subprocess.run(['apt-get', 'source', p])
    except OSError:
      write_log('Reusing ' + p)
      os.chdir(p)

    deps = None

    for filename in os.listdir('.'):
      if filename[-4:] != '.dsc': continue
   
      write_log('Processing ' + filename)
      with open(filename, 'r') as f:
        for line in f:
          if line[:L_BUILD_DEPENDS] == BUILD_DEPENDS: break
              
        deps = line[L_BUILD_DEPENDS:].split(',')
        for line in f:
          if line[0] != ' ': break
          else: deps.extend(line[1:].split(','))

    if deps is None:
      write_log('Cannot find .dsc file in ' + p)
      sys.exit(-1)

    for i in range(len(deps)):
      dep = deps[i].strip()
      if ' ' in dep: dep = dep.split()[0]
      if dep[-4:] == ':any': dep = dep[:-4]
      deps[i] = dep
          
    deps_dict[p] = deps
    pkg_queue.extend(deps)   
    os.chdir('..')

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

