# FILE: Globals_module.py

# Main CONSTANTS are defined here.

# Version number
__version__ = "0.02alpha"   # 1.10.2014 fixed note clipping bug
__version__ = "0.03alpha"   # 3.10.2014 changed the names of the files
__version__ = "0.04alpha"   # 6.10.2014 minor fix to first line of the file
__version__ = "0.05alpha"   # 17.11.2014
__version__ = "0.10beta"    # 5.1.2015
__version__ = "0.11beta"    # 07.04.2015
import os
from collections import OrderedDict

# set out locale to french Canada
# LOCALE = "fr_CA"
#LOCALE = "en_CA"     # if we wanted english stuff.
LOCALE = "en_ca"

NEWLINE = "\n"
MY_SIGNATURE = "Michael LONGVAL, MD"

"""Database structure:
    - Clinic/: Main directory where everything is stored
        - Patients/: where the patient data is stored
            - LastName.FirstName.UID.ChartNumber.Clinic/:  the Patient datastore
                - atcd: the patient's atcd file (history file)
                - billing: the billing file for the patient
                - contact: the patient's contact information
                - meds: the patient's medication file
                - docs/: directory where scans and other documents are stored
                - notes/: the directory where the patients notes are stored
        - Results/: not sure what goes here.....  #FIXME
        - Billing/: where the finalized bills that are sent to the billing
          agency are stored
        - Program/: where the python scripts are stored
"""

# file types
DIRTYPE     = "directory"
FILETYPE    = "file"


# Where to find the data:
#HOME                = os.environ['HOME']
HOME                = "/Volumes"

#CLINIC              = "/TestClinic/"    # <=== used for testing purposes
CLINIC              = "/ClinicalData/"        # <=== REAL WORLD working directory

PREFIX              = HOME + CLINIC

TEMP_DIR            = PREFIX + "temp/" # temporary files stored here

PATIENT_DATA        = PREFIX + "patients/"
RESULTS_DATA        = PREFIX + "results/"
BILLING_DATA        = PREFIX + "billing/"
OTHER_DATA          = PREFIX + "other/"
APPOINTMENT_DATA    = PREFIX + "appointments/"
EMR_LOG_FILE        = PREFIX + ".logfile"  # used for user suggestions etc
SYSTEM_LOG_FILE     = PREFIX + ".system_log"  # used by the system to log events

CLINIC_SCANS        = HOME + "/Desktop/ClinicScans"     # <=== where we pick up
                                                        # scanned documents by
                                                        # default

CURRENT_CLINIC      = PREFIX + "CLINIC.locale"   # used by the
                                                 # getCurrentClinicByLocation
                                                 # function

DATABASE_STRUCTURE = [
    (HOME,DIRTYPE),
    (PREFIX,DIRTYPE),
    (PATIENT_DATA,DIRTYPE),
    (RESULTS_DATA,DIRTYPE),
    (BILLING_DATA,DIRTYPE),
    (OTHER_DATA,DIRTYPE),
    (APPOINTMENT_DATA,DIRTYPE),
    (EMR_LOG_FILE,FILETYPE),
    (SYSTEM_LOG_FILE,FILETYPE)]


# Directories in the PATIENT directorys
NOTE_DATA_SUFFIX = "/notes/"
DOCS_DATA_SUFFIX = "/docs/"

# Files in PATIENT directorys
PATIENT_BILLING_FILE    = "/billing"
PATIENT_MEDS_FILE       = "/meds.yaml"
PATIENT_ATCD_FILE       = "/atcd.yaml"
PATIENT_CONTACT_FILE    = "/contact.yaml"
PATIENT_VCODES_FILE     = "/vcodes.yaml"

# the Record Format for a Patient
PT_MAIN     = PATIENT_DATA + "{0}"
PT_NOTES    = PT_MAIN + NOTE_DATA_SUFFIX
PT_DOCS     = PT_MAIN + DOCS_DATA_SUFFIX
PT_BILL     = PT_MAIN + PATIENT_BILLING_FILE
PT_MEDS     = PT_MAIN + PATIENT_MEDS_FILE
PT_ATCD     = PT_MAIN + PATIENT_ATCD_FILE
PT_CONTACT  = PT_MAIN + PATIENT_CONTACT_FILE

PATIENT_RECORD_FORMAT = [(PT_MAIN,DIRTYPE),
                         (PT_NOTES,DIRTYPE),
                         (PT_DOCS,DIRTYPE),
                         (PT_BILL,FILETYPE),
                         (PT_MEDS,FILETYPE),
                         (PT_ATCD,FILETYPE)]

# Basic data structures in Data files
ATCD_FORM = ("ANTECEDANTS: \n" +
             "    FAMI: \n" +
             "    PERE: \n" +
             "    MERE: \n" +
             "    PERS: \n" +
             "    ACTV: \n")

