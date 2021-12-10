#!/bin/sh

# --------------------------------------------------------------------------------
# Runs Viewgen.sh with several parameters.
#
#    Linux: add the name of the pdf-viewer after the -v argument:  ...   -v <myPdfReader>  ...
#             e.g.   ... -v acroread ...
#
#    If there occurs an OutOfMemoryError, add parameter -Xmx512m in Viewgen.bat (view information in file)
#
#    Minimum requirement: Java 11
#
#    Report                   Plugin-Name
#    -------------------------------------------------
#    AHV free persons         AhvFreeReport
#    AHV                      AhvReport
#    AHV proof of insurance   AhvProofOfInsuranceReport
#    FAK                      FakReport
#    FAK detailed             FakDetailedReport
#    UVG                     	UvgReport
#    UVGZ                     UvgzReport
#    KTG                      KtgReport
#    TaxAccounting            TaxReport or TaxAccountingReport
#    Tax at source            QstReport
#    Tax at source result     QstResultReport
#    Statistic                StatisticReport
#    Ownership right detail   ORDReport
#
#
#    Further plugins:
#    Anonymizer, Barcode, Validator
#
#    For plugin usage see Readme.pdf
#
# uncomment line to run example (remove #). Only 1 line at a time should be uncommented.
# --------------------------------------------------------------------------------

echo Generating sample report. Please wait.

# ====================
# Viewgen (default)
# ====================

# -------------------------------------------------------------------------------------------
#	--- Lohnstandard V4.0
# -------------------------------------------------------------------------------------------
# -------Erzeugung Lohnausweis und Anzeige----------------------
sh ./Viewgen.sh  -p TaxAccountingReport -x "testdata/sd20130514/ICHAGCompanyTestSig.xml" -v acroread

# For Mac: you probably don't need to indicate a program. So do this:
# sh ./Viewgen.sh  -p TaxAccountingReport -x "testdata/sd20130514/ICHAGCompanyTestSig.xml" -v



# -------Erzeugung anonymisierter Lohnausweis und Anzeige-------
# sh ./Viewgen.sh  -p TaxAccountingReport -x "testdata/sd20130514/ICHAGCompanyTestSig.xml" -a -v acroread

# -------Nur Validierung----------------------------------------
# sh ./Viewgen.sh -p Validator -x "testdata/ICHAGCompanyTestSig.xml"

# -------Creates a TaxAccountingReport for the 2nd and third person only and shows it----------------------
# sh ./Viewgen.sh -p TaxAccountingReport -x "testdata/sd20130514/COMPLEXCompany.xml" -s 2 -e 3 -v acroread
