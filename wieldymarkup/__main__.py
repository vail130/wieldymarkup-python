#!/usr/bin/env python

"""
:copyright: (c) 2013 by Vail Gold.
:license: See LICENSE.txt for details.
"""

import sys

args = sys.argv[1:]

compress = False
if "-c" in args:
  compress = True
  args = [arg for arg in args if arg != "-c"]

for filepath in args:
  try:
    ext = filepath.split('/')[-1].split('.')[-1]
  except Exception:
    print "Invalid argument."
    exit()
  
  if ext != 'txt':
    print "Invalid argument."
    exit()
  
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
  
  html = Compiler(data, compress=compress).output
  
  temp = filepath.split('/')
  temp.pop()
  filename = '/'.join(temp) + '/' + filepath.split('/')[-1].split('.')[0] + '.html'
  with open(filename, 'wb') as f:
    f.write(html)
