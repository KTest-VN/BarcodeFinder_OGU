#!/usr/bin/python3

import argparse
import json
import logging
import re

from functools import lru_cache
from io import StringIO
from os.path import join as join_path
from os.path import splitext, basename
from pathlib import Path
from pkg_resources import resource_filename
from time import sleep

from Bio import Entrez, SeqIO
from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqRecord import SeqRecord

from BarcodeFinder import utils

# define logger
FMT = '%(asctime)s %(levelname)-8s %(message)s'
DATEFMT = '%H:%M:%S'
logging.basicConfig(format=FMT, datefmt=DATEFMT, level=logging.INFO)
log = logging.getLogger('barcodefinder')
try:
    import coloredlogs
    coloredlogs.install(level=logging.INFO, fmt=FMT, datefmt=DATEFMT)
except ImportError:
    pass


# load data
with open(resource_filename('BarcodeFinder', 'data/superkingdoms.csv'),
          'r') as _:
    SUPERKINGDOMS = set(_.read().split(','))
with open(resource_filename('BarcodeFinder', 'data/kingdoms.csv'),
          'r') as _:
    KINGDOMS = set(_.read().split(','))
with open(resource_filename('BarcodeFinder', 'data/phyla.csv'),
          'r') as _:
    PHYLA = set(_.read().split(','))
with open(resource_filename('BarcodeFinder', 'data/classes.csv'),
          'r') as _:
    CLASSES = set(_.read().split(','))
with open(resource_filename('BarcodeFinder', 'data/animal_orders.csv'),
          'r') as _:
    ANIMAL_ORDERS = set(_.read().split(','))


def parse_args(arg_list=None):
    arg = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg.add_argument('-gb', nargs='*', help='input filename')
    # trnK-matK
    arg.add_argument('-allow_mosaic_spacer', action='store_true',
                       help='allow mosaic spacer')
    # genes in IR regions
    arg.add_argument('-allow_repeat', action='store_true',
                       help='allow repeat genes or spacer')
    arg.add_argument('-allow_invert_repeat', action='store_true',
                       help='allow invert-repeat spacers')
    # for primer
    arg.add_argument('-expand', type=int, default=0,
                     help='expand length of upstream/downstream')
    arg.add_argument('-max_name_len', default=100, type=int,
                     help='maximum length of feature name')
    # handle rps12
    arg.add_argument('-max_seq_len', default=20000, type=int,
                     help='maximum length of feature sequence')
    arg.add_argument('-no_divide', action='store_true',
                     help='only download')
    # for plastid genes
    arg.add_argument('-rename', action='store_true', help='try to rename gene')
    arg.add_argument('-uniq', choices=('longest', 'random', 'first', 'no'),
                     default='first',
                     help='method to remove redundant sequences')
    query = arg.add_argument_group('Query')
    query.add_argument('-email', type=str,
                       help='email address for querying Genbank')
    query.add_argument('-exclude', type='str', help='exclude option')
    query.add_argument('-gene', type=str, help='gene name')
    # in case of same taxonomy name in different group
    query.add_argument('-group',
                         choices=('animals', 'plants', 'fungi', 'protists',
                                  'bacteria', 'archaea', 'viruses'),
                         help='Species kind')
    query.add_argument('-min_len', default=100, type=int,
                         help='minimum length')
    query.add_argument('-max_len', default=10000, type=int,
                         help='maximum length')
    query.add_argument('-date_start', type='str',
                       help='release date beginning, (eg. 1970/1/1)')
    query.add_argument('-date_end', type='str',
                       help='release date end, (eg. 2020/12/31)')
    query.add_argument('-molecular', choices=('DNA', 'RNA'),
                         help='molecular type')
    query.add_argument('-og', '-organelle', dest='organelle',
                         choices=('mt', 'mitochondrion', 'cp',
                                  'chloroplast', 'pl', 'plastid'),
                         help='organelle type')
    query.add_argument('-query', nargs='*', help='query text')
    query.add_argument('-refseq', action='store_true',
                         help='Only search in RefSeq database')
    query.add_argument('-seq_n', default=None, type=int,
                         help='maximum number of records to download')
    query.add_argument('-taxon', help='Taxonomy name')
    if arg_list is None:
        return arg.parse_args()
    else:
        return arg.parse_args(arg_list)


