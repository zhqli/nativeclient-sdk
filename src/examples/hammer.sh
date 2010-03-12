#!/bin/bash
#
# Copyright 2010 Native Client SDK Authors. All Rights Reserved.
#
# Perform build of the examples by invoking hammer.

HOST=$(uname)
case $HOST in
  Darwin)
    NJOBS="$(sysctl -n hw.logicalcpu)"
    # Most of our Macs build systems are quad-core.
    NSCALE=4
  ;;
  Linux)
    NJOBS="$(grep processor /proc/cpuinfo | wc -l)"
    # Most of our Linux build systems are dual-core.
    NSCALE=2
  ;;
  *)
    NJOBS="1"
  ;;
esac

basedir=$(dirname $0)
export SCONS_DIR=$basedir/../tools/scons/scons-local
exec /bin/bash $basedir/../tools/hammer/hammer.sh -j $NJOBS $*