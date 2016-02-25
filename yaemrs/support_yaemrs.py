"""
These are support functions for the EMR

A place for functions too general to fit in an object

v0.1: 6.10.2014 added the writeToLog()
"""


from globals_yaemrs import EMR_LOG_FILE, TEMP_DIR
from globals_yaemrs import TEXT_TO_PS, PS_TO_PDF, SYS_PRINT_CMD
import globals_yaemrs as g

from subprocess import call
import datetime
import os
import shutil
import locale
from pydoc import pager as screenPager
from tempfile import NamedTemporaryFile

#from pudb import set_trace
# lots of magic via sh module (makes my life much easier)
from sh import tmux
# import pudb


def obligatory_input(prompt="", times=3):
    """Loop until a non-empty string is input
    or number of times is met (default is 3)"""

    counter = 0
    reply = ""
    while reply == "":
        counter += 1
        print("Counter = ", counter)
        if counter > times: break
        reply = input(prompt)
    return reply

def validate_HIN_structure(HIN: str) -> (bool, str):
    """Returns a tuple. The first value is True or False depending on the value
    of HIN which is the Quebec RAMQ health insurance number.
    Second value of tuple is the error message.

    Valid format is AAAA 1234 5678

    AAAA is a string made of the first 3 chars of the
    patient's last name + the first char of their first name

    1234 5678 are all numbers

    12 is the last 2 years of the date of birth

    34 is the month of birth + sex
        for men 01 (jan) to 12 (dec)
        for women 51 (jan) to 62 (dec)
        (ie month + 50 added for women)

    56 is the date of birth (01 - 31)
    (does not check if right number of days for given month,
     ie more than 29 for february, etc.)

    78 is an administrative value (01 - 99)

    example: Linda Dow, 25 oct 1990 would give
            DOWL 9060 2501 (last 2 digits are adminstrative)

    example: Jack Crane, 15 mai 2003 would give
            CRAJ 0305 1501 (last 2 digits are administrative)
    """

    # test length = 12 characters
    if len(HIN) != 12:
        return (False, "Wrong length (not 12 characters)")

    # test first 4 characters are alpha
    if HIN[0:4].isalpha() is False:
        return (False, "First 4 characters not Alpha")

    # test last 8 characters are numbers
    if HIN[4:].isdigit() is False:
        return (False, "Last 8 characters not Digits")

    # we dont test year of birth because it can be 00-99

    # test month of birth, allowed values are 1 to 12 and
    # 51 to 62
    birth_month = int(HIN[6:8].lstrip("0"))
    if not ((1 <= birth_month <= 12) or (51 <= birth_month <= 62)):
        return (False, "Error in month of birth")

    # test date of birth, allowed values are 1 to 31
    birth_day = int(HIN[8:10].lstrip("0"))
    if not (1 <= birth_day <= 31):
        return (False, "Error in date of birth")

    # we dont test the last 2 digits

    # if we got to here it's because the HIN is valid
    # so return True
    return (True, "")

def clearScreen():
    """
    Call the system command 'clear' to clear the screen.

    I have to use 'call("clear")', because it does not work as expected
    if I import it via the sh module... why ... I don't know."""

    call("clear", shell=True)

def currentDate():
    return datetime.datetime.now().strftime("%d.%m.%Y")

def currentTime():
    return datetime.datetime.now().strftime("%H:%M")

def calculateAge(born_year=1965, born_month=5, born_day=4, hundred=False):
    """
    Return the age in years

    If no values are given, it will return my current age in years.

    Params:
        born_year: (int)
        born_month: (int)
        born_day: (int)

    Return:
        age: (int)

    Note:
        the way it is currently implemented this function handles parameters
        that are passed as strings. It will try and convert them to int.
    """
    today = datetime.date.today()

    if isinstance(born_year, str):
        born_year = int(born_year.lstrip("0"))

    if isinstance(born_month, str):
        born_month = int(born_month.lstrip("0"))

    if isinstance(born_day, str):
        born_day = int(born_day.lstrip("0"))

    if born_year < 100:
        if born_year + 2000 > today.year:
            born_year += 1900
        else:
            born_year += 2000

#    set_trace()

    adjust = ((today.month, today.day) < (born_month, born_day))

    age = today.year - born_year - adjust

    return age

def doesFileExist(fileName):
    return os.path.isfile(fileName)

def isDateFormatValid(theDateString: str) -> bool:
    """
    This function verifies that the format and contents of "date" are valid

    This means that it complies with the internal representation of dates,
    which is: dd.mm.yyyy

    dd: is a value between 1 and 31 (dependent of days in month)
    mm: is a value between 1 and 12
    yyyy: is the year

    Requires:
        import datetime

    Param:
        theDataString: (str) the date to validate

    Return:
        Bool True/False
    """

    try:
        datetime.datetime.strptime(theDateString, '%d.%m.%Y')

    except ValueError:
        return False

    else:
        return True

