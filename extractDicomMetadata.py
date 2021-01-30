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
    return p.parse_args()

def main():
    print sys.argv
    if len(sys.argv) == 1: help()
    opts, args = parse_options(sys.argv)
    scan_dir = args[0]
    #set the scan directory
    os.chdir('%s' % scan_dir)
    #Create a container of all the relevant files
    folder = glob.glob('*.dcm')
    with open('./metadata_covariates.tsv', 'w+') as outfile:
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
