@echo off

REM --------------------------------------------------------------------------------
REM Runs Viewgen.bat with several parameters.
REM
REM    Linux: add the name of the pdf-viewer after the -v argument:  ...   -v <myPdfReader>  ...
REM             e.g.   ... -v acroread ...
REM    Solve problem with blanks in path: "\"C:\\Program Files\Adobe\Acrobat\Acrobat.exe\""
REM    If there occurs an OutOfMemoryError, add parameter -Xmx512m in Viewgen.bat (view information in file)
REM
REM    Minimum requirement: Java 11
REM
REM    Report                   Plugin-Name
REM    -------------------------------------------------
REM    AHV free persons         AhvFreeReport
REM    AHV                      AhvReport
REM    AHV proof of insurance   AhvProofOfInsuranceReport
REM    FAK                      FakReport
REM    FAK detailed             FakDetailedReport
REM    UVG                     	UvgReport
REM    UVGZ                     UvgzReport
REM    KTG                      KtgReport
REM    TaxAccounting            TaxReport or TaxAccountingReport
REM    Tax at source            QstReport
REM    Tax at source result     QstResultReport
REM    Statistic                StatisticReport
REM    Ownership right detail   ORDReport
REM
REM
REM    Further plugins:
REM    Anonymizer, Barcode, Validator
REM
REM    For plugin usage see Readme.pdf
REM
REM uncomment line to run example (remove REM). Only 1 line at a time should be uncommented.
REM --------------------------------------------------------------------------------

@echo Generating sample report. Please wait.

REM ====================
REM Viewgen (default)
REM ====================

REM -------------------------------------------------------------------------------------------
REM	--- Lohnstandard V4.0
REM -------------------------------------------------------------------------------------------
REM -------Creates a TaxAccountingReport----------------------
Viewgen.bat -p TaxAccountingReport -x testdata\sd20130514\ICHAGCompanyTestSig.xml -v

REM -------Creates a v and shows it----------------------
REM Viewgen.bat -p TaxAccountingReport -x testdata\sd20130514\ICHAGCompanyTestSig.xml -v

REM -------Creates an anomysized TaxAccountingReport and shows it-------
REM Viewgen.bat -p TaxAccountingReport -x testdata\sd20130514\ICHAGCompanyTestSig.xml -v   -a

REM -------Validation and Signature Check only - no creation of a salary certificate------------
REM Viewgen.bat -p Validator -x testdata\sd20130514\ICHAGCompanyTestSig.xml

REM -------Creates a TaxAccountingReport for the 2nd and third person only and shows it----------------------
REM Viewgen.bat -p TaxAccountingReport -x testdata\sd20130514\COMPLEXCompany.xml -s 2 -e 3 -v


