"""Object abstactions that are used to build other usefull parts of the
system."""


import ruamel.yaml as ryaml
import pathlib
from pprint import pprint

class YAML_setattr_Object():
    """Simple object that accepts 2 parameters:
    yaml_file_name: a YAML formatted data file to read
    canonical_attributes_list: a list of keys to be found in the above file.

    The returned object will posess attributes created using the
    canonical_attributes_list, with values supplied by yaml_file_name

    An example is easier to understand:

    Given the file data1.yaml, which contains:

        FNAME: Jack
        LNAME: Nimble
        PHONE: 888.123.4567
        ADDR:
        ALIAS: Speedy

    and the canonical_attributes_list:

        the_list = ["FNAME","LNAME", "DOB", "PHONE","ADDR"]

    an object is instantiated using the following call:

    my_object1 = YAML_setattr_Object("data1.yaml", the_list)

    After this, my_object1 has the following attributes (properties)
        my_object1.FNAME ---> "Jack"
        my_object1.LNAME ---> "Nimble"
        my_object1.DOB   ---> ""
        my_object1.PHONE ---> "888.123.4567" (NB this is a str())
        my_object1.ADDR  ---> ""

    Note that the DOB attribute exists, and is "" (empty) even though it is not
    in the data1.yaml file. Since it is in the canonical_attributes_list it is
    automatically added to the object and a null value assigned.

    Also note that the ADDR attribute is "" (empty) because it was not assigned
    a value in the data1.yaml file.

    Also note that my_object1 does NOT have a ALIAS attribute.
    Calling my_object1.ALIAS (in this case) will result in a error:

    AttributeError: type object 'my_object1' has no attribute 'ALIAS'

    This is because even though it is specified in the data1.yaml file, it is
    not in canonical_attributes_list and therefor not considered "canonical".
    The reasoning is to allow for arbitrary data fields in the YAML data
    files. The system does not restrict them, but it does not recognize them
    either.

    """
    def __init__(self, yaml_file_name: str, canonical_attributes_list: list):

        # INSTANCE VARIABLES
        self.yaml_read_file_name = yaml_file_name

        # the output file set to the input file, so any changes will overwrite
        # the original data.
        self.yaml_write_file_name = self.yaml_read_file_name
        self.canonical_attributes_list = canonical_attributes_list
        self.data = self._load_yaml()

        # INSTANTIATION CALLS
        self._initialize_all_attrs()
        self._assign_all_attrs()

    def _initialize_all_attrs(self):
        """Initialize all 'canonical' attributes to empty strings."""
        for attribute in self.canonical_attributes_list:
            setattr(self, attribute, "")

    def _load_yaml(self):
        """User ruamel.yaml to load the YAML file definition into the .data
        attribute of this object.
        Raises an error if the file is not found.
        """
        if pathlib.Path(self.yaml_read_file_name).exists():
            try:
                with open(self.yaml_read_file_name, 'r') as handle:
                    return ryaml.load(handle, ryaml.RoundTripLoader)
            except:
                raise ryaml.YAMLError
        else:
            raise FileNotFoundError((yaml_file_name + ": does not exist."))

    def _assign_all_attrs(self):
        """Assign values from .data to object's corresponding attributes,
        using the list of canonical attributes and the values loaded into the
        .data attribute by the _load_yaml() method, called previously.
        """
        for attribute in self.canonical_attributes_list:
            setattr(self, attribute, self.data[attribute])
        return

    def _update_data_dict(self):
        """This method is used to 'update' the .data attribute of the object.
        Upon initialization data is copied OUT of .data, but chages may be
        made to individual attributes. This method copies the changes back
        into the .data attribute.

        Example (see object docstring for example setup):

        my_object1.FNAME is set to "Jack", but the program using the object
        may change the value to "Charles", so my_object1.FNAME ==> "Charles"
        but my_object1.data["FNAME"] (original data as read from yaml file)
        is still set to "Jack".

        This method copies the value back into the .data structure, so that
        my_object1.data["FNAME"] ===> "Charles"
        """
        for member in self.canonical_attributes_list:
            self.data[member] = getattr(self, member)

    def _dump_yaml(self):
        """Returns a format suitable for writing to a file, in YAML format
        """
        self._update_data_dict()    # copy changes to object back into .data
        return ryaml.dump(self.data, Dumper=ryaml.RoundTripDumper)

    def __repr__(self):
        """(Overrides __repr__)
        Return a nice string, representing the object attributes, which
        just happens to be the YAML string representation. (coincidence)
        """
        return self._dump_yaml()

    def _write_yaml(self):
        """Write the YAML representation to the self.yaml_write_file_name
        file.
        """
        with open(self.yaml_write_file_name, 'w') as handle:
            handle.write(self.__repr__())