def get_query_string(arg):
    """
    Based on given options, generate query string from Genbank.
    """
    if arg.allow_repeat:
        log.warning("Repeat genes or spacers will be kept as user's wish.")
    if arg.allow_invert_repeat:
        log.warning("Invert-repeat spacers will be kept.")
    if arg.allow_mosaic_spacer:
        log.warning('The "spacers" of overlapped genes will be kept.')
    if arg.expand is not None:
        log.warning(f'Extend sequences to their upstream/'
                    'downstream with {arg.expand} bp')
    if arg.group is not None:
        log.warning('The filters "group" was reported to return abnormal '
                    'records by Genbank. Please consider to use "-taxon" '
                    'instead.')
    if arg.refseq and arg.gene is None:
        log.info('Reset the limitation of sequence length for RefSeq.')
        arg.min_len = None
        arg.max_len = None
    if arg.rename:
        log.warning('BarcodeFinder will try to rename genes by regular '
                    'expression.')
    condition = []
    if arg.group is not None:
        condition.append(f'{arg.group}[filter]')
    if arg.gene is not None:
        if ' ' in arg.gene:
            condition.append('"{arg.gene}"[gene]')
        else:
            condition.append('{arg.gene}[gene]')
    if arg.molecular is not None:
        d = {'DNA': 'biomol_genomic[PROP]',
             'RNA': 'biomol_mrna[PROP]'}
        condition.append(d[arg.molecular])
    if arg.taxon is not None:
        condition.append('{arg.taxon}[organism]')
    if arg.organelle is not None:
        if arg.organelle in ('mt', 'mitochondrion'):
            condition.append('{mitochondrion}[filter]')
        else:
            condition.append('(plastid[filter] OR chloroplast[filter])')
    if arg.refseq:
        condition.append('refseq[filter]')
    if (len(condition) > 0) and (arg.min_len is not None and arg.max_len is
                                 not None):
        condition.append(f'("{arg.min_len}"[SLEN] : "{arg.max_len}"[SLEN])')
    if arg.exclude is not None:
        condition.append('NOT ({})'.format(arg.exclude))
    if arg.date_start is not None and arg.date_end is not None:
        condition.append(f'"{arg.date_start}"[PDAT] : "{arg.date_end}"[PDAT]')
    if not condition:
        return None
    else:
        string = ' AND '.join(condition)
        string = string.replace('AND NOT', 'NOT')
        return string


def init_arg(arg):
    # join nars
    if arg.query is not None:
        arg.query = ' '.join(arg.query)
        log.warning('Query string is not empty, ignore other options.')
    else:
        arg.query = get_query_string(arg)
    arg.out = utils.init_out(arg)
    if arg.gb is None and arg.query is None:
        log.error('Empty input.')
        return None
    if arg.gb is not None:
        # don't move given gb files?
        arg.gb = [Path(i).absolute() for i in arg.gb]
    else:
        arg.gb = list()
    return arg


