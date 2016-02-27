# Imports

import support_yaemrs as sf
from patient_yaemrs import PatientObject

import asset
import ruamel.yaml as ryaml
import pathlib
import os
import configparser
from pprint import pprint
from pudb import set_trace
import sys
from subprocess import call

# Class Definitions
class PatientDB:
    """The PatientDB class"""

    def __init__(self):

        # Load the full system configuration (Database and Patient)
        # into self.config, which is a OrderedDict
        self.config = self.__load_config()

        # this is the configuration for the "DATABASE" struture
        self.config_DB = self.config["DATABASE"]

        # this is the configuration for the "PATIENT" structure
        self.config_patient = self.config["PATIENT"]

        # using the database configuration, setup object attributes.
        for key in self.config_DB:
            setattr(self, key, self.config_DB[key])

        # at this point the DB object has attributes from the "DATABASE"
        # section of the .ini file.
        # the "PATIENT" setion will be available to patient objects
        # instantiated from this database object, via the
        # self.config_patient attribute

        # finally do a verification of the paths loaded from the config.ini
        # file

        #for key in self.config_DB:
        #    print(key + ": " + getattr(self, key))

        #sys.exit()


        if self.__verify_DB_img() is False:
            raise FileNotFoundError

        if self.__verify_DB_root() is False:
            raise FileNotFoundError

        self.__verify_DB_paths()

    # PRIVATE METHODS GO HERE

    def __load_config(self):
        """Returns the configuration as specified in the project's
        config.ini file.
        The returned object is a configparser.Parser object which
        is essentially an OrderedDict() with subsections with for each
        major section in the .ini file.
        """

        # initialize a configuration parser
        # the configparser.ExtendedInterpolation option allows the
        # values of one section of the .ini file to be referenced in other
        # sections.
        ini_parser = configparser.ConfigParser(
            interpolation=configparser.ExtendedInterpolation())

        # asset.load just gives us a reference to the config.ini file
        # which is situtated in this program's directory
        ini_filename = asset.load("Yaemrs:config/config.ini").filename

        # load the parser with data from the config file
        ini_parser.read(ini_filename)

        # this part fixes the problem when the directories in the
        # config.ini file are preceded with a ~ (shortcut for home)
        # it calls __expand_path to expand the ~ to the value of the
        # home directory of user.
        # -- limitation  = assumes a depth of 2 to the dictionary
        for key in ini_parser:
            for subkey in ini_parser[key]:
                subval = ini_parser[key][subkey]
                ini_parser[key][subkey] = str(self.__expand_path(subval))

        return ini_parser

    def __expand_path(self, the_path):
        return pathlib.Path(the_path).expanduser()

    def __verify_DB_root(self):
        """Verifies for existence of the database root directory."""
        #print(self.db_root_dir)

        the_path = self.__expand_path(self.db_root_dir)
        self.db_root_dir = the_path
        #print(self.db_root_dir)
        #input(the_path)
        if the_path.exists():
            return True
        else:
            print(str(the_path) + ": does not exist")
            return False

    def __load_DB_img(self):
        """Load/mount the database image file"""
        the_img = pathlib.Path(self.db_img_file).expanduser()

        the_img_str = str(the_img)
        the_cmd = "hdiutil attach " + the_img_str
        #call(the_


    def __verify_DB_img(self) -> bool:
