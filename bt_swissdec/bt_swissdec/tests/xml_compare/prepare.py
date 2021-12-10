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
# if len(sys.argv) != 4:
# 	print("Use $python prepare.py input_file output_file its_file")
x1 = tempfile.NamedTemporaryFile()

os.system("xmllint --encode UTF-8 --format {input_file} > {x1}".format(input_file=sys.argv[1],
                                                                       x1=x1.name))


def readline_and_decode(in_file):
    xline = in_file.readline()
    if isinstance(xline, bytes):
        xline = xline.decode("utf-8")
    return xline


substring_list = ['soap:', 'wsse:', 'wsu:', 'ds:', 'ec:', 'CreationDate']
with open(x1.name, "rb") as x:
    with tempfile.NamedTemporaryFile() as x2:
        line = readline_and_decode(x)
        is_in_requestcontext_tag = False

        while line != "":
            if any(substring in line for substring in substring_list):
                line = readline_and_decode(x)
            elif 'RequestContext' in line:
                if not is_in_requestcontext_tag:
                    is_in_requestcontext_tag = True
                else:
                    is_in_requestcontext_tag = False
                line = readline_and_decode(x)
            elif is_in_requestcontext_tag:
                line = readline_and_decode(x)
            else:
                aux = line.replace('ns2:', '').replace('ns3:', '').replace('<Street/>', '').replace(
                    '<Country>SCHWEIZ</Country>', '').replace(
                    '<Country>ITALY</Country>', '').replace('#12336_0', '#1')
                # replacement for monthly
                aux = aux.replace(
                    '<EmployeeNumber>13</EmployeeNumber>', '<EmployeeNumber>7</EmployeeNumber>').replace(
                    '<EmployeeNumber>17</EmployeeNumber>', '<EmployeeNumber>9</EmployeeNumber>').replace(
                    '<EmployeeNumber>21</EmployeeNumber>', '<EmployeeNumber>11.1</EmployeeNumber>').replace(
                    '<EmployeeNumber>27</EmployeeNumber>', '<EmployeeNumber>15</EmployeeNumber>').replace(
                    '<EmployeeNumber>45</EmployeeNumber>', '<EmployeeNumber>24</EmployeeNumber>').replace(
                    '<EmployeeNumber>47</EmployeeNumber>', '<EmployeeNumber>25</EmployeeNumber>').replace(
                    '<EmployeeNumber>49</EmployeeNumber>', '<EmployeeNumber>26</EmployeeNumber>').replace(
                    '<EmployeeNumber>51</EmployeeNumber>', '<EmployeeNumber>27</EmployeeNumber>').replace(
                    '<EmployeeNumber>53</EmployeeNumber>', '<EmployeeNumber>28</EmployeeNumber>').replace(
                    '<EmployeeNumber>55</EmployeeNumber>', '<EmployeeNumber>29</EmployeeNumber>').replace(
                    '<EmployeeNumber>61</EmployeeNumber>', '<EmployeeNumber>31</EmployeeNumber>').replace(
                    '<EmployeeNumber>63</EmployeeNumber>', '<EmployeeNumber>32</EmployeeNumber>').replace(
                    '<EmployeeNumber>65</EmployeeNumber>', '<EmployeeNumber>33</EmployeeNumber>').replace(
                    '<EmployeeNumber>69</EmployeeNumber>', '<EmployeeNumber>35</EmployeeNumber>').replace(
                    '<EmployeeNumber>71</EmployeeNumber>', '<EmployeeNumber>36</EmployeeNumber>').replace(
                    '<EmployeeNumber>73</EmployeeNumber>', '<EmployeeNumber>37</EmployeeNumber>').replace(
                    '<EmployeeNumber>75</EmployeeNumber>', '<EmployeeNumber>38</EmployeeNumber>').replace(
                    '<EmployeeNumber>77</EmployeeNumber>', '<EmployeeNumber>39</EmployeeNumber>').replace(
                    '<EmployeeNumber>83</EmployeeNumber>', '<EmployeeNumber>42</EmployeeNumber>')
                # replacement for yearly
                aux = aux.replace(
                    '<EmployeeNumber>2</EmployeeNumber>', '<EmployeeNumber>1</EmployeeNumber>').replace(
                    '<EmployeeNumber>14</EmployeeNumber>', '<EmployeeNumber>7</EmployeeNumber>').replace(
                    '<EmployeeNumber>95</EmployeeNumber>', '<EmployeeNumber>7.1</EmployeeNumber>').replace(
                    '<EmployeeNumber>18</EmployeeNumber>', '<EmployeeNumber>9</EmployeeNumber>').replace(
                    '<EmployeeNumber>22</EmployeeNumber>', '<EmployeeNumber>11.1</EmployeeNumber>').replace(
                    '<EmployeeNumber>28</EmployeeNumber>', '<EmployeeNumber>15</EmployeeNumber>').replace(
                    '<EmployeeNumber>46</EmployeeNumber>', '<EmployeeNumber>24</EmployeeNumber>').replace(
                    '<EmployeeNumber>48</EmployeeNumber>', '<EmployeeNumber>25</EmployeeNumber>').replace(
                    '<EmployeeNumber>50</EmployeeNumber>', '<EmployeeNumber>26</EmployeeNumber>').replace(
                    '<EmployeeNumber>52</EmployeeNumber>', '<EmployeeNumber>27</EmployeeNumber>').replace(
                    '<EmployeeNumber>54</EmployeeNumber>', '<EmployeeNumber>28</EmployeeNumber>').replace(
                    '<EmployeeNumber>56</EmployeeNumber>', '<EmployeeNumber>29</EmployeeNumber>').replace(
                    '<EmployeeNumber>62</EmployeeNumber>', '<EmployeeNumber>31</EmployeeNumber>').replace(
                    '<EmployeeNumber>64</EmployeeNumber>', '<EmployeeNumber>32</EmployeeNumber>').replace(
                    '<EmployeeNumber>66</EmployeeNumber>', '<EmployeeNumber>33</EmployeeNumber>').replace(
                    '<EmployeeNumber>70</EmployeeNumber>', '<EmployeeNumber>35</EmployeeNumber>').replace(
                    '<EmployeeNumber>72</EmployeeNumber>', '<EmployeeNumber>36</EmployeeNumber>').replace(
                    '<EmployeeNumber>74</EmployeeNumber>', '<EmployeeNumber>37</EmployeeNumber>').replace(
                    '<EmployeeNumber>76</EmployeeNumber>', '<EmployeeNumber>38</EmployeeNumber>').replace(
                    '<EmployeeNumber>78</EmployeeNumber>', '<EmployeeNumber>39</EmployeeNumber>').replace(
                    '<EmployeeNumber>84</EmployeeNumber>', '<EmployeeNumber>42</EmployeeNumber>')
                aux = aux.strip()
                x2.write(str.encode(aux))
                x2.flush()
                line = readline_and_decode(x)

        command = "XMLLINT_INDENT='' xmllint --encode UTF-8 --format {0} > {1} ".format(x2.name, sys.argv[2])
        # command = "xmllint --encode UTF-8 {0} > {1} ".format(x2.name, sys.argv[2])
        os.system(command)

x.close()
# with the first call we can get the meld
# with the second one, we safe the diff into diff_qst_month.txt -> if this file has a size of 0 the xml is correct
# os.system("meld {0} {1}".format(sys.argv[2], sys.argv[3]))
os.system("diff {0} {1} > diff_qst_month.txt".format(sys.argv[2], sys.argv[3]))