def download(arg) -> Path:
    """
    Download records from Genbank.
    Because of connection to Genbank website is not stable (especially in
    Asia), it will retry if failed. Ctrl+C to break.
    """
    TOO_MUCH = 50000
    # although Bio.Entrez has max_tries, current code could handle error
    # clearly
    RETRY_MAX = 10
    if arg.email is None:
        Entrez.email = 'guest@example.com'
        log.info(f'\tEmail address for using Entrez missing, '
                 f'use {Entrez.email} instead.')
    else:
        Entrez.email = arg.email
    query_handle = Entrez.read(Entrez.esearch(db='nuccore', term=arg.query,
                                              usehistory='y'))
    count = int(query_handle['Count'])

    if count == 0:
        log.warning('Got 0 record. Please check the query.')
        log.info('Abort download.')
        return None
    elif count > TOO_MUCH:
        log.warning(f'Got {count} records. May cost long time to download.')
    else:
        log.info(f'\tGot {count} records.')
    if arg.seq_n is not None:
        if count > arg.seq_n:
            count = arg.seq_n
            log.info(f'\tDownload {arg.seq_n} records because of "-seq_n".')
    log.info('\tDownloading...')
    log.warning('\tMay be slow if connection is bad. Ctrl+C to quit.')
    name_words = []
    for i in (arg.group, arg.taxon, arg.organelle, arg.gene, arg.query):
        if i is not None:
            name_words.append(i)
    if len(name_words) != 0:
        name = utils.safe_path('-'.join(name_words)) + '.gb'
    else:
        name = 'sequence.gb'
    file_name = arg._gb / name
    output = open(file_name, 'w', encoding='utf-8')
    ret_start = 0
    if count >= 1000:
        ret_max = 1000
    elif count >= 100:
        ret_max = 100
    elif count >= 10:
        ret_max = 10
    else:
        ret_max = 1
    retry = 0
    while ret_start < count:
        log.info('\t{:d}--{:d}'.format(ret_start, ret_start + ret_max))
        # Entrez accept at most 3 times per second
        # However, due to slow network, it's fine :)
        try:
            data = Entrez.efetch(db='nuccore',
                                 webenv=query_handle['WebEnv'],
                                 query_key=query_handle['QueryKey'],
                                 rettype='gb',
                                 retmode='text',
                                 retstart=ret_start,
                                 retmax=ret_max)
            output.write(data.read())
        # just retry if connection failed
        # IOError could not handle all types of failure
        except Exception:
            sleep(1)
            if retry <= RETRY_MAX:
                log.warning('Failed on download. Retrying...')
                retry += 1
                continue
            else:
                log.critical(f'Too much failure ({RETRY_MAX} times).')
                log.info('Abort download.')
                return None
        ret_start += ret_max
    log.info('Download finished.')
    json_file = arg._tmp / 'Query.json'
    with open(json_file, 'w', encoding='utf-8') as _:
        json.dump(query_handle, _, indent=4, sort_keys=True)
    log.info(f'The query info was dumped into {json_file}')
    return file_name


def clean_gb(gbfile):
    """
    Records in Genbank may be problematic. Check it before parse and skip
    abnormal records.
    """
    log.info('\tCheck Genbank file to remove abnormal records.')

    def parse_gb(handle):
        record = []
        for line in handle:
            record.append(line)
            if line.startswith('//'):
                yield record
                record = []
            else:
                pass

    wrong = 0
    old_gb = open(gbfile, 'r')
    for record in parse_gb(old_gb):
        # StringIO is faster than write tmp file to disk and read
        tmp_gb = StringIO()
        for _ in record:
            tmp_gb.write(_)
        tmp_gb.seek(0)
        try:
            gb_record = SeqIO.read(tmp_gb, 'gb')
            yield gb_record
        except Exception as e:
            log.critical('\tFound problematic record {}: {}'.format(
                record[0][:25], e.args[0]))
            wrong += 1
    tmp_gb.close()
    old_gb.close()
    if wrong != 0:
        log.info('\tRemove {} abnormal records.'.format(wrong))


