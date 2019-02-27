#!/usr/bin/python3

import sys, os, subprocess, shutil

pkg = set()
paths =  { 'dir': os.environ['HOME'] + '/src/debian',
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
  pkg_new = pkg
  order = list(pkg_new)
  while pkg_new:
    write_log('Installing ' + str(pkg_new))
    subprocess.run(['apt-get', 'source'] + list(pkg_new))

    pkg_processed = set()
    for filename in os.listdir('.'):
      if filename[-4:] != '.dsc': continue
     
      for p in pkg_new:
        if p == filename[:len(p)] and filename[len(p)] == '_':
          pkg_processed.add(p)

          write_log('Processing ' + filename)
          deps = []
          with open(filename, 'r') as f:
            for line in f:
              if line[:L_BUILD_DEPENDS] == BUILD_DEPENDS: break
              
            print(line[L_BUILD_DEPENDS:])

    if pkg_new != pkg_processed:
      pkg_diff = pkg_new - pkg_processed
      write_log('Warning: cannot find ' + next(iter(pkg_diff)) + '_*.dsc')
      print('pkg_new - pkg_processed =', pkg_diff)

    pkg_new = set()


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

