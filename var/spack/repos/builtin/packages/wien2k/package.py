##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
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
#     spack install wien2k
#
# You can edit this file again by typing:
#
#     spack edit wien2k
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
from spack import *
import fileinput
import os
import re
import shutil
import sys
import tempfile
from distutils.version import LooseVersion
import pexpect  #FIXME importing pexpect before installing?

class Wien2k(Package):
    """ WIEN2k allows to perform electronic structure calculations of solids using density functional theory (DFT). It is based on the full-potential (linearized) augmented plane-wave ((L)APW) + local orbitals (lo) method, among the most accurate schemes for band structure calculations."""

    homepage = "http://www.wien2k.at"
    url      = "file:///home/hassanah/Downloads/WIEN2k_17.1.tar.gz"
    version('17.1', '6b2f01914d6b3a88add8966c20e11ed5')

    # WIEN2k does not provide these libraries, but allows you to use them
    variant('mpi', default=True, description='Enable MPI parallelism')

    depends_on('python')
    depends_on('perl')
    depends_on('tcsh')
    depends_on('py-numpy')
    depends_on('mpi', when='+mpi')
    depends_on('lapack')
    depends_on('fftw', when='+fftw')
    depends_on('blas')
    depends_on('py-pexpect')

    def install(self, spec, prefix):
        """Unpack WIEN2k sources using gunzip and provided expand_lapw script."""

        sh.gunzip("*.gz")
        child = pexpect.spawn ("./expand_lapw")
        child.expect ("continue (y/n)")
        child.sendline ("y")
        child.sendline ("bye")

        """Configure WIEN2k build by patching siteconfig_lapw script and running it."""

        self.cfgscript = "siteconfig_lapw"

        # patch config file first
      #  comp_answer = None
       # if self.compiler == %intel #----------------------------------------------------------------->
       #     if LooseVersion(get_software_version("icc")) >= LooseVersion("2011"):
       #         comp_answer = 'I'  # Linux (Intel ifort 12.0 compiler + mkl )
       #     else:
       #         comp_answer = "K1"  # Linux (Intel ifort 11.1 compiler + mkl )

       # elif self.compiler == %gcc #------------------------------------------------------------------->
        comp_answer = 'V'  # Linux (gfortran compiler + gotolib)

        # libraries
        rlibs = "%s %s" % (os.getenv('LIBLAPACK_MT'), self.compiler.get_flag('openmp'))
        rplibs = [os.getenv('LIBSCALAPACK_MT'), os.getenv('LIBLAPACK_MT')]
        fftwver = get_software_version('FFTW')
        if fftwver:
            suff = ''
            if LooseVersion(fftwver) >= LooseVersion("3"):
                suff = '3'
            rplibs.insert(0, "-lfftw%(suff)s_mpi -lfftw%(suff)s" % {'suff': suff})
        else:
            rplibs.append(os.getenv('LIBFFT'))

        rplibs = ' '.join(rplibs)

        d = {
             'FC': '%s %s' % (os.getenv('F90'), os.getenv('FFLAGS')),
             'MPF': "%s %s" % (os.getenv('MPIF90'), os.getenv('FFLAGS')),
             'CC': os.getenv('CC'),
             'LDFLAGS': '$(FOPT) %s ' % os.getenv('LDFLAGS'),
             'R_LIBS': rlibs,  # libraries for 'real' (not 'complex') binary
             'RP_LIBS' : rplibs,  # libraries for 'real' parallel binary
             'MPIRUN': '',
            }

        for line in fileinput.input(self.cfgscript, inplace=1, backup='.orig'):
            # set config parameters
            for (k,v) in d.items():
                regexp = re.compile('^([a-z0-9]+):%s:.*' % k)
                res = regexp.search(line)
                if res:
                    # we need to exclude the lines with 'current', otherwise we break the script
                    if not res.group(1) == "current":
                        line = regexp.sub('\\1:%s:%s' % (k, v), line)
            # avoid exit code > 0 at end of configuration
            line = re.sub('(\s+)exit 1', '\\1exit 0', line)
            sys.stdout.write(line)

        # set correct compilers
        env.setvar('bin', os.getcwd())

        dc = {
            'COMPILERC': os.getenv('CC'),
            'COMPILER': os.getenv('F90'),
            'COMPILERP': os.getenv('MPIF90'),
        }

        for (k, v) in dc.items():
            write_file(k, v)

        # configure with patched configure script
        self.log.debug('%s part I (configure)' % self.cfgscript)
