import pydicom, re, glob
import itertools as it
from pydicom.data import get_testdata_files
import os, sys, optparse

def help():
    print ''' 
    =======================================================================================================================
    Usage:
    
    python extractDicomMetadata.py <scan_directory>
    
    A scan_directory must be provided.
    
    For more information, run:

    python extractDicomMetadata.py -h

    or

    python extractDicomMetadata.py --help
    =======================================================================================================================
    '''
    sys.exit(1)

def parse_options(values):
    p = optparse.OptionParser()
   # p.add_option("-p", action = "store", dest = "pheno_file")
   # p.add_option("--phenos", action = "store", dest = "pheno_file")
   # p.set_defaults(pheno_file = '/exports/igmm/eddie/haley-lab/Common/UKB/ukb27263.tsv',
   #     out_file = 'extracted_ukbb_phenotypes.tsv', translation_file = '/exports/igmm/eddie/haley-lab/Common/UKB/ukb27263_fields.tsv')
    return p.parse_args()

def main():
    print sys.argv
    if len(sys.argv) == 1: help()
    opts, args = parse_options(sys.argv)
    scan_dir = args[0]
    #set the scan directory
    os.chdir('/exports/igmm/eddie/haley-lab/bailey/ukbb/ukbbDexa/dxa_processing_scripts/%s' % scan_dir)
    #Create a container of all the relevant files
    folder = glob.glob('*.dcm')
    with open('./ukbb_metadata_covariates.tsv', 'w+') as outfile:
        outfile.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % ('iid', 'centre', 'bg_colour', 'sex', 'age', 'height', 'weight', 'ethnicity'))
        for f in folder:
            try:
                ds = pydicom.dcmread('%s' % f)
                iid = f.rsplit('/')[0]
                centre = ds.InstitutionalDepartmentName
                try:
                    bg = ds.pixel_array[0][0]
                except AttributeError:
                    bg = "?"
                sex = ds.PatientSex
                age = int(ds.PatientAge.rstrip('Y'))
                height = float(ds.PatientSize)
                weight = int(ds.PatientWeight)
                ethnicity = ds.EthnicGroup
                #print iid, sex 
                outfile.write('%s\t%s\t%s\t%s\t%d\t%.2f\t%d\t%s\n' % (iid, centre, bg, sex, age, height, weight, ethnicity))
            except IOError:
                pass

if __name__ == '__main__':
    main()
