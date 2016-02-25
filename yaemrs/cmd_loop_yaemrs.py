# Basic interface to the database
import cmd
import readline
import subprocess
import database_yaemrs as database
import support_yaemrs as support
from support_yaemrs import obligatory_input as oinput
import patient_yaemrs as pObj
from pprint import pprint
from collections import OrderedDict
import code
from datetime import datetime

yaemrs_version = "0.01alpha"
yaemrs_version_date = "21.10.2015"

INTRODUCTION_MESSAGE = """
YAEMRS (Yet Another Electronic Medical Record System)
Version: {0} ({1})
""".format(yaemrs_version, yaemrs_version_date)

class CommandShell(cmd.Cmd):
    """Abstraction to add a few class variables"""

    # class variables go here

    DB = None               # Database referenced by this menu
    patient_UID = None      # Current patient UID referenced by this menu
    patient_object = None   # Current patient OBJECT referenced by this menu
    stop = None             # Loop STOP flag (exit loop if True)

    # overriden class methods go here

    def postcmd(self, stop, line):
        """Called after each user command has be called."""
        return self.stop

    def default(self, line):
        """Called when unrecognized command is entered on the command line."""
        print("Unrecognized command.")
        self.do_help(None)
        return

    # shell methods go here

    def do_exit(self, arg):
        """Quit the program."""
        self.do_cls(arg)
        self.stop = True         # Exit the command loop
        return

    def do_quit(self, arg):
        """Quit the program."""
        # alias for do_exit
        self.do_exit(arg)
        return

    def do_cls(self, arg):
        """Clear the screen"""
        support.clearScreen()
        return

#endclass