@lru_cache(maxsize=None)
def gene_rename(old_name: str, genbank_format=False) -> (str, str):
    """
    Old doc:
        Different name of same gene will cause data to be splited to numerous
        files instead of one and some data may be dropped.

        For chloroplast genes, the author summarized various kinds of
        annotation error of gene name or synonyms and try to use regular
        expression to fix it.

        Ideally, use BLAST to re-annotate sequence is the best(and slow) way to
        find the correct name. This function only offers a "hotfix" which is
        enough.
    Rename plastid genes.
    May be dangerous.
    Will cache results.
    Args:
        old_name: old gene name
        genbank_format: use style like "trnH-GUG" or "trnHgug"
    Returns:
        new_name(str): new name, if fail, return old name
        gene_type(str): gene types, guessed from name
    """
    lower = old_name.lower()
    # (trna|trn(?=[b-z]))
    s = re.compile(r'(\d+\.?\d?)(s|rrn|rdna)')
    if lower.startswith('trn'):
        pattern = re.compile(r'([atcgu]{3})')
        prefix = 'trn'
        aa_letter = 'X'
        try:
            anticodon = Seq(re.search(pattern, lower[3:]).group(1))
        except Exception:
            return old_name, 'bad_name'
        # rna editing? trnI-CAU
        if anticodon == 'cau' and lower.startswith('trni'):
            aa_letter = 'I'
        # for trnfM-CAU
        elif lower.startswith('trnfm'):
            prefix = 'trnf'
            aa_letter = 'M'
        else:
            aa_letter = anticodon.reverse_complement().translate().upper()
            #anticodon = anticodon.transcribe()
        if genbank_format:
            new_name = f'{prefix}{aa_letter}-{anticodon.upper()}'
        else:
            new_name = f'{prefix}{aa_letter}{anticodon.lower()}'
        gene_type = 'tRNA'
    elif lower.startswith('rrn'):
        pattern = re.compile(r'(\d+\.?\d?)')
        try:
            number = re.search(pattern, lower).group(1)
        except Exception:
            return old_name, 'bad_name'
        new_name = 'rrn{}'.format(number)
        gene_type = 'rRNA'
    elif re.search(s, lower) is not None:
        new_name = 'rrn{}'.format(re.search(s, lower).group(1))
        gene_type = 'rRNA'
    else:
        pattern = re.compile(r'[^a-z]*'
                             '(?P<gene>[a-z]+)'
                             '[^a-z0-9]*'
                             '(?P<suffix>[a-z]|[0-9]+)')
        match = re.search(pattern, lower)
        try:
            gene = match.group('gene')
            suffix = match.group('suffix')
        except Exception:
            return old_name, 'bad_name'
        new_name = '{}{}'.format(gene, suffix.upper())
        # capitalize last letter
        if len(new_name) > 3:
            s = list(new_name)
            if s[-1].isalpha():
                new_name = '{}{}'.format(
                    ''.join(s[:-1]), ''.join(s[-1]).upper())
        gene_type = 'normal'
    if len(lower) >= 15:
        gene_type = 'suspicious_name'
    return new_name, gene_type


def get_feature_name(feature, arg):
    """
    Get feature name and collect genes for extract spacer.
    Only handle gene, CDS, tRNA, rRNA, misc_feature, misc_RNA.
    """
    def _extract_name(feature):
        if 'gene' in feature.qualifiers:
            name = feature.qualifiers['gene'][0]
        elif 'product' in feature.qualifiers:
            name = feature.qualifiers['product'][0]
        elif 'locus_tag' in feature.qualifiers:
            name = feature.qualifiers['locus_tag'][0]
        elif 'note' in feature.qualifiers:
            name = feature.qualifiers['note'][0]
        else:
            log.debug('Cannot recognize annotation:\n{}'.format(feature))
            name = None
        return name

    name = None
    # ignore exist exon/intron
    accept_type = {'gene', 'CDS', 'tRNA', 'rRNA', 'misc_feature', 'misc_RNA'}
    if feature.type not in accept_type:
        return name
    name = _extract_name(feature)
    if name is None:
        return name
        # log.warning('Unsupport annotation type {}'.format(feature.type))
    if feature.type == 'misc_feature':
        if 'internal transcribed spacer' in name:
            name = 'ITS'
        if 'intergenic_spacer' in name or 'IGS' in name:
            name = name.replace('intergenic_spacer_region', 'IGS')
    if feature.type == 'misc_RNA':
        # handle ITS
        if 'internal transcribed spacer' in name:
            name = name.replace('internal transcribed spacer', 'ITS')
    if name is not None:
        name = utils.safe_path(name)
    else:
        return name
    if arg.rename:
        name = utils.gene_rename(name)[0]
    return name


