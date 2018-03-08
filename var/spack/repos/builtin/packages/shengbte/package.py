##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install shengbte
#
# You can edit this file again by typing:
#
#     spack edit shengbte
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
from spack import *
from os import *

class Shengbte(Package):
    """ShengBTE is a software package for solving the Boltzmann Transport Equation for phonons."""

    homepage = "http://www.shengbte.org/"
    url      = "http://www.shengbte.org/downloads/ShengBTE-v1.1.1-8a63749.tar.bz2"

    version('1.1.1', '5d5ad00322ed6451c0ba7fe6e32966a8')

    depends_on('mpi%intel')
    depends_on('mkl%intel')
    depends_on('py-spglib%intel')

    def setup_environment(self, spack_env, run_env):

        run_env.prepend_path('PATH', self.spec.prefix.bin)
        run_env.prepend_path('PATH', self.spec['mpi'].prefix.bin)
        run_env.prepend_path('LIBRARY_PATH', self.spec['mpi'].prefix.lib)
        run_env.prepend_path('LD_LIBRARY_PATH', self.spec['mpi'].prefix.lib)
        run_env.prepend_path('PKG_CONFIG_PATH', join_path(self.spec['mpi'].prefix.lib, 'pkgconfig'))
        run_env.prepend_path('CPATH', self.spec['mpi'].prefix.include)

    def install(self, spec, prefix):
        chdir("Src")
        f=open("arch.make","w")
        f.write("export FFLAGS=-traceback -debug -O2 -static_intel\nexport LDFLAGS=-L$(PY_SPGLIB_ROOT)/lib -lsymspg\nexport MPIFC=mpiifort\n")
        f.write("MKL=$(MKLROOT)/lib/intel64/libmkl_lapack95_lp64.a -Wl,--start-group       \
$(MKLROOT)/lib/intel64/libmkl_intel_lp64.a                                \
 $(MKLROOT)/lib/intel64/libmkl_sequential.a                               \
 $(MKLROOT)/lib/intel64/libmkl_core.a -Wl,--end-group -lpthread -lm\nexport LAPACK=$(MKL)\nexport LIBS=$(LAPACK)")
        f.close()
        make()
        make('install')

    def test_installation(self)
        chdir("")
