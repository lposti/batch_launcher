__author__ = 'lposti'

from numpy import linspace, logspace, append, meshgrid, reshape, ones
from subprocess import call


class ModelJobs(object):

    def __init__(self, num, mode="simple Hernquist"):

        self.num = int(num)
        self.num_jobs = self.num * self.num
        self.iter = 0

        if (mode == "simple Hernquist" or mode == "simple hernquist" or mode == "simple Hernq" or
                    mode == "simple hernq"):
            self.model_type, self.dhz, self.dhphi, self.dgz, self.dgphi, self.chi, self.A, self.B\
                = self._mode_hernquist_h_eq_g_chi1(num)
        elif (mode == "A,B only" or mode == "A B only" or mode == "A, B only" or mode == "A and B only" or
                      mode == "A & B only"):
            self.model_type, self.dhz, self.dhphi, self.dgz, self.dgphi, self.chi, self.A, self.B\
                = self._mode_a_b_only(num)
        elif mode == "A hJ" or mode == "A and hJ" or mode == "A & hJ":
            self.model_type, self.dhz, self.dhphi, self.dgz, self.dgphi, self.chi, self.A, self.B\
                = self._mode_a_h(num)
        elif mode == "mock catalog" or mode == 'catalog' or mode == 'mock':
            self.model_type, self.dhz, self.dhphi, self.dgz, self.dgphi, self.chi, self.A, self.B\
                = self._mode_catalog(num)
        else:
            raise ValueError("Set 'mode' properly!")

        self.input_dir = "inputfiles/"
        self.jobs_dir = "jobfiles/"
        self.basename = ""

    def _mode_hernquist_h_eq_g_chi1(self, num):

        model_type = "Hernquist"
        max_delta = 10.
        x = append(linspace(1. / max_delta, 1., num=num / 2, endpoint=False), linspace(1, max_delta, num=num / 2))
        y = append(linspace(1. / max_delta, 1., num=num / 2, endpoint=False), linspace(1, 1. / max_delta, num=num / 2))

        chi = ones(self.num_jobs, dtype=float)
        dz, dphi = meshgrid(x, y)
        dz, dphi = reshape(dz, self.num_jobs), reshape(dphi, self.num_jobs)

        return model_type, dz, dphi, dz, dphi, chi, 'none', 'none'

    def _mode_a_b_only(self, num):

        model_type = "null"

        dhphi, dhz = 0.5 * ones(self.num_jobs, dtype=float), 0.5 * ones(self.num_jobs, dtype=float)
        dgphi, dgz = ones(self.num_jobs, dtype=float), ones(self.num_jobs, dtype=float)
        chi = ones(self.num_jobs, dtype=float)

        x = linspace(0.7, 2.5, num=num)
        y = linspace(2.5, 6.5, num=num)
        a, b = meshgrid(x, y)
        a, b = reshape(a, self.num_jobs), reshape(b, self.num_jobs)

        return model_type, dhz, dhphi, dgz, dgphi, chi, a, b

    def _mode_a_h(self, num):

        model_type = "null"

        dgphi, dgz = ones(self.num_jobs, dtype=float), ones(self.num_jobs, dtype=float)
        chi = ones(self.num_jobs, dtype=float)
        b = 5. * ones(self.num_jobs, dtype=float)

        x = linspace(0.7, 2.5, num=num)
        y = append(linspace(0.2, 1., num=num / 2, endpoint=False), linspace(1, 5, num=num / 2))
        a, dh = meshgrid(x, y)
        a, dh = reshape(a, self.num_jobs), reshape(dh, self.num_jobs)

        return model_type, dh, dh, dgz, dgphi, chi, a, b

    def _mode_catalog(self, num):

        model_type = "Hernquist"
        x = logspace(-2., 1., num=num)
        y = logspace(-2., 1., num=num)

        chi = ones(self.num_jobs, dtype=float)
        dhz, dhphi = 0.5 * ones(self.num_jobs, dtype=float), 0.5 * ones(self.num_jobs, dtype=float)

        dgz, dgphi = meshgrid(x, y)
        dgz, dgphi = reshape(dgz, self.num_jobs), reshape(dgphi, self.num_jobs)

        return model_type, dhz, dhphi, dgz, dgphi, chi, 'none', 'none'

    def launch_jobs(self):

        for i in range(self.num_jobs):

            self.print_input_file()
            pbs_script_name = self.print_pbs_script()

            call(["qsub", pbs_script_name])
            self._advance_iter()

    def test_launch_jobs(self):

        for i in range(self.num_jobs):

            self.print_input_file()
            pbs_script_name = self.print_pbs_script()

            call(["echo", pbs_script_name])
            self._advance_iter()

    def print_input_file(self):

        dhphi, dhz, dgphi, dgz, chi = self.dhphi[self.iter], self.dhz[self.iter], \
            self.dgphi[self.iter], self.dgz[self.iter], \
            self.chi[self.iter]
        name = self._get_basename(dhphi, dhz, dgphi, dgz, chi)

        f = open(self.input_dir+name+".par", 'w')
        f.write("itermax    5\n")
        if self.model_type is "null":
            f.write("# model      "+self.model_type+"\n")
            f.write("A            "+str(self.A[self.iter])+"\n")
            f.write("B            "+str(self.B[self.iter])+"\n")
        else:
            f.write("model      "+self.model_type+"\n")
        f.write("outfile    "+name+"\n")
        f.write("h(J):dphi  "+str(dhphi)+"\n")
        f.write("h(J):dz    "+str(dhz)+"\n")
        f.write("g(J):dphi  "+str(dgphi)+"\n")
        f.write("g(J):dz    "+str(dgz)+"\n")
        f.write("chi        "+str(chi)+"\n")
        f.write("mass       1.\n")
        f.write("r0         1.\n")
        f.write("q          1.\n")

    def print_pbs_script(self):

        pbs_script_name = self.jobs_dir+self.basename+".pbs"
        f = open(pbs_script_name, 'w')
        f.write("#!/bin/bash\n")
        f.write("#PBS -A IscrC_CALIFAfJ\n")
        f.write("#PBS -l walltime=1:00:00\n")
        f.write("#PBS -l select=1:ncpus=16:mem=1GB\n")
        f.write("#PBS -N "+self.basename+"\n")
        f.write("#PBS -o "+self.basename+".out\n")
        f.write("#PBS -e "+self.basename+".err\n")
        f.write("#PBS -m a\n")
        f.write("#PBS -M lorenzo.posti@gmail.com\n\n")
        f.write("cd /gpfs/work/IscrC_CALIFAfJ/fJmodels/\n")
        f.write("module load intel/cs-xe-2015--binary\n")
        f.write("module load gsl/1.16--intel--cs-xe-2015--binary\n\n")
        f.write("./fJmodels "+self.input_dir+self.basename+".par \n")

        return pbs_script_name

    def _get_basename(self, dhphi, dhz, dgphi, dgz, chi):

        if self.model_type == "null":
            mod_name = "A" + '{:4.2f}'.format(self.A[self.iter]) + "_B" + '{:4.2f}'.format(self.B[self.iter])
        else:
            mod_name = self.model_type[0:5]
        self.basename = mod_name + \
            "_dp" + '{:4.2f}'.format(dhphi) + "_" + '{:4.2f}'.format(dgphi) + "_dz" + '{:4.2f}'.format(dhz) + "_" + \
            '{:4.2f}'.format(dgz) + "_c" + '{:4.2f}'.format(chi)
        return self.basename

    def _advance_iter(self):
        self.iter += 1
        return self.iter