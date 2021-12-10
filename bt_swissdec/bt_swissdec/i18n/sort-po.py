#!/usr/bin/python

import sys, getopt, re
from operator import itemgetter, attrgetter
import argparse
import collections

def sortPo(file, module):
    """Read in the file and returns a array of
        [0]: module name (e.g. res_partner)
        [1]: tag line (e.g. #: model:ir.actions.act_window,help:res_partner.additional_name)
        [2]: ir.translation.src
        [3]: ir.translation.value
    """
    prefix = ""
    module_name = False
    po = []

    for line in file:

        # in the header
        if not module_name and not re.search(r"^#\. module:", line):
            prefix += line

        else:
            # start with "#. module"
            if re.search(r"^#\. module:", line):

                # if not first module
                if module_name:
                    for key in keys:
                        po.append([module_name, key, msgid, msgstr])

                module_name = re.sub(r"^#\. module:\s*(.*)\n", '\\1', line)
                keys = []
                msgid = msgstr = False

            elif re.search(r"^#:", line):
                keys.append(re.sub(r"(.*)\n", '\\1', line))

            elif re.search(r"^msgid ", line):
                msgid = re.sub(r"msgid\s*(.*)", '\\1', line)

            elif re.search(r"^msgstr ", line):
                msgstr = re.sub(r"msgstr\s*(.*)", '\\1', line)

            # multiline msgid or msgstr
            elif re.search(r"^\"", line):
                if not msgstr:
                    msgid += line
                else:
                    msgstr += line

    # handle the last entry (id any)
    if module_name:
        for key in keys:
            po.append([module_name, key, msgid, msgstr])

    po2 = []
    for po_line in po:
        module_name, key, msgid, msgstr = po_line

        # We only remove the name of the module if we indicated the name of the module,
        # i.e. if the option -m was provided, AND only if the entry doesn't correspond
        # to a menuitem, since in that case removing the module causes the entry in the
        # PO to be hidden and thus the translations not to be considered.
        if module and not re.search(r"^#: model:ir.ui.menu,", key):
            key = key.replace(":{0}.".format(module), ':')
        po2.append([module_name, key, msgid, msgstr])
    poFileContent = collections.namedtuple('poFileContent', ['prefix', 'values'])
    vals = poFileContent(prefix=prefix, values=sorted(po2, key=itemgetter(0, 2, 1)))
    return vals