def writeToLog(userMessage="", logFile=EMR_LOG_FILE):
    """
    Append a message to the log file designated by EMR_LOG_FILE (as default
    file) otherwise use the supplied filename.

    Param:
        userMessage:  (str)
            the message to be written

        logFile: (str)
            the name of the log file to write to.
            (defaults to EMR_LOG_FILE)
    """

    if userMessage != "":
        logMessage = (currentDate() + " @ " + currentTime() +
                      " :: " + userMessage + "\n")

        with open(logFile, "a") as fileHandle:
            fileHandle.write(logMessage)

def readFromLog(logFile=EMR_LOG_FILE):
    """
    Read (page to screen) the program's log file (EMR_LOG_FILE)

    Param:
        logFile: (str) defaults to EMR_LOG_FILE

    Requires:
        pager from pydoc
    """

    with open(logFile) as theFileHandle:
        screenPager(theFileHandle.read())

def touchFile(fname):
    """
    Function will "touch" (in Unix parlance) a file
    and thus update it's last access time, or create it if non-existant.

    Param:
        fname: (str) the name of the file to 'touch'

    Requires:
        import os

    Note:
        this function could be replaced with sh.touch (maybe not as portable?)
    """

    open(fname, 'a').close()
    os.utime(fname, None)

def listFiles(path):
    """
    Returns a list of all files in folder 'path'

    Param:
        path: (str) the path from which we want the list.

    Requires:
        import os

    Note:
        the list of filenames will not have the path prepended.
        the list will not contain directories.
    """

    files = []
    for name in os.listdir(path):
        if os.path.isfile(os.path.join(path, name)):
            files.append(name)
    return files

def moveFiles(sourcePath, destPath, fileList):
    """
    Move all files in list fileList from sourcePath to destPath

    Param:
        sourcePath: The folder/directory FROM which to move files

        destPath: The folder/directory TO which to move files

        fileList: The list of files to move

    Requires:
        import os
        import shutil
    """

    # first check the sourcePath and destPath for existence
    if os.path.isdir(sourcePath) and os.path.isdir(destPath):

        # make sure there is only 1 leading and trailing / on the paths
        # then add the leading and trailing / to them
        sourcePath = "/" + sourcePath.strip('/') + "/"
        destPath = "/" + destPath.strip('/') + "/"

        for file in fileList:
            sourceFile = sourcePath + file
            destFile = destPath + file
            shutil.move(sourceFile, destFile)

def changeTMUXWindowName(newName="NewName"):
    """
    Wrapper around the tmux program

    tmux is imported by sh.py
    (sh.py makes me happy.)"""

    tmux("rename-window", newName)

def NoneToEmptyString(value):
    """
    Convert None value to ""

    Param:
        value (str)

    Return:
        an empty string "" if value is None,
        otherwise returns str(value) (converted to string)
    """
    if value is None: return ""
    else: return str(value)

def CheckContactFile(thePath, ptName, theExtension):
    if ptName == "":
        return

    theParts = ptName.split(".")
    lName = theParts[0]
    fName = theParts[1]
    UID = theParts[2]
    cNumber = theParts[3]
    theClinic = theParts[4]

    theFile = thePath + ptName + theExtension

    newOutputString = ""
    try:
        with open(theFile, 'r') as fileHandle:
            theData = fileHandle.read()

        if len(theData.strip()) == 0:

            newOutputString = ("NOM: " + lName + "\n" +
                               "PRENOM: " + fName + "\n" +
                               "NAM: " + UID + "\n" +
                               "EXP: " + "\n" +
                               "CLINIQUE: " + theClinic + "\n" +
                               theClinic.upper() + ": " + cNumber + "\n")
        else:
            theData = theData.replace(":", ": ")
            theData = theData.replace(":  ", ": ")
            theData = theData.split("\n")

            for line in theData:
                if "CONTACT" in line.upper():
                    theData.remove(line)

            for line in theData:
                newOutputString += line.strip() + "\n"

        print(newOutputString)
        with open(theFile, 'w') as newOutputFileHandle:
            newOutputFileHandle.write(newOutputString)

    except FileNotFoundError:
        # this part fixes when the file is not found
        theString = ("NOM: " + lName + "\n" +
                     "PRENOM: " + fName + "\n" +
                     "NAM: " + UID + "\n" +
                     "EXP: " + "\n" +
                     "CLINIQUE: " + theClinic + "\n" +
                     theClinic.upper() + ": " + cNumber + "\n")

        with open(theFile, 'w') as newFileHandle:
            newFileHandle.write(theString)

