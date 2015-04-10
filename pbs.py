__author__ = 'lposti'

from numpy import linspace, append, meshgrid, reshape
from subprocess import call


class ModelJobs(object):

    def __init__(self, num):

        self.num = int(num)
        self.num_jobs = self.num * self.num
        self.iter = 0

        self.model_type = "Hernquist"
        x = append(linspace(0.2, 1., num=num/2, endpoint=False), linspace(1, 5, num=num/2))
        y = append(linspace(0.2, 1., num=num/2, endpoint=False), linspace(1, 5, num=num/2))

        self.dz, self.dphi = meshgrid(x, y)
        self.dz, self.dphi = reshape(self.dz, self.num_jobs), reshape(self.dphi, self.num_jobs)

        self.input_dir = "inputfiles/"
        self.jobs_dir = "jobfiles/"
        self.basename = ""

    def launch_jobs(self):

        for i in range(self.num_jobs):

            self.print_input_file()
            pbs_script_name = self.print_pbs_script()

            call(["qsub", pbs_script_name])
            self._advance_iter()

    def print_input_file(self):

        dphi, dz, chi = self.dphi[self.iter], self.dz[self.iter], 1.
        name = self._get_basename(dphi, dz, chi)

        f = open(self.input_dir+name+".par", 'w')
        f.write("itermax   5\n")
        f.write("model   "+self.model_type+"\n")
        f.write("outfile   "+name+"\n")
        f.write("h(J):dphi   "+str(dphi)+"\n")
        f.write("h(J):dz   "+str(dz)+"\n")
        f.write("g(J):dphi   "+str(dphi)+"\n")
        f.write("g(J):dz   "+str(dz)+"\n")
        f.write("chi   "+str(chi)+"\n")
        f.write("mass   1.\n")
        f.write("r0   1.\n")
        f.write("q   1.\n")

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
        f.write("#PBS -M lorenzo.posti@gmail.com\n")
        f.write("cd /gpfs/scratch/userexternal/lposti00/fJmodels\n")
        f.write("module load intel/cs-xe-2015--binary\n")
        f.write("module load gsl/1.16--intel--cs-xe-2015--binary\n")
        f.write("./fJmodels "+self.input_dir+self.basename+".par \n")

        return pbs_script_name

    def _get_basename(self, dphi, dz, chi):

        self.basename = self.model_type[0:5] + \
            "_dp" + '{:4.2f}'.format(dphi) + "_dz" + '{:4.2f}'.format(dz) + "_c" + '{:4.2f}'.format(chi)
        return self.basename

    def _advance_iter(self):
        self.iter += 1
        return self.iter