def is_same_record(record1, record2):
    """Return True if the records are equivalent.
    """

    if type(record1) == tuple:
        record1 = list(record1)
    if type(record2) == tuple:
        record2 = list(record2)

    if (
        # 0: e.g. #. module: res.partner
        record1[0] == record2[0] and

        # 1: e.g. #: #: code:addons/translation_test/translation_test.py:34
        # here the line number after ":" doen't matter
        re.sub(r"(.*):\d*$", '\\1', record1[1]) == re.sub(r"(.*):\d*$", '\\1', record2[1]) and \

        # 2: msgid "This is a help"
        record1[2] == record2[2]
    ):
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description='Find differences between two .po files and sort them for SVN diff')

    parser.add_argument("-m", "--module", nargs="?", dest="module", type=str,
                        help="Module name to store this po file")
    parser.add_argument("-i1", "--infile1", nargs="?", dest="infile1", type=argparse.FileType('r'),
                        help="i18n file from addons folder")
    parser.add_argument("-i2", "--infile2", nargs="?", dest="infile2", type=argparse.FileType('r'),
                        help="i18n file exported from odoo-server")
    # We just open the file for appending, to not destroy the file, e.g. for inline sorting
    parser.add_argument("-o", "--output", nargs="?", dest="output", type=argparse.FileType('a'), default=sys.stdout,
                        help="Filename to store the differences between the two files")
    parser.add_argument("-s", "--just-sort", dest="justSort", action='store_true',
                        help="Just sort the --infile1 and exit")
    parser.add_argument("-M", "--merge", dest="merge", action='store_true',
                        help="On sort, merges identical translations together")
    args = parser.parse_args()



    if args.justSort:
        infile1_sorted = sortPo(args.infile1, args.module)

        # truncate now
        args.output.seek(0)
        args.output.truncate(0)

        args.output.write(infile1_sorted.prefix)
        if args.merge:
            last_entry = False
            for entry in infile1_sorted.values:
                if last_entry:
                    if (last_entry[0], last_entry[2], last_entry[3]) == (entry[0], entry[2], entry[3]):
                        if last_entry[1] != entry[1]:
                            last_entry[1] = last_entry[1] + "\n" + entry[1]
                        entry[1] = None
                if entry[1]:
                    last_entry = entry
        last_entry = False
        # entries starting with "code:" -> save msgid in code_msgids
        code_msgids = []
        for entry in infile1_sorted.values:
            if entry[1] is None:
                continue
            # just write if either first line or not the same entry than the last
            if not last_entry or not is_same_record(last_entry, entry):
                # remove :lineno at the end
                entry_1 = re.sub(r"(.*):\d*$", '\\1', entry[1])
                if entry_1.startswith("#: code:"):
                    entry_1 += ':0'
                    if entry[2] in code_msgids:
                        print('------------')
                        print('Entry already exists! Make sure you have different msgids for terms in code.')
                        print(entry)
                        continue
                # add :0
                if entry_1.startswith("#: selection:"):
                    entry_1 += ':0'
                if entry_1.startswith("#: constraint:"):
                    entry_1 += ':0'
                if entry_1.startswith("#: sql_constraint:"):
                    entry_1 += ':0'

                # Use msgid as msgstr, if msgstr is empty
                # Odoo don't remove the ir.translation record, if we change msgstr to empty (old translation remains in the DB).
                entry_3 = entry[3]
                if entry_3 == '""\n':
                    entry_3 = entry[2]

                code_msgids.append(entry[2])
                args.output.write("#. module: " + entry[0] + "\n")
                args.output.write(entry_1 + "\n")
                args.output.write("msgid " + entry[2])
                args.output.write("msgstr " + entry_3)
                args.output.write("\n")
            else:
                #print(entry)
                pass
            last_entry = entry

    else:
        try:
            infile1_sorted = sortPo(args.infile1, args.module)
            infile2_sorted = sortPo(args.infile2, args.module)
        except IOError:
            print('Please use -i1 FILE -i2 FILE')

        # compare the two files
        differences = []
        for idx2, value2 in enumerate(infile2_sorted.values):
            for idx1, value1 in enumerate(infile1_sorted.values):
                if is_same_record(value1, value2):
                    break
            else:
                differences.append(value2)

        # truncate now
        # args.infile1.close()
        args.output.seek(0)
        args.output.truncate(0)

        last_entry = False
        # entries starting with "code:" -> save msgid in code_msgids
        code_msgids = []
        for entry in differences:
            # just write if either first line or not the same entry than the last
            if not last_entry or not is_same_record(last_entry, entry):
                # remove :lineno at the end
                entry_1 = re.sub(r"(.*):\d*$", '\\1', entry[1])
                if entry_1.startswith("#: code:"):
                    entry_1 += ':0'
                    if entry[2] in code_msgids:
                        print('------------')
                        print('Entry already exists! Make sure you have different msgids for terms in code.')
                        print(entry)
                        continue
                # add :0
                if entry_1.startswith("#: selection:"):
                    entry_1 += ':0'
                if entry_1.startswith("#: constraint:"):
                    entry_1 += ':0'
                if entry_1.startswith("#: sql_constraint:"):
                    entry_1 += ':0'

                # Use msgid as msgstr, if msgstr is empty
                # Odoo don't remove the ir.translation record, if we change msgstr to empty (old translation remains in the DB).
                entry_3 = entry[3]
                if entry_3 == '""\n':
                    entry_3 = entry[2]

                code_msgids.append(entry[2])
                args.output.write("#. module: " + entry[0] + "\n")
                args.output.write(entry_1 + "\n")
                args.output.write("msgid " + entry[2])
                args.output.write("msgstr " + entry_3)
                args.output.write("\n")
            else:
                # print(entry)
                pass
            last_entry = entry

        args.infile2.close()

    args.output.close()
    exit



#     outputfile = open(outputfile, "w")
#     outputfile.write(prefix)
#     for tupel in po_sorted:
#         outputfile.write("#. module: " + tupel[0] + "\n")
#         outputfile.write(tupel[1] + "\n")
#         outputfile.write("msgid " + tupel[2])
#         outputfile.write("msgstr " + tupel[3])
#         outputfile.write("\n")
#
#     outputfile.close()
#
#
#
#     print po
#
#
#
# #        outputfile.writelines(data_parser(line, reps))
#
#     print 'Input file is "', inputfile
#     print 'Output file is "', outputfile

if __name__ == "__main__":
    main()
