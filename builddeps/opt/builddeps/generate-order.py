#!/usr/bin/python3

import sys, os, subprocess, shutil, heapq

pkg = set()
params =  { 'dir': os.path.join(os.environ['HOME'], 'src/pkgs'),
  'circular': 'circular.pkg',
  'script': '/tmp/build.sh',
  'level': '1' }
deps_dict = {}
circular = []
order = []

def get_default_log_name(name):
  if '.' in name: name = name.split('.')[0]
  return name + '.log'


def prepare_env():
  basepath, basename = os.path.split(__file__)
  params['log'] = get_default_log_name(basename)
  params['pkgbuild'] = 'pkgbuild.sh'

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

      print("""Creates an ordered list of packages required to build specified packages. The packages which break circular dependencies are built first.
Usage:""", basename, """[OPTION] <package list>
Options (default value in brackets):
  --dir DIR         use DIR as a working directory (""" + params['dir'] + """)
  --clean           clean working directory first
  --script FILE     write a build script to FILE (""" + params['script'] + """)
  --pkgbuild SCRIPT use SCRIPT to build a package (""" + params['pkgscript'] + """)
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
      for dep in deps: heapq.heappush(pkg_queue, (l + 1, dep))
          
    deps_dict[p] = deps
    #write_log(p + '->' + str(deps))


def gen_lists():
  ref_count = {}

  empty_nodes = set()
  pkgs = set()
  for k, v in deps_dict.items():
    for d in v:
      if not d in deps_dict: empty_nodes.add(d)

  for d in empty_nodes: deps_dict[d] = []
  for k in deps_dict:
    pkgs.add(k)
    ref_count[k] = 0

  for k, v in deps_dict.items():
    for d in v: ref_count[d] += 1

  while pkgs:

    while True:
      zero_ref_counts = set()
      for k in pkgs:
        if ref_count[k] == 0:
          zero_ref_counts.add(k)
          order.append(k)
          for d in deps_dict[k]: ref_count[d] -= 1

      if zero_ref_counts:
        pkgs -= zero_ref_counts
      else: break

    if not pkgs: break

    # all ref_count[k] > 0 - each node has a parent reference
    parent = {}
    for k in pkgs:
      for v in deps_dict[k]: parent[v] = k

    # walk along the graph until we come to the point
    # which was already visited
    visited = set()
    while not k in visited:
      visited.add(k)
      k = parent[k]

    # place package which breaks a loop to the front
    circular.append(k)
    for v in deps_dict[k]: ref_count[v] -= 1
    pkgs.remove(k)
  
  write_log('circular: ' + str(circular))
  write_log('order: ' + str(order))


def flush_output():
  params['log'].close()
  with open(params['circular'], 'w') as f:
    f.write('\n'.join(circular))
  
  with open(params['script'], 'w') as f:
    f.write("""#!/bin/sh

pkgbuild() {
  sh """ + params['pkgbuild'] + """ $1 && echo PKGBUILD_OK $1 || echo PKGBUILD_ERROR $1
}

""")
    for p in circular: f.write('pkgbuild ' + p + '\n')
    for i in range(len(order)-1, -1, -1): f.write('pkgbuild ' + order[i] + '\n')
    f.write('echo PKGBUILD_COMPLETE\n')


prepare_env()
get_deps()
gen_lists()
flush_output()

