import pandas as pd
import numpy as np
import sys, optparse
import re
import pprint

def read_extraction_file(file):
    phens = []
    with open(file) as f:
        for line in f:
           phens.append(line.strip().split())
    return phens

def rename(x):
    try:
        return translations.ix[x]['Field_name'].lower()
    except (KeyError, AttributeError):
        return x

def grab_chunk():
    #ukbb_phen_reader = pd.read_csv(pheno_file, header = 'infer', sep = "\t", index_col = 0, chunksize = 10000)
    extractor = get_columns()
    next(extractor) #or extractor.next()
    while True:
        try:
            chunk = ukbb_phen_reader.get_chunk()
        except:
            break
        chunk.columns = pd.MultiIndex.from_tuples(map(lambda x: (x, x.split(".")[1], rename(int(x.split(".")[1]))), chunk.columns))
        extractor.send(chunk)
        yield
def get_columns():
    chunk = None
    field_numbers = []
    for trait in desired_phens:
        if str(trait[0]).startswith('f.') or str(trait[0]).isdigit() or bool(re.match(r'([0-9.]+)$', str(trait[0]))):
            field_numbers.append(trait[0].strip('f.'))
        else:
            if len(translations[translations['Field_name'] == trait[0]]) == 1:
                [field_numbers.append(str(x)) for x in translations.index[translations['Field_name'] == trait[0]].tolist()]
            else:
                [field_numbers.append(str(x)) for x in translations.index[translations['Field_name'].str.contains(trait[0], case = False, na = False)].tolist()]
    print 'Number of fields to be extracted: %d' % len(field_numbers)
    print 'Fields to be extracted: %s' % field_numbers
    while True:
        chunk = (yield chunk)
        extract = chunk[[x for x in chunk.columns if str(x[1]) in field_numbers or x[0].strip('f.') in field_numbers]]
        with open(out_file, 'at') as f:
            extract.to_csv(f, sep = "\t", na_rep = "NA", header = not bool(f.tell()), index = True)

#def process_chunk(file_reader, phen_requests):
#    try:
#        chunk = file_reader.get_chunk()
#    except:
#        pass
#    chunk.columns = pd.MultiIndex.from_tuples(map(lambda x: (x, x.split(".")[1], rename(int(x.split(".")[1]))), chunk.columns))
#    requested_phens = 


#    chunk[[x for x in chunk.columns if x[0].split(".")[1] == str(54)]]

def help():
    print '''
    =======================================================================================================================
    Usage:
    
    python ukbb_phenotype_extractor.py -p <pheno_file> -e <extract_file> [, -o <out_file> [, -t <translation_file> ] ]
    
    A pheno_file and an extract file must be provided.
    
    An output file name and translation file may be optionally specified;
    if these are not given, default values will be used.

    For more information, run:

    python ukbb_phenotype_extractor.py -h

    or

    python ukbb_phenotype_extractor.py --help
    =======================================================================================================================
    '''
    sys.exit(1)

def parse_options(values):
    p = optparse.OptionParser()
    p.add_option("-p", action = "store", dest = "pheno_file")
    p.add_option("--phenos", action = "store", dest = "pheno_file")
    p.add_option("-e", action = "store", dest = "extract_file")
    p.add_option("--extract", action = "store", dest = "extract_file")
    p.add_option("-o", action = "store", dest = "out_file")
    p.add_option("--output", action = "store", dest = "out_file")
    p.add_option("-t", action = "store", dest = "translation_file")
    p.add_option("--translations", action = "store", dest = "translation_file")
    p.set_defaults(out_file = 'extracted_ukbb_phenotpes.tsv', translation_file = '/exports/igmm/eddie/haley-lab/Common/UKB/ukb27263_fields.tsv')
    return p.parse_args()


def main():
    if len(sys.argv) == 1: help()
    opts, args = parse_options(sys.argv)
    print 'opts:'
    pprint.pprint(opts)
    pprint.pprint('args: %s' % args)
    globals().update({'desired_phens' : read_extraction_file(opts.extract_file)})
    globals().update({'ukbb_phen_reader' : pd.read_csv(opts.pheno_file, header = 'infer', sep = "\t", index_col = 0, chunksize = 10000, memory_map = True, low_memory = False)})
    globals().update({'translations' : pd.read_csv(opts.translation_file, header = 'infer', sep = "\t", index_col = 0)})
    globals().update({'out_file' : opts.out_file})
    trial = grab_chunk()
    while True:
        try:
            next(trial)
        except StopIteration:
            break
    print 'Extraction completed.'


if __name__ == '__main__':
    main()
