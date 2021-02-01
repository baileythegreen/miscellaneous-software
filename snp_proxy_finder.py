!ls
from typing import NamedTuple
import queue, threading
import inspect
from profilehooks import profile
import yaml
import requests, sys

def lineno():
    """Returns the current line number in our program."""
    return "line number: %d" % inspect.currentframe().f_back.f_lineno

class Snp(NamedTuple):
    rsid: str
    chrom: int
    line: list

class TSnp(NamedTuple):
    rsid: str
    chrom: int
    ld: set
dir(requests)
class Subset():
    def __init__(self):
        self.__dict__.update({'ends': [set() for i in range(10)]})
        self.__dict__.update({'rows': [{} for i in range(10)]})
        self.inbox = queue.Queue()
        self.workers = []
        self.working = threading.Event()
        for i in range(5):
            self.workers.append(threading.Thread(target = self.add_snp))
        self.manager = threading.Thread(target = self.start_work)
        self.manager.start()
    def start_work(self):
        while True:
            self.working.wait()
            [t.start() for t in self.workers]
            [t.getName() for t in self.workers]
            return
    def add_snp(self):
        while True:
            try:
                snp = self.inbox.get(timeout = 10)
                self.ends[int(snp.rsid[-1])].add(snp.rsid)
                self.rows[int(snp.rsid[-1])][snp.rsid] = snp.line
            except queue.Empty:
                print("Line %s: Queue empty" % (35))
                self.working.clear()
                break

class SnpSet():
    def __init__(self, subset = False):
        self.subset = subset
        if self.subset:
            self.__dict__.update({f'chrom{i}': Subset() for i in range(1,23)} )
        else:
            self.__dict__.update({f'chrom{i}': {} for i in range(1,23)} )
            self.search_queue = queue.Queue()  #new
    def add_snp(self, rsid, chrom, row = None, ld_snps = None):
        chromosome = chrom
        chrom = 'chrom' + chrom
        if self.subset:
            exec(f'self.{chrom}.inbox.put(Snp(rsid, chrom, row))')                     #*
            exec(f'self.{chrom}.working.set()')
        else:
            exec(f'self.{chrom}[rsid] = TSnp(rsid, chrom, ld_snps)')
            self.search_queue.put((chrom, rsid))

def process():
    while True:
        try:
            format, row = lines.get(timeout = 10)
            row = row.lower().split()
            def wil(line):
                rsid = line[0]                          #
                if rsid != ".":
                    chrom = str(line[2])                #
                    wilson.add_snp(rsid, chrom, row)                                   #*
            def ten(line):
                rsid = line[2]                          #
                chrom = line[0]                         #
                ld_snps = line[11].split(';')           #
                tenesa.add_snp(rsid, chrom, ld_snps)
            if format == 'wilson':
                wil(row)
            elif format == 'ld_clumps':
                ten(row)
        except queue.Empty:
            break


#@profile
def read(file):                                 #this could take in a list of files
    print("Line %s: Opening file." % (79))
    format = files[file]['format']
    with open(files[file]['file_name']) as f:
        f.readline()
        while True:
            line = f.readline()
            if not line: break
            lines.put((format, line))                 #
        print("Line %s: Read in file finished." % (89))
#    with open(file['file_name']) as f:
#        while True:
#            line = f.readline()
#            if not line: break
#            lines.put((format, line))                 #
#        print("Line %s: Read in wilson file finished." % (84))
#        #next(f)
#        #for _ in range(1000000):
#        #    lines.put(('wilson', next(f)))
#        f.readline()



def search():  #function to search inside the data structures for snps; should be parallel
    while True:
        try:
            chrom, rsid = tenesa.search_queue.get(timeout = 10)
            snps = eval(f'wilson.{chrom}.ends[int(rsid[-1])]')
            if rsid in snps:
                proxies[rsid] = [rsid]
            else:
                ld_snps = eval(f'tenesa.{chrom}[rsid].ld')
                try:
                    potential_proxies = eval(f'[x for x in ld_snps if x in wilson.{chrom}.ends[int(x[-1])]]')
                    proxies[rsid] = best_proxy(rsid, potential_proxies)
                except ValueError:
                    print('Problematic snp: %s' % rsid)
        except queue.Empty:
            break

def get_args(file):
    with open(file) as f:
        docs = list(yaml.safe_load_all(f)) #returns a list of dictionaries,
                                           #one per document
        globals()['files'] = {k:v for x in docs if x != None for k,v in x.items()}
        #globals()['files'] = [{k: v for x in docs for k, v in x.items()}]


