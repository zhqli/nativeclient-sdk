#!/usr/bin/python
# Copyright (c) 2011 The Native Client Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Create the base (auto)updater for the Native Client SDK"""

import py_compile
import optparse
import os
import shutil
import sys
import tarfile

from build_tools.sdk_tools import update_manifest
from build_tools.sdk_tools import sdk_update

NACL_SDK = 'nacl_sdk'


def MakeSdkTools(nacl_sdk_filename, sdk_tools_filename):
  '''Make the nacl_sdk and sdk_tools tarballs

  The nacl_sdk package contains these things:

  nacl_sdk/
    nacl(.bat)  - The main entry point for updating the SDK
    sdk_tools/
      sdk_update.py  - Performs the work in checking for updates
    python/
      python.exe  - (optional) python executable, shipped with Windows
      ... - other python files and directories
    sdk_cache/
      naclsdk_manifest.json  - manifest file with information about sdk_tools

  Args:
    nacl_sdk_filename: name of tarball that the user directly downloads
    sdk_tools_filename: name of tarball that has the sdk_tools directory
  '''
  base_dir = os.path.abspath(os.path.dirname(__file__))
  temp_dir = os.path.join(base_dir, NACL_SDK)
  if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
  os.mkdir(temp_dir)
  for dir in ['sdk_tools', 'sdk_cache']:
    os.mkdir(os.path.join(temp_dir, dir))
  nacl_frontend = 'nacl.bat' if sys.platform in ['cygwin', 'win32'] else 'nacl'
  shutil.copy2(os.path.join(base_dir, nacl_frontend), temp_dir)
  shutil.copy2(os.path.join(base_dir, 'sdk_tools', 'sdk_update.py'),
               os.path.join(temp_dir, 'sdk_tools'))
  py_compile.compile(os.path.join(temp_dir, 'sdk_tools', 'sdk_update.py'))
  update_manifest_options = [
       '--bundle-revision=%s' % sdk_update.MINOR_REV,
       '--bundle-version=%s' % sdk_update.MAJOR_REV,
       '--description=Native Client SDK Tools, revision %s.%s' % (
           sdk_update.MAJOR_REV, sdk_update.MINOR_REV),
       '--bundle-name=sdk_tools',
       '--recommended=yes',
       '--stability=stable',
       '--manifest-version=%s' % sdk_update.SDKManifest().MANIFEST_VERSION,
       os.path.join(temp_dir, 'sdk_cache', 'naclsdk_manifest.json')]
  if 0 != update_manifest.main(update_manifest_options):
    raise Exception('update_manifest terminated abnormally.')
  def WriteTarFile(outname, in_dir, tar_dir):
    tar_file = None
    try:
      tar_file = tarfile.open(outname, 'w:gz')
      tar_file.add(in_dir, tar_dir)
    finally:
      if tar_file:
        tar_file.close()
  WriteTarFile(nacl_sdk_filename, temp_dir, NACL_SDK)
  WriteTarFile(sdk_tools_filename, os.path.join(temp_dir, 'sdk_tools'), '')
  shutil.rmtree(temp_dir)


def main(argv):
  parser = optparse.OptionParser()
  parser.add_option(
      '-n', '--nacl-sdk', dest='nacl_sdk', default='nacl_sdk.tgz',
      help='name of the nacl_sdk tarball')
  parser.add_option(
      '-s', '--sdk-tools', dest='sdk_tools', default='sdk_tools.tgz',
      help='name of the sdk_tools tarball')
  (options, args) = parser.parse_args(argv)
  MakeSdkTools(options.nacl_sdk, options.sdk_tools)
  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
