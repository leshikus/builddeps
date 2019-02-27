#!/usr/bin/python3

import sys, os, subprocess, shutil, heapq

pkg = set()
params =  { 'dir': os.path.join(os.environ['HOME'], 'src/pkgs'),
  'circular': 'circular.pkg',
  'script': '/tmp/build.sh',
  'level': '1' }
circular = []
deps_dict = {}
order = []
bootstrap = set()

def get_default_log_name(name):
  if '.' in name: name = name.split('.')[0]
  return name + '.log'


def prepare_env():
  basepath, basename = os.path.split(__file__)
  params['bootstrap'] = os.path.join(basepath, 'bootstrap.pkg')
  params['log'] = get_default_log_name(basename)

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

      if opt in params:
        params[opt] = sys.argv[pos]
        pos += 1
        continue

      print("""Creates an ordered list of packages required to build specified packages
Usage:""", basename, """[OPTION] <package list>
Options (default value in brackets):
  --dir DIR         use DIR as a working directory (""" + params['dir'] + """)
  --clean           clean working directory first
  --bootstrap FILE  read bootstrap packages from FILE (""" + params['bootstrap'] + """)
  --circular FILE   write circularular dependenies to FILE (""" + params['circular'] + """)
  --script FILE     write a build script to FILE (""" + params['script'] + """)
  --log FILE        log warnings to FILE (""" + params['log'] + """)
  --level n         recursion level for dependencies (""" + params['level'] + ')')
      sys.exit(-1)

  if not pkg:
    print('No packages given, exiting. Use', basename, '--help for help.')
    sys.exit(-1)
    
  wdir = params['dir']
  if clean_flag:
    print('Removing ' + wdir)
    shutil.rmtree(wdir, ignore_errors = True)

  with open(params['bootstrap']) as f:
    bootstrap.update(line.strip() for line in f)
  os.makedirs(wdir, exist_ok = True)
  os.chdir(wdir)

  params['log'] = open(params['log'], 'w')
  params['level'] = int(params['level'])


def write_log(message):
  print(message)
  params['log'].write(message + '\n')
  params['log'].flush()


def get_deps():
  BUILD_DEPENDS = 'Build-Depends:'
  pkg_queue = [(0, p) for p in pkg]
  while pkg_queue:
    l, p = heapq.heappop(pkg_queue)
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
    
    if l < params['level']:
      for dep in deps:
        if not dep in bootstrap: heapq.heappush(pkg_queue, (l + 1, dep))
          
    deps_dict[p] = deps
    #write_log(p + '->' + str(deps))


def gen_lists():
  ref_count = {}

  for k, v in deps_dict.items():
    for d in v:
      r = ref_count.get(d)
      ref_count[d] = 1 if r is None else r + 1

  for k, v in deps_dict.items():
    if not k in ref_count:
      order.append(k)
      for d in v: ref_count[d] -= 1
  
  is_changed = True
  while is_changed:
    is_changed = False
    for k, v in ref_count.items():
      if v == 0:
        order.append(k)
        r = deps_dict.get(k)
        if r is not None:
          for d in r: ref_count[d] -= 1
        is_changed = True
        del ref_count[k]
        break

  
  circ_refs = [(v, k) for k, v in ref_count.items()]
  circ_refs.sort(reverse = True)
  for v, k in circ_refs: circular.append(k)

  write_log('circular: ' + str(circular))
  write_log('order: ' + str(order))


def flush_output():
  params['log'].close()
  with open(params['circular'], 'w') as f:
    f.write('\n'.join(circular))
  
  with open(params['script'], 'w') as f:
    f.write("""#!/bin/sh

build() (
  mkdir $1
  cd $1
  apt-get source $1
  apt-get build-dep $1
  cd $1/debian
  debuild -b -uc -us
  cd ../..
  dpkg -i *.deb
)

cd `dirname "$0"`
mkdir -p build
cd build

""")
    for p in circular: f.write('build ' + p + '\n')
    for i in range(len(order)-1, -1, -1): f.write('build ' + order[i] + '\n')
    f.write('echo Comlete\n')


prepare_env()
get_deps()
gen_lists()
flush_output()