def get_spacer(genes):
    """
    Given list of genes, extract spacers.
    genes: [name, feature]
    """
    if len(genes) <= 1:
        return []
    spacers = list()
    names = set()
    # sorted according to sequence starting position
    genes.sort(key=lambda x: int(x[1].location.start))
    for i in range(len(genes)-1):
        b_name, before = genes[i]
        c_name, current = genes[i+1]
        invert_repeat = False
        repeat = False
        # gene name may contain "_", use "-" instead
        name = '-'.join([b_name, c_name])
        # 1. A.start--A.end--B.start--B.end
        if before.location.end <= current.location.start:
            # check invert repeat
            invert_name = '-'.join([c_name, b_name])
            if invert_name in names:
                invert_repeat = True
            elif name in names:
                repeat = True
            else:
                names.add(name)
            spacer = SeqFeature(
                type='spacer',
                id=name,
                location=FeatureLocation(before.location.end,
                                         current.location.start),
                qualifiers={'upstream': b_name,
                            'downstream': c_name,
                            'repeat': str(repeat),
                            'invert_repeat': str(invert_repeat)})
            spacers.append(spacer)
        # 2. A.start--B.start--A.end--B.end
        elif before.location.end <= current.location.end:
            # overlap, no spacer
            pass
        # 3. A.start--B.start--B.end--A.end
        else:
            spacer_up = SeqFeature(
                type='mosaic_spacer',
                id=name,
                location=FeatureLocation(before.location.start,
                                         current.location.start),
                qualifiers={'upstream': b_name,
                            'downstream': c_name,
                            'repeat': str(repeat),
                            'invert_repeat': str(invert_repeat)})
            spacer_down = SeqFeature(
                type='mosaic_spacer',
                id='-'.join([c_name, b_name]),
                location=FeatureLocation(current.location.end,
                                         before.location.end),
                qualifiers={'upstream': b_name,
                            'downstream': c_name,
                            'repeat': str(repeat),
                            'invert_repeat': str(invert_repeat)})
            spacers.extend([spacer_up, spacer_down])
    spacers = [i for i in spacers if len(i) != 0]
    return spacers


def get_intron(genes):
    """
    Given list of genes, extract introns.
    genes: [name, feature]
    Return:
        intron(list): [name, feature]
    """
    # exons = []
    introns = []
    for gene_name, feature in genes:
        # for n, part in enumerate(feature.location.parts):
        #     exon = SeqFeature(
        #     type='exon',
        #     id='-'.join([gene_name, n+1]),
        #     location=part,
        #     qualifiers={'gene': gene_name,
        #                 'count': n+1})
        # exons.append(exon)
        strand = feature.location.strand
        # sort by start, no matter which strand
        parts = sorted(feature.location.parts, key=lambda x: x.start)
        n_part = len(parts)
        for i in range(len(parts)-1):
            before = parts[i]
            current = parts[i+1]
            # Z00028
            if before.end >= current.start:
                break
            # complement strand use reversed index
            # n_intron start with 1 instead of 0
            if strand != -1:
                n_intron = i + 1
            else:
                n_intron = n_part - i - 1
            intron = SeqFeature(
                type='intron',
                id='{}.{}'.format(gene_name, n_intron),
                location=FeatureLocation(before.end,
                                         current.start,
                                         before.strand),
                qualifiers={'gene': gene_name,
                            'count': n_intron})
            introns.append(intron)
    return introns


