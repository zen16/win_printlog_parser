#!/usr/bin/env python3

import csv
import re
import os
import sys
import argparse


SEARCH_PATTERN = r'Document \d{1,3}, (.*) owned by (.*) on (.*) ' \
                 r'was printed on (.*) through port (.*).  ' \
                 r'Size in bytes: (\d*). Pages printed: (\d*). ' \
                 r'No user action is required.'


def create_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('script_path')
    arg_parser.add_argument('-i', '--input_log_file',
                            type=argparse.FileType(encoding="utf8"))
    arg_parser.add_argument('-o', '--output_file',
                            type=argparse.FileType('w'))
    return arg_parser


def get_data_from_printlog(input_csv_file, pattern):
    print(f'#### Reading CSV ####\n'
          f'Input print log CSV-file opened from "{input_csv_file}"')
    with open(input_csv_file, 'r', encoding="utf8") as f:
        f.readline()   # skip first line
        reader = csv.reader(f)
        rows_total = 0
        # write headers
        parsed_data = [('DATE', 'DOCUMENT', 'USER', 'SOURCE_HOST', 'PRINTER', 'PORT', 'SIZE', 'PAGES')]

        for row in reader:
            date = row[1]
            if len(row) == 6:
                match_row = re.search(pattern, row[5])
                if not match_row:
                    print(f"No matches in string: {row[5]}")
                    continue
                parsed_data.append((date, ) + match_row.groups())
            else:
                print(f"\tIncorrect string length:\n{row}")
            rows_total += 1
        print(f'Input rows processed:\t{rows_total}')
    return parsed_data


def write_to_csv(csv_file_path, data):
    # writing out formatted csv-file
    print("\n#### Writing CSV ####")
    csv_file_dir = os.path.dirname(csv_file_path)
    if not os.path.isdir(csv_file_dir):
        os.makedirs(csv_file_dir)
        print(f"Created directory\t'{csv_file_dir}'")
    with open(csv_file_path, 'w', encoding='cp1251', errors='ignore') as out_f:
        writer = csv.writer(out_f, delimiter=';', lineterminator='\n')
        writer.writerows(data)
        print(f'Formatted CSV-csv written to "{csv_file_path}"')
        print(f'Rows written out:\t{len(data)}\n')


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args(sys.argv)

    script_dir = os.path.abspath(os.path.dirname(args.script_path))
    if args.input_log_file:
        input_log_file = args.input_log_file.name
        if not os.path.isfile(input_log_file):
            print(f'Sorry. No such file: {input_log_file}')
            sys.exit(1)
    else:
        # try to take one of csv-files from script directory
        os.chdir(script_dir)
        csv_in_dir = [csv for csv in os.listdir(script_dir) if csv.lower().endswith('.csv') and os.path.isfile(csv)]
        csv_file_id = 0
        if len(csv_in_dir) == 0:
            print(f"There's no csv-files in the directory '{script_dir}'.\n Please, put the csv-file to directory"
                  f" or call the script with parameter '-i <path_to_csv>'.\nProgram will be closed.")
            sys.exit(1)
        elif len(csv_in_dir) == 1:
            pass   # csv_file_id = 0
        else:
            print("There's few csv-files in the directory:")
            for i, csv_input_file in enumerate(csv_in_dir):
                print('\t{}\t{}'.format(i, csv_input_file))
            while True:
                csv_file_id_str = input("Please, input csv number: ")
                if len(csv_file_id_str) == 0:
                    print('Nothing entered. Program will be closed.')
                    sys.exit(1)
                if csv_file_id_str.isdigit():
                    csv_file_id = int(csv_file_id_str)
                    if 0 <= csv_file_id < len(csv_in_dir):
                        print(f'You choose {csv_in_dir[csv_file_id]}')
                        break
                print("Incorrect number.")

        input_log_file = os.path.join(script_dir, csv_in_dir[csv_file_id])

    if not args.output_file:
        output_file = os.path.join(script_dir, "PARSED", "parsed_print_log.csv")
    else:
        output_file = args.output_file.name

    string_pattern = re.compile(SEARCH_PATTERN)

    mined = get_data_from_printlog(input_log_file, string_pattern)
    write_to_csv(output_file, mined)