MEDS_FORM = "MEDS:\n-\n"

CONTACT_FORM = ("NOM: {lname}\n" +
                "PRENOM: {fname}\n" +
                "NAM: {nam}\n" +
                "EXP: {exp}\n" +
                "CLINIQUE: {clinique}\n" +
                "{clinique}: {dossier}\n" +
                "TEL: \n" +
                "CEL: \n" +
                "EMAIL: \n" +
                "PHTEL: \n" +
                "PHFAX: \n" +
                "PHNOM: \n" +
                "ADRESSE: \n" +
                "VILLE: \n" +
                "PROVINCE: \n" +
                "PAYS: \n" +
                "CODEPOSTAL: \n"
               )


CONTACT_HEAD = "CONTACT:"
CONTACT_DICT = OrderedDict([('NOM', None),
                            ('PRENOM', None),
                            ('NAM', None),
                            ('EXP', None),
                            ('CLINIQUE', None),
                            ('CMRF', None),
                            ('CHUS', None),
                            ('TEL', None),
                            ('CEL', None),
                            ('EMAIL',None),
                            ('ADRESSE',None),
                            ('VILLE', None),
                            ('PROVINCE', None),
                            ('PAYS', None),
                            ('CODEPOSTAL', None),
                            ('PHTEL', None),
                            ('PHFAX', None),
                            ('PHNOM', None)
                            ])

NOTE_FORM = ("Date: {date}\n" +
             "Nom:  {lname}.{fname}\n" +
             "{clinique}: {dossier}\n\n\n\n\n" +
             "Histoire: |\n\n" +
             "Examen: |\n\n" +
             "Impression:\n\n" +
             "Conduite:\n" +
             "Revoir: \n\n" +
             "Dx: \n" +
             "Code: \n\n\n" +
             "sig: Michael LONGVAL, MD\n"
            )


PHONECALL_FORM = ("Date: {date}" + NEWLINE +
                  "Nom: {lname}.{fname}" + NEWLINE +
                  "{clinique}: {dossier}" + 5* NEWLINE +
                  "RC: Téléphone du patient" + 2* NEWLINE +
                  "Discussion: " + 2* NEWLINE +
                  "Conduite: " + 2* NEWLINE +
                  "sig: " + MY_SIGNATURE)

# These are the options for the Clinic or Hospital under which
# the patient data is entered.
# CHUS = Centre Hospitalier Universitaire de Sherbrooke
# CMRF = Clinique Medicale Rock Forest
# CMND = Clinique Medicale Notre-Dame
CLINIC_ID = ("CHUS", "CMRF", "CMND")


# Billing options

BILLING_DICT = OrderedDict([ ('1',('Examen Ordinaire','ExamenOrdinaire')),
                              ('2',('Examen Complet','ExamenComplet')),
                              ('3',('Examen Complet Majeur','ExamenCompletMajeur')),
                              ('4',('Examen Psychiatrique Ordiaire','ExPsyOrdinaire')),
                              ('5',('Examen Psychiatrique Complet','ExPsyComplet')),
                              ('6',('Therapie de Support 30minutes','TherapieSupport30min')),
                              ('7',('Examen Psy Ordinaire + 30minutes support','ExPsyOrd+30min')),
                              ('8',('8871','Code8871')),
                              ('9',('8879','Code8879')),
                              ('10',('Aucun','xxxx'))
                              ])


# Structure of the MedicationObject

MEDICATION_OBJECT_MEMBERS = ["NAME", "DOSE", "FREQ", "MOD1", "COMMENT"]

# Choice of pager
#PAGER = "less "
#PAGER = "more "
PAGER = "most "

# Choice of editor
#
#EDITOR = "pico "
#EDITOR = "vim "
#VIMCONFIG =
#EDITOR = "vim -u /Users/doc/EMR/config/vimrc "
#EDITOR = "vim -u $HOME/EMR/config/vimrc + "    # used this way will open first file AT THE END OF FILE
EDITOR = "vim -p + "    # used this way will open first file AT THE END OF FILE

# Choice of interface language
LANGUAGE = "ENGLISH"
#LANGUAGE = "FRANCAIS"

# path to terminal multiplexer
TMUX="/usr/local/bin/tmux "

# our favorite file python file browser
FILE_BROWSER="ranger "

# Setup the globals needed to print
# We require a text to Postscript converter
# Here 'paps' fits the bill nicely and is UTF-8 compliant

TEXT_TO_PS = "paps --paper=letter "

# We require a PostScript to PDF converter
#
PS_TO_PDF = "ps2pdf "

# We require a command to print
# This is the lpr command on MacOSX
#
SYS_PRINT_CMD  = "lpr -h "







