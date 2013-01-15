#!/usr/bin/env python

"""
:copyright: (c) 2013 by Vail Gold.
:license: See LICENSE.txt for details.
"""

import sys, os

def compile_file_from_path(filepath, strict=True, compress=False):
  try:
    ext = filepath.split('/')[-1].split('.')[-1]
  except Exception:
    if strict:
      raise Exception("Could not get extension in " + str(filepath))
    else:
      return
  
  if ext != 'wml':
    if strict:
      raise Exception("Invalid extension (" + str(filepath) + "). Must be .wml.")
    else:
      return
  
  def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
      data = file_object.read(chunk_size)
      if not data:
        break
      yield data
  
  with open(filepath, 'rb') as f:
    for piece in read_in_chunks(f):
      data = piece
  
  from compile import Compiler
  
  html = Compiler(text=data, compress=compress).output
  
  temp = filepath.split('/')
  temp.pop()
  filename = '/'.join(temp) + '/' + filepath.split('/')[-1].split('.')[0] + '.html'
  with open(filename, 'wb') as f:
    f.write(html)

args = sys.argv

if args[0].split('/')[0] == "wieldymarkup":
  args = args[1:]

compress = False
if "-c" in args or "--compress" in args:
  compress = True
  args = [arg for arg in args if arg not in ["-c", "--compress"]]

if "-d" in args:
  d_index = args.index("-d")
  if len(args) < d_index + 1:
    raise Exception("The -d argument must be followed immediately by a directory path in which to compiler .wml files.")
  
  dir_path = str(args[d_index + 1])
  if not os.path.isdir(dir_path):
    raise Exception("Invalid directory path following -d argument.")
    
  if "-r" in args:
    for root, dirs, files in os.walk(dir_path):
      compile_file_from_path(os.path.join(root, name), strict=False, compress=compress)
  else:
    for filepath in os.listdir(dir_path):
      if not os.path.isdir(os.path.join(dir_path, filepath)):
        compile_file_from_path(os.path.join(dir_path, filepath), strict=False, compress=compress)
  
else:
  strict = True
  if "-f" in args or "--force" in args:
    strict = False
    args = [arg for arg in args if arg not in ["-f", "--force"]]
  
  for filepath in args:
    compile_file_from_path(filepath, strict=strict, compress=compress)
  