#        """Verify that the disk img of the database exists as per config.ini
#        Return True if success. False if not"""
#
#        the_img_path = pathlib.Path(self.db_img_file).expanduser()
#
#        if the_img_path.exists():
#            return True
#        else:
#            print("the DB img : " + str(the_img_path) + " not found")
#            return False
        return True

    def __verify_DB_paths(self):
        """Verify that the DB paths exist and
        that they are writable only for the user (chmod 700)
        """

        list_of_dirs = [directory.strip() for directory in
                       self.config_DB["db_dirs"].split(",")]

        for reference in list_of_dirs:
            self.__test_and_create_path(getattr(self, reference))
        return

    def __test_and_create_path(self, path_string):
        """Test if path exists, if not then create it with
        the proper mode (700)
        TODO: creation and logging
        """

        the_path = pathlib.Path(path_string).expanduser()

        if the_path.exists() is False:
            the_path.mkdir(mode=0o700)

    def __make_patient_UID(self, fname: str, lname: str,
                           HIN: str, chart: str, clinic: str) -> str:
        """Build the UID string for the patient."""

        def __check_name(name: str):
            """Capitalize first letter of fname and lname
            and make sure it is not empty
            """
            if len(name) == 0:
                raise ValueError("Value cannot be null_string ''")
            elif name.isalpha() is False:
                raise ValueError("Value cannot contain non alpha chars")
            else:
                # uppercase the first character
                name = name[0].upper() + name[1:]
            return name

        # Placeholder for our new patient entry
        new_patient_UID = str()

        # check the names for validity
        new_patient_UID += (__check_name(lname) + "." +
                            __check_name(fname) + ".")

        # uppercase the HIN
        HIN = HIN.upper()

        # do a validity check on HIN
        HIN_test, error_msg = sf.validate_HIN_structure(HIN)

        if HIN_test is False:
            raise ValueError("HIN validation error: " + error_msg)
        else:
            new_patient_UID += HIN + "."

        # Add the chartnumber and the clinic name

        # check for chart number validity
        if chart.isdigit() is False:
            raise ValueError("Chart number can contain only digits")

        # check for clinic validity
        if clinic.upper() not in self.clinics.split(","):
            raise ValueError("Clinic name is invalid")

        new_patient_UID += chart + "." + clinic.upper()

        return new_patient_UID

    def __make_patient_dir(self, patient_UID: str) -> str:
        """create the patient directory.
        patient_UID does not contain the full path to where
        we must create it, so it has to be added
        TODO ... use the data in the "PATIENT" section of the config
        information to setup the patient directories.
        """
        full_path_patient_UID = str(self.__expand_path(self.patients_data_dir))\
                                + "/" + patient_UID

        try:
            os.mkdir(full_path_patient_UID, mode=0o700)
        except Exception as mkdir_error:
            if isinstance(mkdir_error, FileExistsError):
                # trying to mkdir an existing directory will raise this erorr
                # but will NOT be handled.
                pass
            else:
                # some OTHER error than FileExistsError
                raise mkdir_error
        return full_path_patient_UID

    def __chart_clinic_combo_unique(self, patient_UID: str) -> bool:
        """Make sure that the chart and clinic combo do not currently exist
        in the database.
        """
        search_pattern = ".".join(patient_UID.split(".")[-2:])
        if search_pattern in self.__chart_clinic_list():
            return False
        else:
            return True

    def __HIN_unique(self, patient_UID: str) -> bool:
        """Make sure that the HIN does not currently exist
        in the database.
        """
        HIN = patient_UID.split(".")[2]

        if HIN in self.__HIN_list():
            return False
        else:
            return True

    def __chart_clinic_list(self) -> list:
        """Return a list containing only the CHART.CLINIC portions of
        the patient_list()
        """
        return [".".join(item.split(".")[-2:]) for item in
               self.patient_list()]

    def __HIN_list(self) -> list:
        """Return a list containing only the HIN numbers of the
        patients in the database"""

        return [item.split(".")[2] for item in self.patient_list()]

    def __verify_patient_UID(self, patient_UID) -> bool:
        """Make some verifications on the patient_UID
        1. that the full patient_UID is unique
        2. that the chart and clinic COMBINATION is unique
        3. that the HIN is unique
        """

        # Check for uniqueness of full UID in patient list
        if patient_UID in self.patient_list():
            raise ValueError(patient_UID + " : is not a unique UID")

        # Check that the chart_and_clinic combination are unique
        if self.__chart_clinic_combo_unique(patient_UID) is False:
            error = ("Chart number and clinic COMBINATION in " +
                     patient_UID + " exists already.")
            raise ValueError(error)

        # Check that the HIN in unique
        if self.__HIN_unique(patient_UID) is False:
            error = ("The HIN in " + patient_UID + " already exists.")
            raise ValueError(error)

        # if we get here it is because the UID seems valid
        return True


    # PUBLIC METHODS GO HERE


    def patient_list(self, pattern: str="*") -> list:
        """Returns a list containing all the patients in the directory defined
        by self.patients_data_dir
        """

        # correct the user supplied pattern to make sure it contains a leading
        # and trailing * (best way to do this is strip off any that may be
        # there and then add more
        pattern = ("*" + pattern.strip("*") + "*").replace("**","*")

        # the expanduser() call just expands any "~" refs in
        # self.patients_data_dir
        path_object = pathlib.Path(self.patients_data_dir).expanduser()

        # this splits the output of find command and removes the last element
        # which is an empty line
        full_path_list = (sf.find(str(path_object), pattern)).split("\n")[:-1]

        filename_list = []

        for directory in full_path_list:
            filename_list.append(pathlib.Path(directory).name)

        filename_list.sort()

        # this is an fugly hack to fix a "FEATURE/BUG" in MacOSX
        # the damn Finder always adds 'DS_Store' files in directories
        # so I have to remove it.

        return [filename for filename in filename_list
                if ("DS_Store".upper() not in filename.upper())]


    def new_patient(self, fname: str, lname: str, HIN: str,
                    chart: str, clinic: str) -> str:
        """Build a new patient in the database

        This is accomplished by making a directory with the proper
        identification and then populating it with the proper files and
        subdirs.
        """
        patient_UID = self.__make_patient_UID(fname=fname, lname=lname,
                                              HIN=HIN, chart=chart,
                                              clinic=clinic)

        # this call will check the patient_UID and throw and error
        # if necessary
        self.__verify_patient_UID(patient_UID)

        # create the patient directory
        patient_path = self.__make_patient_dir(patient_UID)

        # create new patient object with newly created patient_UID
        # but tell the object NOT to load its data because we
        # must populate some files first.
        new_patient_object = PatientObject(patient_UID, self, autoload=False)

        # call _write_default_files on the new patient_object
        new_patient_object._write_default_files()

        # delete our REFERENCE to the patient object (we no longer need it)
        del new_patient_object

        return patient_path