def divide(gbfile, arg):
    """
    Given genbank file, return divided fasta files.
    """
    log.info('Divide {} by annotation.'.format(gbfile))

    def get_taxon(taxon_str):
        """
        Get taxon info based on suffix and list from NCBI taxonomy database.
        """
        # kingdom|phylum|class|order|family|organims(genus|species)
        # add my_ prefix to avoid conflict of "class"
        my_kingdom = ''
        my_phylum = ''
        my_class = ''
        my_order = ''
        my_family = ''
        for item in taxon_str:
            if item in SUPERKINGDOMS:
                my_kingdom = item
            # mix superkingdom and kingdom to reduce name length
            elif item in KINGDOMS:
                my_kingdom = item
            elif item in PHYLA:
                my_phylum = item
            elif item in CLASSES:
                my_class = item
            if item.endswith('ales') or item in ANIMAL_ORDERS:
                my_order = item
            elif item.endswith('aceae') or item.endswith('idae'):
                my_family = item
        # get fake class for plant
        if my_phylum == 'Streptophyta' and my_class == '':
            last_phyta = ''
            for i in taxon_str:
                if i.endswith('phyta'):
                    last_phyta = i
            try:
                my_class = taxon_str[taxon_str.index(last_phyta) + 1]
            except IndexError:
                my_class = ''
        return (my_kingdom, my_phylum, my_class, my_order, my_family)

    # put raw fasta into root of output folder, so not to use clean_path
    raw_fasta = join_path(arg.out, splitext(basename(gbfile))[0] + '.fasta')
    handle_raw = open(raw_fasta, 'w', encoding='utf-8')
    wrote_by_gene = set()
    wrote_by_name = set()
    accession = ''
    for record in clean_gb(gbfile):
        # only accept gene, product, and spacer in misc_features.note
        taxon_str = record.annotations.get('taxonomy', None)
        if taxon_str is None:
            kingdom, phylum, class_, order, family = '', '', '', '', ''
        else:
            kingdom, phylum, class_, order, family = get_taxon(taxon_str)
        # gb annotation may be empty
        organism = record.annotations.get('organism', None)
        if organism is not None:
            organism = organism.replace(' ', '_')
            genus, *species = organism.split('_')
        else:
            genus, species = '', ''
        # species name may contain other characters
        taxon = '{}|{}|{}|{}|{}|{}|{}'.format(kingdom, phylum, class_,
                                              order, family, genus,
                                              '_'.join(species))
        accession = record.annotations.get('accessions', ['', ])[0]
        specimen = record.features[0].qualifiers.get('specimen_voucher',
                                                     ['', ])
        specimen = specimen[0].replace(' ', '_')
        isolate = record.features[0].qualifiers.get('isolate', ['', ])
        isolate = isolate[0].replace(' ', '_')
        # usually the record only has one of them
        specimen = '_'.join([specimen, isolate]).rstrip('_')
        seq_info = (taxon, accession, specimen)
        whole_seq = record.seq
        feature_name = []
        have_intron = {}
        genes = []
        not_genes = []
        # get genes
        for feature in record.features:
            if feature.type == 'source':
                continue
            name = get_feature_name(feature, arg)
            # skip unsupport feature
            # support: gene, CDS, tRNA, rRNA, misc_feature, misc_RNA
            if name is None:
                continue
            if len(name) > arg.max_name_len:
                log.debug('Too long name: {}. Truncated.'.format(name))
                name = name[:arg.max_name_len-3] + '...'
            if feature.type == 'gene':
                genes.append([name, feature])
                # only use gene name as sequence id
                feature_name.append(name)
            else:
                not_genes.append([name, feature])
            if feature.location_operator == 'join':
                # use dict to remove repeat name of gene/CDS/tRNA/rRNA
                have_intron[name] = feature

        # write genes
        wrote = write_seq(genes, seq_info, whole_seq, arg)
        wrote_by_gene.update(wrote)
        # write non-genes
        wrote = write_seq(not_genes, seq_info, whole_seq, arg)
        wrote_by_gene.update(wrote)
        # extract spacer
        spacers = get_spacer(genes)
        # write spacer annotations
        if not arg.allow_mosaic_spacer:
            spacers = [i for i in spacers if i.type != 'mosaic_spacer']
        record.features.extend(spacers)
        # extract intron
        introns = get_intron(have_intron.items())
        record.features.extend(introns)
        if not arg.allow_invert_repeat:
            spacers = [i for i in spacers if i.qualifiers[
                'invert_repeat'] == 'False']
        # write seq
        spacers_to_write = [[i.id, i] for i in spacers]
        # write intron or not?
        introns_to_write = [(i.id, i) for i in introns]
        wrote = write_seq(spacers_to_write, seq_info, whole_seq, arg)
        wrote_by_gene.update(wrote)
        _ = write_seq(introns_to_write, seq_info, whole_seq, arg)
        # write to group_by name, i.e., one gb record one fasta
        if 'ITS' in feature_name:
            name_str = 'ITS'
        elif len(feature_name) >= 4:
            name_str = '{}-...-{}'.format(feature_name[0], feature_name[-1])
        elif len(feature_name) == 0:
            name_str = 'Unknown'
        else:
            name_str = '-'.join(feature_name)
        # directly use genome type as name
        if arg.organelle is not None:
            name_str = '{}_genome'.format(arg.organelle)
        record.id = '|'.join([name_str, taxon, accession, specimen])
        record.description = ''
        filename = join_path(arg.by_name_folder, name_str + '.fasta')
        with open(filename, 'a', encoding='utf-8') as out:
            SeqIO.write(record, out, 'fasta')
            wrote_by_name.add(filename)
        # write raw fasta
        SeqIO.write(record, handle_raw, 'fasta')

    # skip analyze of Unknown.fasta
    unknown = join_path(arg.by_name_folder, 'Unknown.fasta')
    if unknown in wrote_by_name:
        log.info('Skip Unknown.fasta')
        wrote_by_name.remove(unknown)
    log.info('Divide finished.')
    return list(wrote_by_gene), list(wrote_by_name)