##FIXME
        os.system("./%s" % self.cfgscript)
        child = pexpect("Press RETURN to continue:")
        child.sendline('')     
        child.expect('Your compiler:' )
        child.sendline('')
        child.expect('Hit Enter to continue:')
        child.sendline('')
        child.expect('Remote shell (default is ssh) =:')
        child.sendline('')
        chid.expect('and you need to know details about your installed  mpi ..) (y/n)')
        child.sendline('y')
        child.expect('Q to quit Selection:')
        child.sendline('Q')
        child.expect('A Compile all programs (suggested) Q Quit Selection:') 
        child.sendline('Q')
        child.expect(' Please enter the full path of the perl program: ')
        child.sendline('')
        child.expect('continue or stop (c/s)') 
        child.send('c')
        child.expect('(like taskset -c). Enter N / your_specific_command:')
        child.sendline('N')
        
        if LooseVersion(self.version) >= LooseVersion("13"):
            fftw_root = get_software_root('FFTW')
            if fftw_root:
                fftw_maj = get_software_version('FFTW').split('.')[0]
                fftw_spec = 'FFTW%s' % fftw_maj
            else:
                raise EasyBuildError("Required FFTW dependency is missing")
            qanda.update({
                 '(not updated) Selection:': comp_answer,
                 'Shared Memory Architecture? (y/N):': 'N',
                 'Set MPI_REMOTE to  0 / 1:': '0',
                 'You need to KNOW details about your installed  MPI and FFTW ) (y/n)': 'y',
                 'Please specify whether you want to use FFTW3 (default) or FFTW2  (FFTW3 / FFTW2):' : fftw_spec,
                 'Please specify the ROOT-path of your FFTW installation (like /opt/fftw3):' : fftw_root,
                 'is this correct? enter Y (default) or n:' : 'Y',
            })
        else:
            qanda.update({
                 'compiler) Selection:': comp_answer,
                 'Shared Memory Architecture? (y/n):': 'n',
                 'If you are using mpi2 set MPI_REMOTE to 0  Set MPI_REMOTE to 0 / 1:': '0',
                 'Do you have MPI and Scalapack installed and intend to run ' \
                    'finegrained parallel? (This is usefull only for BIG cases ' \
                    '(50 atoms and more / unit cell) and you need to know details ' \
                    'about your installed  mpi and fftw ) (y/n)': 'y',
            })

        no_qa = [
            'You have the following mkl libraries in %s :' % os.getenv('MKLROOT'),
            "%s[ \t]*.*" % os.getenv('MPIF90'),
            "%s[ \t]*.*" % os.getenv('F90'),
            "%s[ \t]*.*" % os.getenv('CC'),
            ".*SRC_.*",
            "Please enter the full path of the perl program:",
        ]

        std_qa = {
            r'S\s+Save and Quit[\s\n]+To change an item select option.[\s\n]+Selection:': 'S',
            'Recommended setting for parallel f90 compiler: .* Current selection: Your compiler:': os.getenv('MPIF90'),
        }

        run_cmd_qa(cmd, qanda, no_qa=no_qa, std_qa=std_qa, log_all=True, simple=True)
##FIXME
        # post-configure patches
        parallel_options = {}
        parallel_options_fp = os.path.join(self.cfg['start_dir'], 'parallel_options')

        if self.cfg['wien_mpirun']:
            parallel_options.update({'WIEN_MPIRUN': self.cfg['wien_mpirun']})

        if self.cfg['taskset'] is None:
            self.cfg['taskset'] = 'no'
        parallel_options.update({'TASKSET': self.cfg['taskset']})

        for opt in ['use_remote', 'mpi_remote', 'wien_granularity']:
            parallel_options.update({opt.upper(): int(self.cfg[opt])})

        write_file(parallel_options_fp, '\n'.join(['setenv %s "%s"' % tup for tup in parallel_options.items()]))

        if self.cfg['remote']:
            if self.cfg['remote'] == 'pbsssh':
                extratxt = '\n'.join([
                    '',
                    "set remote = pbsssh",
                    "setenv PBSSSHENV 'LD_LIBRARY_PATH PATH'",
                    '',
                ])
                write_file(parallel_options_fp, extratxt, append=True)
            else:
                raise EasyBuildError("Don't know how to handle remote %s", self.cfg['remote'])

        self.log.debug("Patched file %s: %s", parallel_options_fp, read_file(parallel_options_fp))

    def build_step(self):
        """Build WIEN2k by running siteconfig_lapw script again."""

        self.log.debug('%s part II (build_step)' % self.cfgscript)
##FIXME
        cmd = "./%s" % self.cfgscript

        qanda = {
                 'L Perl path (if not in /usr/bin/perl) Q Quit Selection:': 'R',
                 'A Compile all programs S Select program Q Quit Selection:': 'A',
                 'Press RETURN to continue': '\nQ',  # also answer on first qanda pattern with 'Q' to quit
                 ' Please enter the full path of the perl program: ':'',
                }
        no_qa = [
                 "%s[ \t]*.*" % os.getenv('MPIF90'),
                 "%s[ \t]*.*" % os.getenv('F90'),
                 "%s[ \t]*.*" % os.getenv('CC'),
                 "mv[ \t]*.*",
                 ".*SRC_.*",
                 ".*: warning .*",
                 ".*Stop.",
                 "Compile time errors (if any) were:",
                 "Please enter the full path of the perl program:",
                ]

        self.log.debug("no_qa for %s: %s" % (cmd, no_qa))
        run_cmd_qa(cmd, qanda, no_qa=no_qa, log_all=True, simple=True)
##FIXME

    def test_step(self):
        """Run WIEN2k test benchmarks. """

        def run_wien2k_test(cmd_arg):
            """Run a WPS command, and check for success."""
##FIXME
            cmd = "x_lapw lapw1 %s" % cmd_arg
            (out, _) = run_cmd(cmd, log_all=True, simple=False)

            re_success = re.compile("LAPW1\s+END")
            if not re_success.search(out):
                raise EasyBuildError("Test '%s' in %s failed (pattern '%s' not found)?",
                                     cmd, os.getcwd(), re_success.pattern)
            else:
                self.log.info("Test '%s' seems to have run successfully: %s" % (cmd, out))

    def install_step(self):
        """Fix broken symlinks after build/installation."""
        # fix broken symlink
        os.remove(os.path.join(self.installdir, "SRC_w2web", "htdocs", "usersguide"))
        os.symlink(os.path.join(self.installdir, "SRC_usersguide_html"),
                   os.path.join(self.installdir, "SRC_w2web","htdocs", "usersguide"))

