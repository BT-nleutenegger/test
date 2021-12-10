import os
import sys
import tempfile
'''
This script will allow us to correctly 
parser the XML and format it to pretty print. 

Example of Use:

 python prepare.py jan/out-flow-report--message.xml  jan/2.xml

Later we can do:
 meld jan/2.xml jan/its-server.xml
'''
if len(sys.argv) != 4:
	print("Use $python prepare.py input_file output_file its_file")
x1 = tempfile.NamedTemporaryFile()

os.system("xmllint --encode UTF-8 --format {input_file} > {x1}".format(input_file=sys.argv[1],
                                                                       x1=x1.name))

x = open(x1.name, "rb")
substring_list = ['soapenv', 'CreationDate']
with tempfile.NamedTemporaryFile() as x2:
        line = x.readline()
        is_in_requestcontext_tag = False

        while line != "":
            if any(substring in line for substring in substring_list):
                line = x.readline()
            elif 'RequestContext' in line:
                if not is_in_requestcontext_tag:
                    is_in_requestcontext_tag = True
                else:
                    is_in_requestcontext_tag = False
                line = x.readline()
            elif is_in_requestcontext_tag:
                line = x.readline()
            else:
                aux = line.replace('ns2:', '').replace('ns3:', '')
                x2.write(aux)
                x2.flush()
                line = x.readline()

        command = "xmllint --encode UTF-8 --format {0} > {1} ".format(x2.name,
                                                                      sys.argv[2])
        os.system("cp -R {input_file} /tmp/mozilla_jool10/.".format(input_file=x2.name))
        os.system(command)

x.close()
# with the first call we can get the meld
# with the second one, we safe the diff into diff_qst_month.txt -> if this file has a size of 0 the xml is correct
os.system("meld {0} {1}".format(sys.argv[2], sys.argv[3]))
# os.system("diff {0} {1} > diff_qst_month.txt".format(sys.argv[2], sys.argv[3]))

