# TODO: Find the best place for this file.

# Utility functions used project wide.

from Bio import SeqIO
from io import TextIOWrapper


def get_fasta_from_file(in_memory_file):
    file = TextIOWrapper(in_memory_file, 'utf-8')
    fasta_seq = SeqIO.parse(file, 'fasta')
    records = []
    for record in fasta_seq:
        temp = record.id, str(record.seq).lower()
        records.append(temp)
    file.close()
    return records