def write_seq(record, seq_info, whole_seq, arg):
    """
    Write fasta files to "by-gene" folder only.
    record: [name, feature]
    seq_info: (taxon, accession, specimen)
    ID format: >name|taxon|accession|specimen|type
    Return: {filename}
    """

    def careful_extract(name, feature, whole_seq):
        # illegal annotation may cause extraction failed

        try:
            sequence = feature.extract(whole_seq)
        except ValueError:
            sequence = ''
            log.warning('Cannot extract sequence of {} from {}.'.format(
                name, seq_info[1]))
        return sequence

    path = arg.by_gene_folder
    seq_len = len(whole_seq)
    filenames = set()
    expand_files = set()
    record_uniq = []
    if not arg.allow_repeat:
        names = set()
        for i in record:
            if i[0] not in names:
                record_uniq.append(i)
                names.add(i[0])
    else:
        record_uniq = record

    for i in record_uniq:
        name, feature = i
        # skip abnormal annotation
        if len(feature) > arg.max_seq_len:
            log.debug('Annotaion of {} (Accession {}) '
                      'is too long. Skip.'.format(name, seq_info[1]))
        sequence_id = '>' + '|'.join([name, *seq_info, feature.type])
        filename = join_path(path, feature.type+'.'+name+'.fasta')
        sequence = careful_extract(name, feature, whole_seq)
        with open(filename, 'a', encoding='utf-8') as handle:
            handle.write(sequence_id + '\n')
            handle.write(str(sequence) + '\n')
        filenames.add(filename)
        if arg.expand != 0:
            if feature.location_operator == 'join':
                loc = feature.location.parts
                # ensure increasing order
                # parts do not have sort method
                loc.sort(key=lambda x: x.start)
                new_loc = sum([
                    # avoid IndexError
                    FeatureLocation(max(0, loc[0].start-arg.expand),
                                    loc[0].end, loc[0].strand),
                    *loc[1:-1],
                    FeatureLocation(loc[-1].start,
                                    min(seq_len, loc[-1].end+arg.expand),
                                    loc[-1].strand)])
                feature.location = new_loc
            feature.type = 'expand'
            sequence = careful_extract(name, feature, whole_seq)
            filename2 = join_path(path, '{}.expand'.format(name))
            with open(filename2, 'a', encoding='utf-8') as handle:
                handle.write(sequence_id + '\n')
                handle.write(str(sequence) + '\n')
            expand_files.add(filename2)
    if arg.expand != 0:
        filenames = expand_files
    file_to_analyze = []
    keep = ('gene.fasta', 'misc_feature', 'misc_RNA', 'spacer')
    for i in filenames:
        if i.endswith(keep):
            file_to_analyze.append(i)
        else:
            log.debug('Skip {}'.format(i))
    return filenames


def gb2fasta_main(arg_str=None):
    """
    Collect genbank files and convert them to fasta files.
    Args:
        arg_str(str): arguments string
    Return:
        output(Path): output folder
    """
    if arg_str is None:
        arg = parse_args()
    else:
        arg = parse_args(arg_str.split(' '))
    init_ok, arg = init_arg(arg)
    if not init_ok:
        log.critical('Quit.')
        return None
    log.info(f'Input genbank files:\t{arg.gb}')
    log.info(f'Query: {arg.query}')
    gb_file = download(arg)
    arg.gb.append(gb_file)
    for i in arg.gb:
        divide(i, arg)
    return arg


if __name__ == '__main__':
    gb2fasta_main()