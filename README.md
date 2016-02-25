##**YAEMRS (Yet Another Electronic Medical Record System)**

Copyright (c) 2015 Michael LONGVAL, mlongval(at)gmail.com<br>
This software is licensed under the [GNU GPLv3](http://www.gnu.org/licenses/gpl.html) <br>

1. Purpose (Requirements)<br>

    The intent of the system is to provide a SMALL, FAST and EFFICIENT patient record management
    system.<br><br>

    As a primary care physician I work with many electronic medical records systems.<br>
    While I do not want to be disrespectful to the developers of those systems, I have always felt
    that they are of the "one size fits all" type.<br><br>

    That of course is their purpose. It is impossible for large EMR systems to cater to the specific
    requirement/preferences of each individual user.<br><br>

    My goal therefor with this program is to create something simple and fast, that is adapted to my
    individual tastes.<br><br>

    This system grew out of my use of the VIM editor to create my patient files,
    using the YAML data serialization format (perhaps an ill fated attempt to use it in-lieu of
    a "REAL" database) with some added Python3 macros.<br><br>

    That being said, I think the learning curve is steep for this system.  If your are unfamiliar
    with VIM and/or unwilling to put in the time to learn it, I would suggest, to paraphrase master
    Obi-Wan: "This is not the software you are looking for."<br><br>

2. Audience
    I wrote this system for myself (scratching the itch). I am a primary care physician.
    I live and work in Sherbrooke, Québec.<br>
    YAEMRS reflects my working situation.
    I live and work in both French and English, in the public health care service,
    so the system is adapted to my needs. <br>
    But since it is also OpenSource Software, you can (with some work) adapt it to your
    situation.<br><br>

3. Structure (Implementation)

    1. The program is written in Python3.5

    2. The underlying database structure is just the operating system filesystem. No fancy SQL RDBMS
       here folks. (this may prove to be more of a bug than a feature....)

    3. The data files are just text files. The format for the files is UTF-8 and the data is
       structured using the YAML data serialisation format.

    4. The system relies on the VIM editor. In fact the speed and efficiency that I found I gained
       while using VIM was what made me want to extend it to a whole system.  While it could
       probably work with another editor, I have no intention of supporting it.

    5. I developped the system on my MacBook Pro with MacOSX (El-Capitan). Most of my tools come
       from the Homebrew system, including Python3.5 and VIM7.4. I have not tried it with the stock
       Python and Vim that come with MacOSX.

    6. Running it on Linux "should" be rather trivial, as the tools I used on MacOSX are essentially
       ports from Linux. That being said, I have not tested it on Linux.

    7. I do not have a Windows system to test it on, but I have tried to stick to the Python3.5
       standard library (using the pathlib library).

    8. As above, I try to use only "standard" Python3.5 libraries, the exception are the use of
       ruamel.yaml inlieu of the "standard" yaml that ships with Python3.5. The reason is that
       ruamel.yaml supports output to Python OrderedDict types, where the order of the keys is
       preserved. As a side note, I cannot imagine why on earth the standard YAML definition does
       not mandate that key order be presereved, after all, YAML is intended to be HUMAN readable,
       and out-of-order-keys does NOT help readability.
       The ruamel.yaml library is available via "pip install ruamel.yaml" or
       "pip3 install ruamel.yaml" if using MacOSX Homebrew.

    9. Database Layout

        db_root_dir                                          <=== DB main directory<BR>
        ├── patients_data_dir                                <=== where all patient subdirs are kept<BR>
        │   └── Lastname.Firstname.LASF14123101.99999.CMRF   <=== an individual patient subdir<BR>
        ├── temp                                             <=== temporary files go here<BR>
        ├── appointments                                     <=== db level appointment data here<BR>
        └── billing                                          <=== db level billing data here<BR>

    10. Individual Patient Directory Layout

        Lastname.Firstname.LASF14123101.99999.CMRF          <=== directory name is Patient UID<BR>
        ├── atcd.yaml                                       <=== patient antecedants file<BR>
        ├── contact.yaml                                    <=== contanct and demographic data<BR>
        ├── docs                                            <=== scanned documents and relevant data<BR>
        │   └── scanned_doc.pdf<BR>
        ├── meds.yaml                                       <=== medication list<BR>
        └── notes                                           <=== clinical notes subdir<BR>
            └── 28.08.2015.note                             <=== note for 28.08.2015 (dd.mm.yyyy)<BR>

        Patient UID (Unique Identifier) format:

        Lastname                                            <=== patient's last name (alpha only)<BR>
        Firstname                                           <=== patient's first name (alpha only)<BR>
        LASF14123101                                        <=== *Québec RAMQ format HIN<BR>

            LASF: first 3 letters of Lastname (LAS) + first letter of Firstname (F)<BR>
            141231: DOB (YYMMDD) (50 will be added to MM if it is a woman<BR>
                    so a man born on 141231 would have the value 141231<BR>
                    while a woman would have 146231)<BR>
            01: (the last 2 digits are an administrative identifier to distinguish 2 people<BR>
                who are born on the same day and have the same first 4 letters of the ID<BR>
                which are the same. The first registered would be 01, the second 02)<BR>

        99999: is the chart number at the primary clinic for this patient. (no upper limit, digits
               only)<BR>
        CMRF: is the abbreviation for the primary clinic for this patient. (user defined)<BR>

        * The province of Québec public health insurance (RAMQ - Régie de l'Assurance Maladie du
        Québec) standard HIN (Health insurance number) for each citizen of the province.<BR>

4. Configuration

    The configuration, as noted above, is specified by the "config.ini" file. It follows the Python
    "configparser" library format. Please note however that the system has only been tested using
    the standard configuration. Your mileage may vary.

5. Security

    Security is of utmost importance to me. My patients' personal information must be kept safe
    at all times. Therefor I have structured my system in the following manner.
    (Plase not that YAEMRS does NOT provide the following features, they must be implemented by the
    user of the system. The following are only examples of what I do.)

    1. My computer (MacBook Pro) has a firmware password set.
    2. The entire computer system HD is encrypted with Apple's FileVault set at AES-256bit with a
    different password than the firmware's.
    3. The patient data is stored on a AES-256bit encrypted virtual disk. This virtual disk
    NOT automounted with the base system password. A separate, longer password is needed to
    unlock the virutal disk.
    4. The backups of the data are made to a secure system, in encrypted virtual disk format so
    they are not visible on the backup system without knowledge of the password.
    5. Since the system is text only, SSH access is available. A valid SSH certificate
    is required.

6. Pro and Cons

    - Pros:
        - Text mode (console) + Python + Simple text file based DB = Fast and efficient system
        - Source code is available so you can adapt it to your needs.
        - Vim !!!! what else can I say ;)
    - Cons:
        - Text mode → many people will see it as "old school".
        - Steep learning curve. Learning Vim can be very daunting.
        - I AM NOT A PROFESSIONAL PROGRAMMER. I wrote this software using the *"scratch the itch"*
          philosophy. That means that it is probably just a hodgepodge of spaghetti code.
          But hey I find it useful spaghetti code.