class MainShell(CommandShell):
    """Yaemrs command shell"""

    # class global constants go here
    PLAIN_PROMPT = " > "

    MAIN_SHELL_TEXT = ("""
    Database commands:

    dbinfo    (show information about the database)
    new       (create a new patient)
    select    (select patient in database using 'pattern')
    list      (list all patients in database)

    exit

    Patient actions (act upon selected patient):

    edit      (edit the currently selected patient's chart)
    print     (print from patient's chart)
    clip      (clip from patient's chart)

    Other commands:

    clear     (clear screen)
    """)

    # CLASS GLOBAL VARIABLES GO HERE

    # OVERRIDEN CLASS METHODS GO HERE

    def preloop(self):
        """Called once before the command loop execution"""
        self.DB = database.PatientDB()
        self.intro = self.MAIN_SHELL_TEXT
        self.patient_UID = None
        self.prompt = self.PLAIN_PROMPT
        support.clearScreen()
        print(INTRODUCTION_MESSAGE)
        return

    def emptyline(self):
        """Called when user inputs an empty line"""
        self.do_cls(None)
        self.show_intro()
        return

    # SHELL COMMANDS GO HERE

    #   DATABASE COMMANDS

    def do_list(self, pattern):
        """Show a list of patients in the database matching 'pattern'"""
        if pattern == "": pattern = "*" #bug in cmd loop

        patient_list = self.DB.patient_list(pattern)

        for item in patient_list:
            print(item)

        print("\nResults: " + str(len(patient_list)))

        return

    def do_dbinfo(self, arg):
        """Print information about the database.
        Including: number of patients in database."""

        npatients = str(len(self.DB.patient_list("*")))

        info = "Number of patients in database: " + npatients
        print(info)

    def do_new(self, arg):
        """Make new patient or new note for existing patient.
        new patient ===> create new patient
        new note ===> new note for selected patient."""

        if arg.lower() == "patient":
            """Create a new patient in the database"""
            fname = oinput("First name: ")
            lname = oinput("Last name: ")
            HIN = oinput("RAMQ: ")
            chart = oinput("chart number: ")
            clinic = oinput("Clinic: ")
            # attempt to create the new patient
            try:
                newpatient_UID = self.DB.new_patient(
                        fname=fname, lname=lname, HIN=HIN,
                        chart=chart, clinic=clinic)
            except ValueError as e:
                print("\nCould not create new patient.")
                print("\nError: " + str(e))
            else:
                pattern=newpatient_UID.split("/")[-1:][0]
                self.do_select(pattern)
            return

        elif arg.lower() == "note":
            # make sure we have a patient
            if self.patient_object == None:
                print("Must choose a patient first")
                return

            # ask if for today or another date
            note_date_str = input("Enter date: (Return for today)")

            # default is today
            if note_date_str == "":
                note_date_str = \
                    str(datetime.today().strftime("%d.%m.%Y")) + ".note"
            else:
                note_date_str += ".note"

            self.patient_object.new_note(note_date_str)
            self.patient_object.edit_note(note_date_str)

    def do_select(self, pattern: str = ""):
        """Select a patient in database using 'pattern' """

        if pattern == "":
            pattern = input("Input search pattern (RETURN for all): ")

        pattern = "*" + pattern + "*"
        patient_list = self.DB.patient_list(pattern)
        len_patient_list = len(patient_list)

        if len_patient_list == 0:
            print("Pattern: " + pattern + " not found")

        elif len_patient_list == 1:
            self.set_patient_UID(patient_list[0])

        else:
            print("Multiple results: " + "(" + str(len_patient_list) + ")")
            counter = 1
            for item in patient_list:
                print("[" + str(counter) + "]: " + item)
                counter += 1
            print()
            print("Results: " + str(len_patient_list))
            print()

            r = 0

            while True:
                try:
                    r = int(support.obligatory_input("Please select: "))
                    if 0 < r < (len_patient_list + 1): break
                    else: print("Value out of range")

                except:
                    break

            if r == 0: return

            self.set_patient_UID(patient_list[r-1])
        return

    def do_clear(self, arg):
        """Clear the selected patient."""
        print("\nCleared selected patient.\n")
        self.set_patient_UID(None)
        return

    #   PATIENT COMMANDS (ACT ON SELECTED PATIENT) GO HERE

    def do_notes(self, arg):
        """Select from list of notes for selected patient."""

        if self.patient_UID is not None:
            counter = 0

            # note_list is a list of tuples (numeric date value (sorted) and
            # the title of the note for that date
            note_list = self.patient_object.patient_note_list()

            for note in note_list:
                counter +=1
                print("["+str(counter)+"] "+ note[1])

            choice = input("Select note: ")
            lookup_value = int(choice) -1
            chosen_note_string = note_list[lookup_value][1]

            self.patient_object.edit_note(chosen_note_string)
        else:
            print("No patient selected")

    def do_interact(self, arg):
        """Drop into Python interpreter"""
        db=self.DB
        patient=self.patient_object

        # this will drop out of the program and into the python prompt
        code.interact(local=locals())

    def do_label(self, arg):
        """Operate on patient labels."""
        if self.patient_UID is not None:
            print("\n" + self.patient_object.CHUS_label + "\n")
        else:
            print("No patient selected")

    def do_meds(self, arg):
        """Show patient medication list."""
        if self.patient_UID is not None:
            print("\nCurrent medication list\n")
            print(self.patient_object.meds)
        return

    def do_info(self, arg):
        """Show info on the selected patient"""
        if self.patient_UID is not None:
            print(self.patient_object.contact_info)
        return

    def do_listp(self, arg):
        """List properties of patient object."""
        if self.patient_UID is not None:
            the_dict = OrderedDict(sorted(self.patient_object.__dict__.items()))
            for key in the_dict:
                if key != '_data':
                    print(key, ": ", the_dict[key])
        else:
            print("No patient selected")

    def do_property(self, arg):
        """Show desired property from patient"""
        if arg == "": return
        try:
            if self.patient_UID is not None:
                print(getattr(self.patient_object, arg))

        except:
            print("Property not found")

    def do_edit(self, arg="", arg2=""):
        """Edit parts of currently selected patients chart (note/info)"""
        if self.patient_UID is None:
            print("No patient selected.")

        elif arg.strip() == "":
            print("Options: info, note")

        elif arg.lower() == "info":
            self.patient_object.edit_info()
            # reload all data
            self.reload_patient()

        elif arg.lower() == "note":
            self.do_notes(None)

        elif arg.lower() == "all":
            self.patient_object.edit()

        return

    def do_print(self, arg):
        """Print information from currently selected patient's chart."""
        if self.patient_UID is not None:
            print("Printing " + self.patient_UID)
        return

    def do_clip(self, arg):
        """Clip parts of patient chart to system clipboard."""
        if self.patient_UID is not None:
            print("Clipping " + self.patient_UID)
        return

    def do_files(self, arg):
        """Execute the ranger file manager on the currently selected patient."""
        if self.patient_UID is not None:
            command_string = "ranger " + self.patient_object.patient_dir
            subprocess.call(command_string, shell=True)
        return

    def do_paths(self, arg):
        """Show the system paths associated with currently selected patient."""
        if self.patient_UID is not None:
            print(self.patient_object.all_paths())
        return

    #   ALIASES TO COMMANDS GO HERE

    def do_ls(self, parttern):
        self.do_list(pattern)
        return

    def do_q(self, arg):
        self.do_exit(None)
        return

    def do_x(self, arg):
        self.do_exit(None)
        return

    def do_s(self, pattern: str= ""):
        self.do_select(pattern)
        return

    # END SHELL COMMANDS

    # UTILITY FUNCTIONS GO HERE

    def print_dict(self, the_dict):
        if the_dict is not None:
            for key in the_dict:
                part1 = str(key) + ": "
                part2 = (str(the_dict[key]) if the_dict[key] is not None
                        else "")
                print(part1 + part2)
        return

    def set_patient_UID(self, UID):
        """Set the cmd loop patient_UID value"""
        if UID is None:
            self.patient_UID = None
            self.patient_object = None
            self.prompt = self.PLAIN_PROMPT
        else:
            self.patient_UID = UID
            self.patient_object = pObj.PatientObject(self.patient_UID, self.DB)
            print("Selected: " + self.patient_UID + "\n")
            self.prompt = self.patient_UID + " > "
        return

    def reload_patient(self):
        """Force system to reload the patient values from updated files."""
        self.set_patient_UID(self.patient_UID)

    def show_intro(self):
        print(self.MAIN_SHELL_TEXT)
        return

#ENDCLASS

if __name__ == "__main__":

    main_shell = MainShell()
    main_shell.cmdloop()