tenesa_file = "geneatlas_height_snps.tsv"
wilson_file = "ulna.tsv"


server = "https://grch37.rest.ensembl.org"
ext = "/ld/human/pairwise/"
def ld_get(rs1, rs2):
    r = requests.get("%s%s%s/%s?" % (server, ext, rs1, rs2), headers = {"Content-Type": "application/json"})
    if not r.ok:
       r.raise_for_status()
       sys.exit()
    ld_info = r.json()
    return ld_info

def pop_ld(ld_info, population = 'GBR'):
    rsquare = [float(x['r2']) for x in ld_info if x['population_name'].endswith(population)]
    return rsquare[0] if len(rsquare) > 0 else 0

def best_proxy(rsid, potential_proxies):
    rsquare = 0
    best = None
    while len(potential_proxies) > 0:
        proxy = potential_proxies.pop()
        ld_info = ld_get(rsid, proxy)
        if pop_ld(ld_info) > rsquare:
            rsquare = pop_ld(ld_info)
            best = proxy
    return best

=============================================
arg_file = "snp_proxy_config.yaml"
get_args(arg_file)
tenesa = SnpSet()
wilson = SnpSet(subset = True)
lines = queue.Queue()
read()
readers = []
searchers = []
for x in range(5):
    readers.append(threading.Thread(target = process))
    searchers.append(threading.Thread(target = search))
read('index_snps')
read('sumstats')
[t.start() for t in readers]
[t.join() for t in readers]
[t.join() for i in range(1,23) for t in eval(f'wilson.chrom{i}.workers')]
proxies = {}
[t.start() for t in searchers]
[t.join() for t in searchers]



def main():
    for x in range(5):
        readers.append(threading.Thread(target = process))
    [t.start() for t in readers]
    [t.join() for t in readers]
    [t.join() for t in wilson.chr1.workers]





#========================================================================

#@profile
def test():                                                 #need to find a way to multithread this
    print("Line %s: Opening file." % (88))
    with open(wilson_file) as f:
        next(f)
        data2 = [next(f).lower().split() for x in range(1000000)]
        for line in data2:
            process('wilson', line)
        print("Line %s: Read in file finished." % (94))

#def add_snp(holder, type, key, *value):
#    holder[key] = type(*value)

#def read_in_file(file, format):
#	with open(file) as f:
#		for line in enumerate(f):
#			line = line.lower.split()
#			processor(format, line)
#
#def read_in_file(file, format):
#    with open(wilson_file) as f:
#        next(f)
#        data2 = [next(f).lower().split() for x in range(1,10)]
#        for line in data2:
#            #line = line.lower.split()
#            process(format, line)



#def namedtupleise(holder, type, key, *value):
#    holder[key] = type(*value)



#Snp(chrom, ld)

#exec(f'wilson.{chrom}.ends[rsid[-1]].add(rsid)')
#eval(f'wilson.{chrom}.ends[rsid[-1]].add(rsid)')


#wilson.chr1.minions = []
#for i in range(5):
#    wilson.chr1.minions.append(threading.Thread(target = wilson.chr1.add_snp))

#[t.start() for t in wilson.chr1.minions]


#read_in_file(tenesa_file, 'tenesa')

#'rs4641' in wilson.chr1.end1   #works
#'rs8274' in eval(f'wilson.{chrom}.{subset}')  #also works

#exec(f'wilson.{chrom}.ends[int(rsid[-1])].add(rsid)')

#[x[0] for x in data[1:]]
#Snp(data[1][0], set(data[1][11].split(';')))
#rsid = Snp(data[row][0], set(data[row][11].split(';')))
#wilson_snps[rsid[-1]].add(rsid)
#globals().update({f'chr{i}':{} for i in range(1,23)} )
#[globals().update(f'chr{i}':{}) for i in range(22)]
#globals().update({'chrom' + str(i) for i in range(1,23)})  # python 2 version
#namedtupleise(wilson.chrom[subset], Snp, rsid, chrom)
#namedtupleise(tenesa.chrom[subset], Snp, rsid, chrom, ld_snps)
# data = [next(f).lower().split() for x in range(10)]


#class Subset():
#    def __init__(self):
#        self.__dict__.update({'ends': [set() for i in range(10)]})
#exec(f'wilson.{chrom}.ends[int(rsid[-1])].add(rsid)')
#eval(f'wilson.{chrom}.ends[int(rsid[-1])].add(rsid)')
