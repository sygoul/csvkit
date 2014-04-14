#!/usr/bin/env python

from collections import defaultdict
from operator import itemgetter

from csvkit import table, CSVKitWriter
from csvkit.cli import CSVKitUtility

class CSVStat(CSVKitUtility):

    description = 'Print a frequency table for the values of the specified column in a CSV file.'

    override_flags = ['l']

    def add_arguments(self):
        self.argparser.add_argument('-c', '--columns', dest='columns',
            help='A column index or name to be examined.')
        self.argparser.add_argument('--percentage', dest='percentage',
            action='store_true',
            help='Print also a relative frequency (percentage) column')
        self.argparser.add_argument('--cumulative', dest='cumulative',
            action='store_true',
            help='Print also cumulative column(s)')

    def main(self):

        if not self.args.columns:
            self.argparser.error('A column index or name must be specified.')

        #elif len(parse_column_identifiers(self.args.columns, )) > 1:
            #self.argparser.error('Only one column index or name may be specified.')

        tab = table.Table.from_csv(
            self.args.file,
            column_ids=self.args.columns,
            zero_based=self.args.zero_based,
            no_header_row=self.args.no_header_row,
            **self.reader_kwargs
        )


        for c in tab:
            
            frequencies = defaultdict(lambda : 0)
            
            for value in filter(lambda i: i is not None, c):
                frequencies[value] += 1

            print_frequencies(frequencies, c.name, self.output_file,
                              write_percentage=self.args.percentage,
                              write_cumulative=self.args.cumulative,
                              **self.writer_kwargs)


def print_frequencies(frequencies, header, fout,
                      write_percentage=False, write_cumulative=False,
                      **writer_kwargs):

    sorted_frequencies = sorted(frequencies.items(),
                                key=itemgetter(1),
                                reverse=True)
    total_freq = 0
    for item in sorted_frequencies:
        total_freq += item[1]

    headers = [header, u'Frequency']
    if write_cumulative:
        headers.append(u'Cumulative Frequency')
    if write_percentage:
        headers.append(u'Percentage')
    if write_cumulative and write_percentage:
        headers.append(u'Cumulative Percentage')

    writer = CSVKitWriter(fout, **writer_kwargs)

    writer.writerow(headers)

    cumulative_freq = 0
    for value, freq in sorted_frequencies:

        cumulative_freq += freq

        row = [unicode(value), freq]
        if write_cumulative:
            row.append(cumulative_freq)
        if write_percentage:
            row.append(100 * float(freq) / total_freq)
        if write_cumulative and write_percentage:
            row.append(100 * float(cumulative_freq) / total_freq)

        writer.writerow(row)

def launch_new_instance():
    utility = CSVStat()
    utility.main()
    
if __name__ == "__main__":
    launch_new_instance()