def pad_string(string:str, N_th:int=5, pad:str=" ") -> str:
    """
    Insert a pad character every N_th characters in the string.
    if N_th is < 1 returns the original string

    Param:
        string: (str) string to work on
        N_th: (int) interval between pad insertions
        pad: (str) the character to insert
    """
    if N_th < 1: return string
    else:
        return (pad.join(string[i:i+N_th]
                for i in range(0, len(string), N_th)))

def convertPostScriptToPDF(PostScript_Filename):
    """
    Convert PostScript file to PDF

    Param:
        PostScript_Filename: (str)
            name of the postscript file to convert

    Return: (str)
        the NAME of the output PDF file

    Note:
        the 'ps2pdf' system command must be on the $PATH

        A NamedTemporaryFile is created with dir option set to
        TEMP_DIR which points to a directory on the encrypted disk image.
    """

    if not doesFileExist(PostScript_Filename):
        return False

    # create out PDF output file (call returns a file HANDLE)
    #
    output_FileHandle = NamedTemporaryFile(dir=TEMP_DIR, delete=False)

    # now get the NAME of the file
    #
    PDF_Filename = output_FileHandle.name

    conversion_CMD = PS_TO_PDF
    conversion_CMD += PostScript_Filename + " "
    conversion_CMD += PDF_Filename

    call(conversion_CMD, shell=True)

    return PDF_Filename

def convertTextFileToPDF(text_Filename):
    """
    Combine text to PostScript and then PostScript to PDF

    Function returns the NAME of the ouput PDF file.i
    """

    return convertPostScriptToPDF(convertTextFileToPostScript(text_Filename))

def printTextFile(text_Filename):
    """Print a text file to the system printer on MacOSX

    text_Filename is output to PDF and then the PDF is
    finally printed via the global SYS_PRINT_CMD command

    Here the SYS_PRINT_CMD is set in the Globals.py file

    This function returns True if everthing went as planned...."""

    if not doesFileExist(text_Filename):
        return False

    # Hardcoded path is BAD!!!!!! I know
    printCMD = SYS_PRINT_CMD

    #
    generatedPDF_Filename = convertTextFileToPDF(text_Filename)

    if generatedPDF_Filename is False:
        return False
    else:
        printCMD += generatedPDF_Filename
        call(printCMD, shell=True)
        return True

def sendStringToPrinter(outputString=""):
    """Function to print a string to the default system printer
    Tested only on OSX. This function ultimately uses the 'paps'
    text to PostScript converter, which must be installed and available
    on the $PATH variable for this to work.
    Using 'paps' allows for UTF-8 strings to be correctly printed.
    As with other printing functions in this file, the data is written
    to a 'NamedTemporaryFile' which is NOT deleted after use.
    Security is assured by setting the 'dir' value to a temporary directory
    that is on the encrypted disk image."""

    if outputString == "":
        return False
    else:
        outputData = bytes(outputString, 'UTF-8')

    with NamedTemporaryFile(dir=TEMP_DIR, delete=False) as fh:

        outputFilename = fh.name

        fh.write(outputData)
        fh.flush()
        # why do I have to do this ????? the context manager should just close
        # it.

    printTextFile(outputFilename)

def set_our_locale():
    """
    Function to set the locale for use with datetime etc functions.
    The value is set according to the on in the GLOBALS file
    """
    locale.setlocale(locale.LC_TIME, g.LOCALE)

def str_to_list(the_string: str, separator=",") -> list:
    """Convert a string to a list. String is split at 'separator' and parts are
    stripped of leading and trailing spaces.
    Separator is "," (comma) by default.
    Passing the function an empty string "" returns an empty list []

    Param:
        the_string: (str) the string to convert
        separator: (str) "," by default
    Returns:
        list: a list of parts of the original string, split at separator."""

    if the_string == "":
        return []
    else:
        return [item.strip() for item in the_string.split(separator)]

def pickFromList(theListToPickFrom):
    """This function is an ugly way to show a list with a numeric choice and then return
    the value selected by the user.
    It will first reverse the list because I am using it mostly with directory listings
    which have the newest file at the bottom.
    """

    theListReversed = theListToPickFrom[::-1]

    if len(theListReversed) > 0:
        for index, item in enumerate(theListReversed, start=1):
            print(index, ":", item)
    else:
        return("")

    while True:                                                     # Loop
        try:
            choice = input("Your choice: ")                         # Get user's choice

            if choice == "":                                        # a carriage return gets the first one.
                choice = 1

            elif choice.upper() in ('X','Q','R'):
                return("")                                          # user quits return empty string

            else:
                choice = int(choice)

        except ValueError:                                          # if it not a numeric choice → ValueError
            print("Invalid choice (non-numeric)")

        else:                                                       # we're OK
            if choice < 1 or choice > len(theListReversed):       # make sure that it is within bounds
                print("Invalid choice (out-of-bounds)")
            else:
                return(theListReversed[int(choice) -1])            # now we have the one we want


