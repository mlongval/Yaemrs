# Imports
import ruamel.yaml as yaml
import support_yaemrs as s
import pathlib
from datetime import datetime
import subprocess
import os.path
from collections import OrderedDict

# Currently unused imports
from pudb import set_trace
import asset
from pprint import pprint

class PatientObject():
    """
    Object representing patient data contained in the patient_UID
    data store.

    The data is stored as an OrderedDict and is accessed by _data member of
    the class.
    (I tried using a version of this class where the class was itself an
    instance of the OrderedDict class, but I was having some strange
    problems, do I decided to just make the class an object and that the
    data would be accessed as a sub-member.)

    Args:
        patient_UID (str) → the patient identifier returned by the
        y_database.PatientDatabase

    Methods:

    Attributes:
        _data (OrderedDict) → class data store
    """

    # CLASS VARIABLES GO HERE
    patient_UID = None
    DB_id = None

    # INITIALIZERS FOR OBJECT AND PRIVATE METHODS GO HERE

    def __init__(self, patient_UID, DB_id, autoload=True):

        # INSTANCE VARIABLES GO HERE

        # patient_UID is a str(), the UID of this object
        self.patient_UID = patient_UID

        # DB_id is object of type PatientDB(), the reference to the calling DB
        self.DB_id = DB_id

        # copy the DB configuration into self
        self.config_DB = self.DB_id.config_DB

        self.config_patient = self.DB_id.config["PATIENT"]

        # build object (self) attributes using DB description (self.config_DB)
        if self.DB_id is not None:
            for key in self.config_DB:
                setattr(self, key, self.config_DB[key])

        if self.patient_UID is not None:
            for key in self.config_patient:
                # DEBUG
                # print(key)
                setattr(self, key,
                        self.config_patient[key].format(self.patient_UID))

        self.meds_field_name_list = [field_name.strip() for field_name in
                                     self.meds_field_names.split(",")]

        self.billing_field_name_list = [field_name.strip() for field_name in
                                        self.billing_field_names.split(",")]

        if autoload is True:
            #print("autoloading...")
            # _data is the objects datastore
            self._data = OrderedDict()

            # verify the paths
            #print("verifying dirs")
            self.__verify_dirs()

            # verify files
            #print("verifying files")
            self.__verify_files()

            # _errors is a list of errors encountered during loading of data
            self._errors = list()

            # calling _load() will set self's dictionary structure
            # use autoload = False to prevent the object from automatically
            # populating itself.
            #print("calling _load")
            self._load()

        return          #  end def __init__

    def __verify_dirs(self):
        """Convert self.config_patient["pt_dirs"] (which is a string) into
        a list. Then iterate over it and call __test_and_create_dir on each
        element.
        """
        # this part does the conversion from a string to a list
        dir_list = self.config_patient["pt_dirs"].replace(" ","").split(",")

        for ref in dir_list:
            self.__test_and_create_dir(getattr(self, ref))
        return

    def __verify_files(self):
        file_list = self.config_patient["pt_files"].replace(" ","").split(",")

        for ref in file_list:
            self.__test_and_create_file(getattr(self, ref))
        return

    def __test_and_create_dir(self, path_string):
        the_path = pathlib.Path(path_string).expanduser()
        if the_path.exists() is False:
            the_path.mkdir(mode=0o700)
        return

    def __test_and_create_file(self, path_string):
        the_path = pathlib.Path(path_string).expanduser()
        if the_path.exists() is False:
            the_path.touch(mode=0o700)
        return

    def _load(self):
        """Call the data loading methods."""
        #set_trace()
        self._load_contact()
        self._load_antecedants()
        self._load_medications()
        self._load_notes()
        return

    def _load_contact(self):
        """load contact data."""
        try:
            # attempt to load with yaml loader
            with open(self.pt_contact_file, 'r') as file_handle:
                self._data["CONTACT"] = yaml.load(file_handle,
                                                  yaml.RoundTripLoader)
        except:
            # the file was not in a valid yaml format
            # for the contact file data this should be very rare.
            # Since contact data that is not in yaml format is useless for us
            # we raise an error and fail miserably.
            raise yaml.YAMLError
        return

    def _load_antecedants(self):
        """load antecedants data."""
        yaml_data = OrderedDict()    # placeholder for data
        try:
            with open(self.pt_atcd_file, 'r') as file_handle:
                yaml_data = yaml.load(file_handle, yaml.RoundTripLoader)
        except UnicodeDecodeError as e:
            self._errors.append("Probable vim swap file problem. " + str(e))
        except FileNotFoundError as e:
            self._errors.append("Not found: " + str(e))
        except BaseException as e:
            # what is this error for ?
            self._errors.append("Failed to load atcd: " + str(e))
        else:
            if yaml_data is not None:
                self._data["ATCD"] = yaml_data["ANTECEDANTS"]
            else:
                self._errors.append("empty atcd.yaml file")
        return

    def _load_medications(self):
        """load medication data."""
        #set_trace()
        yaml_data = OrderedDict()   # temporary data hold
        try:
            with open(self.pt_meds_file, 'r') as file_handle:
                yaml_data = yaml.load(file_handle, yaml.RoundTripLoader)
            # DEBUG
            # FIXME
            # input("yaml_data type() is : " + str(type(yaml_data)))
        except Exception as e:
            self._errors.append("error loading meds: " + str(e))
        else:
            if yaml_data["MEDS"] is not None:
                self._data["MEDS"] = yaml_data["MEDS"]
            else:
                self._data["MEDS"] = None
                self._errors.append("empty meds.yaml file")
        return

    def _get_list_of_notes(self):
        """return a list of all notes for this patient."""
        in_list = s.listFiles(self.pt_notes_dir)
        out_list = list()
        for a_file in in_list:
            out_list.append(self.pt_notes_dir + "/" + a_file)
        return out_list

    def _load_notes(self):
        """load all the notes for this patient."""

        def _load_one_note(self, note_path):
            """Load one note using 'note_path'"""
            the_note = OrderedDict()
            the_note["PATH"] = note_path
            the_note["YAML"] = True
            the_note["NOTE"] = ""
            try:
                with open(note_path, 'r') as file_handle:
                    the_note["NOTE"] = yaml.load(file_handle,
                                                 yaml.RoundTripLoader)
            except UnicodeDecodeError as e:
                self._errors.append("Probable vim swap file problem. " + str(e))
            except:
                self._errors.append("Non-YAML note.")
                with open(note_path, 'r') as file_handle:
                    the_note["NOTE"] = file_handle.read()
                    the_note["YAML"] = False
            return the_note

        all_notes = OrderedDict()

        list_of_notes = self._get_list_of_notes()

        for note in list_of_notes:
            note_name = note.split("/")[-1:][0]
            all_notes.update({note_name: _load_one_note(self, note)})

        self._data["NOTES"] = all_notes
        return

    def _write_default_files(self):
        """Write default file contents for contact.yaml, atcd.yaml and
        meds.yaml files"""
        self._write_default_contact_file()
        self._write_default_atcd_file()
        self._write_default_meds_file()
        return

    def _write_default_contact_file(self):
        """Write the default values for contact file"""

        # get correct path to the contact file
        contact_path = pathlib.Path(self.pt_contact_file)

        # get the field names as defined in config.ini file
        field_names = self.config_patient["contact_field_names"]

        # build the contact file skeleton
        data_to_write = ("".join([item + ": \n"
            for item in field_names.replace(" ","").split(",")]))

        # add basic contact data from UID to fields in this file
        lname, fname, hin, chart, clinic = self.patient_UID.split(".")

        # this is an ugly kludge !!!!
        basic_contact_fieldnames = self.config_patient["UID_field_parts"]


        # check if file exists and if not write the file with default data
        if contact_path.exists():
            print("cannot overwrite existing file")
        else:
            with open(self.pt_contact_file, 'w') as fhandle:
                fhandle.write(data_to_write)
        return

    def _write_default_atcd_file(self):
        """Write the default values for atcd file"""
        atcd_path = pathlib.Path(self.pt_atcd_file)
        field_names = self.config_patient["atcd_field_names"]
        data_to_write = (self.atcd_file_header + ":\n" +
            "".join(["    " + item + ":\n"
            for item in field_names.replace(" ","").split(",")]))

        if atcd_path.exists():
            input("cannot overwrite existing atcd file")
        else:
            with open(self.pt_atcd_file, 'w') as fhandle:
                fhandle.write(data_to_write)
        return

    def _write_default_meds_file(self):
        """Write the header for the meds file"""
        meds_path = pathlib.Path(self.pt_meds_file)
        data_to_write = self.meds_file_header + ":\n"

        if meds_path.exists():
            input("Cannot overwrite existing meds files.")
        else:
            with open(self.pt_meds_file, 'w') as fhandle:
                fhandle.write(data_to_write)
        return

    # PUBLIC OBJECT METHODS GO HERE

    def date_of_birth(self, format="short"):
        """
        Cludgy function to return the date of birth of a patient
        it assumes (probably at some point incorrectly),
        that nobody is older than 100.
        one way to get around this is to have a dob field in the
        contacts file that would be able to override the value that is
        calculated from the import hin
        """
        # define what formats we will return in strftime format
        short_format_str = "%y.%m.%d"
        long_format_str = "%-d %b %y"
        full_format_str = "%a, %-d %b %y"

        # set the format to use of the above ones
        if format.lower() == "long":
            format_str = long_format_str

        elif format.lower() == "full":
            format_str = full_format_str

        else:
            format_str = short_format_str

        # get the current year"
        current_year = datetime.now().year

        # get the dob in the hin
        HIN_dob = self.HIN()[4:10]

        y = int(HIN_dob[:2])   # the year part

        # correct the year
        # here we assume that nobody is 100 or older
        birth_year = y + 2000

        current_year = datetime.now().year

        if birth_year > current_year:
            birth_year = y + 1900

        m = int(HIN_dob[2:4])  # the month part

        # these lines correct for the fact that
        # the hin contains sex info
        # if the value is above 50 the person is a woman.
        if m > 50:
            m -= 50

        d = int(HIN_dob[4:])   # the day part

        # make a datetime with the values we have
        the_date = datetime(year=birth_year, month=m, day=d)

        return the_date.strftime(format_str)

    def exp(self, format="short"):
        """return the expiry date in either long or short
        note that the only valid parameter is long,
        anything else returns the short version."""
        if format.lower() == "long":
            v = str(self._data["CONTACT"]["EXP"])
            d = datetime.strptime(v, "%y%m")
            return d.strftime("%b %y")
        elif format.lower() != "long":
            # this is the default action (as format == "short")
            return str(self._data["CONTACT"]["EXP"])

    def errors(self):
        """returns list of errors that may have occured in object."""
        return self._errors

    def all_paths_list(self):
        """
        return list containing the paths to the different data stores
        """
        r_list = list()

        refs = (self.config_patient["pt_dirs"] + "," +
                self.config_patient["pt_files"])

        references = refs.replace(" ","").split(",")

        for ref in references:
            r_list.append(getattr(self, ref))

        return r_list

    def all_paths(self):
        """
        printable version of self.all_paths_list()
        """
        return "\n".join(self.all_paths_list())

    def atcd_raw_list(self):
        return self._data["ATCD"]

    def atcd_raw_list_pers(self):
        return self.atcd_raw_list()["PERS"]

    def atcd_list_pers(self):
        return (" - " + "\n - ". join(self.atcd_raw_list_pers()))

    def meds_raw_list(self):
        """
        returns the raw yaml data from meds.yaml file
        """
        return self._data["MEDS"]

    def meds_shortform_list(self, **kwargs):
        """
        this method returs a printable/formatted string containing all
        the medications in the patient's meds.yaml file.
        each medication is in "short format" as opposed to the multiline format
        that is in the yaml files.

        args: **kwargs
            sortedlist (False) → returned string will be sorted
            showcomments (True) → returned string will include comments

        notes:
        """
        kwargs.setdefault("sortedlist", False)
        kwargs.setdefault("showcomments", True)

        def med_shortform(med):
            return_str = ""
            # this is not a pretty sequence, but it checks for special cases
            # in the medication
            # → the comment field can be omitted, and if shown then () are added
            # → the name field will call .title() method to capitalize the fist
            # letter of the string

            # here we are using the 'medication_object_members' "template"
            # to get our keys.
            # i could have used the keys in "med" but i sometimes
            # add different keys (like date) that are in some patients yaml
            # files but not all, so to avoid having to handle all the special
            # cases i just stick to the "template" standard fields.

            for key in self.meds_field_name_list:
                return_str += " "

                if key == "COMMENT" and kwargs["showcomments"] is True:
                    return_str += "(" if (key == "COMMENT" and
                                          med[key] is not None) else ""

                    return_str += (med[key] or "")

                    return_str += ")" if (key == "COMMENT" and
                                          med[key] is not None) else ""
                    continue

                elif key == "COMMENT" and kwargs["showcomments"] is False:
                    continue

                elif key == "NAME":
                    # .title() is called to capitalize the "NAME" value
                    # because sometimes I forget to capitalize when I
                    # enter the data
                    return_str += str(med[key]).title()
                    continue

                else:
                    return_str += str(med[key] or "")

            # this line just makes sure that the returned string
            # does not contain double spaces
            return " ".join(return_str.split())

        # Edge-case where the MEDS.yaml file contains a "MEDS:" header
        # but no medications (which will be common...)
        # we exit the method
        if self._data["MEDS"] is None:
            return ""

        short_form_list = list()

        # Normally the yaml.load will give us a "List of Dict"
        # the List is in self._data["MEDS"]
        # and each entry is a Dict "like" structure
        # so here "the_med" is one of these Dict-like stuctures
        for the_med in self._data["MEDS"]:
            # Edge case where the yaml file contains a single "-"
            # character on one line and makes an "empty" Dict
            # → this creates a None type entry which we just ignore
            if the_med is not None:
                short_form_list.append(med_shortform(the_med) + "\n")
                # the above line send the Dict-like structure to the
                # med_shortform function (defined above) which returns a
                # single line version (str) of the Dict-like object
                # The values are appended to a list instead of doing
                # a string concantenation. The final "".join() at return
                # makes the routine faster this way
        if kwargs["sortedlist"] is True:
            short_form_list.sort()

        return (" - " + " - ".join(short_form_list))

    def _validate_HIN(self):
        """
        Verify that the HIN (unique patient identifier is valid)

        The HIN format is 12 characters long:
            4 letters + 8 numbers
            the 4 characters are:
                3 first characters of last name
                1 first character of first name

            the 8 characters are:
                last 2 numbers of birth date year
                2 numbers indicating month of birth date
                    (if the patient is female the value has 50 added to it.
                    so a man born in november has the value 11 here
                    while a woman born in november has the value 51)
                2 numbers indicating day of birth date
                the last 2 numbers are an administrative value to differentiate
                people with possible the same 4 chars, that were born on the
                same date (they can have any value)

        HIN format:

        1234 5678 9012
        FIRL 6505 01xx

        Errors are generated if:
            string length is not 12
            4 first characters don't match name values
            7th character is not 0, 1, 5 or 6
            9th character is not 0, 1, 2 or 3
        """

        error_list = []

        # check the length
        if len(self.HIN()) != 12:
            error_list.append("Length is not 12 chars.")

        # check the first 4 chars for letters only
        if not self.HIN()[:4].isalpha():
            expected_value = (self.last_name()[:3] +
                              self.first_name()[:1]).upper()

            error_list.append("Unexpected first 4 chars,"
                              "expected: {}".format(expected_value))

        if int(self.HIN()[6:7]) not in [0, 1, 5, 6]:
            error_list.append("Unexpected 7th character.")

        if int(self.HIN()[8:9]) not in [0, 1, 2, 3]:
            error_list.append("Unexpected 9th character.")

        return(error_list)

    def __str__(self):
        """Return a string representation of the object."""
        return (self.first_name() + " " +
                self.last_name().upper() + "\n" +
                self.HIN() + "  exp: " + self.exp(format="long") + "\n")

    def edit_info(self):
        """edit the meds, atcd and contact
        files this patient object."""
        editor = self.editor + " "
        files = self.pt_meds_file + " "
        files += self.pt_atcd_file + " "
        files += self.pt_contact_file + " "
        command_string = editor + files
        subprocess.call(command_string, shell=True)
        return

    def new_note(self, filename):
        # filename is a string with format dd.mm.yyyy.note
        # or dd.mm.yyyy.phcall.note

        # build the header for the note
        # contains DATE:, NOM:, CLINIQUE -> prefered clinique based on context
        # and also the chart number for the CLINIQUE context

        # get first 10 chars of filename
        date_string = filename[0:10]

        with open('/home/doc/Clinic/Other/Templates/patient.note','r') as fh:
            basic_note = fh.read()

        note_to_be_written = self.notes_path + "/" + date_string + ".note"

        #DEBUG INFO
        #print("Note will be written to : " + note_to_be_written)
        #print("Note contents: ")

        the_note = basic_note.format(date=date_string,
                lname=self.last_name,
                fname=self.first_name,
                hin=self.HIN,
                clinique= self.clinique,
                dossier= self.chart,
                exp=self.exp(),
                meds=self.meds,
                atcd=self.atcd)



        # check that there is not a note already with the same date.
        if os.path.isfile(note_to_be_written) is False:
            with open(note_to_be_written, 'w') as file_handle:
                file_handle.write(the_note)
        else:
            input("File exists for that date already (Return to continue)")

    def edit_note(self, filename):
        editor = self.editor + " "

        file_to_edit = self.notes_path + "/" + filename
        command_string = editor + file_to_edit
        subprocess.call(command_string, shell=True)

    def edit(self, arg=""):
        """Method to call the editor on patient files."""
        file_list = [fname.strip() for fname in self.pt_files.split(",")]

        input(file_list)

        file_string = ""

        for fname in file_list:
            file_string += getattr(self,fname) + " "

        #print("file_string = " + file_string)
        input()

        command_string = self.editor + " " + file_string
        subprocess.call(command_string, shell=True)

    def patient_note_list(self):
        # return a sorted list of tuples representing the internal
        # self._get_list_of_notes()

        def sort_note_list(n_list):
            """Sorts the list of notes by date."""
            new_list=[]

            for item in n_list:
                #get only the first 10 chars (xx.xx.xxxx) dd.mm.yyyy
                date = item[0:10]

                year = date[6:]
                month = date[3:5]
                day = date[0:2]

                new_list.append((int(year+month+day), item))
                new_list.sort()

            return new_list

        n_path = self.notes_path + "/"

        n_list = []
        for item in self._get_list_of_notes():
            n_list.append(item.replace(n_path, ''))

        new_sorted_list = sort_note_list(n_list)

        return new_sorted_list

    # OBJECT PROPERTIES GO HERE

    @property
    def note_list(self):
        return self.patient_note_list()

    @property
    def notes_path(self):
        for path in self.all_paths_list():
            if "/notes" in path:
                return path

    @property
    def UID(self):
        return self.patient_UID

    @property
    def contact_info(self):
        """Returns a string dump of the CONTACT data."""
        the_info = str()
        contact_dict = self._data["CONTACT"]
        for key in contact_dict:
            the_info += str(key) + ": " + str(contact_dict[key] or "")
            the_info += "\n"
        return the_info

    @property
    def name(self):
        return self.first_name + " " + self.last_name

    @property
    def first_name(self):
        return self._data["CONTACT"]["PRENOM"]

    @property
    def last_name(self):
        return self._data["CONTACT"]["NOM"]

    @property
    def short_DOB(self):
        return self.date_of_birth(format="short")

    @property
    def long_DOB(self):
        return self.date_of_birth(format="long")

    @property
    def full_DOB(self):
        return self.date_of_birth(format="full")

    @property
    def short_exp(self):
        return self.exp(format="short")

    @property
    def long_exp(self):
        return self.exp(format="long")

    @property
    def HIN(self):
        return self._data["CONTACT"]["NAM"]

    @property
    def CHUS(self):
        return str(self._data["CONTACT"]["CHUS"] or "")

    @property
    def clinique(self):
        return str(self._data["CONTACT"]["CLINIQUE"] or "")

    @property
    def CMRF(self):
        return str(self._data["CONTACT"]["CMRF"] or "")

    @property
    def chart(self):
        if self.clinique == "CHUS":
            return self.CHUS
        elif self.clinique== "CMRF":
            return self.CMRF

    @property
    def telephone(self):
        return str(self._data["CONTACT"]["TEL"] or "")

    @property
    def cellular(self):
        return str(self._data["CONTACT"]["CEL"] or "")

    @property
    def street(self):
        return str(self._data["CONTACT"]["ADRESSE"] or "")

    @property
    def city(self):
        return str(self._data["CONTACT"]["VILLE"] or "")

    @property
    def province(self):
        return str(self._data["CONTACT"]["PROVINCE"] or "")

    @property
    def post_code(self):
        return str(self._data["CONTACT"]["CODEPOSTAL"] or "")

    @property
    def address(self):
        return (self.street + "\n" +
                self.city + " " +
                self.province + "\n" +
                self.post_code
               )

    @property
    def mailing_label(self):
        return self.name + "\n" + self.address

    @property
    def CHUS_label(self):
        return (self.name + "\n" +
                self.HIN + "\n" +
                "CHUS: " + self.CHUS + "\n" +
                self.telephone + "\n" +
                self.cellular + "\n" +
                self.address
                )

    @property
    def meds(self):
        return(self.meds_shortform_list())

    @property
    def atcd(self):
        return(self.atcd_list_pers())


#ENDCLASS
