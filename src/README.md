# Documentation for specific modules

## Script ```license_manager_script```

This script is just interface to ```license_manager``` module.
Script is used for finding and replacing licenses in given files/locations whilest supporting placeholders.
*For usage run ```python license_manager_script.py --help```*

### Adding locations to script

In order to work user needs to specify ```files``` or ```locations``` which will be processed.

* Flag ```-f``` or ```--file``` (can be used multiple times)
  
  Value should be absolute or relative path to file which will be processed
  
* Flag ```-d``` or ```--dir``` (can be used multiple times)
  
  Value should be absolute or relative path to dir which will be **recursively** processed.
  
### What files will be processed?
All recursively search dirs will process only files with extensions: ```'.hh', '.cc', '.h', '.c', '.cpp', '.hpp'```.
Exception is flag ```-f``` or ```--file``` which will process given file always. 

### Finding license
User can specify which old license looked like: how it stared and how it ended.
Old license will be regonized as license if it starts **at the beginning of the file** (whitespace ignored).

* Flag ```-s``` or ```--start``` (default is ```/*!```)
  
  Value should be start sequence of the old license
  
* Flag ```-e``` or ```--end``` (default is ```*/```)

  Value should be end sequence of the old license.
  

### New license
User can specify new license which will replace old one. If no license is specified old license will be removed.

* Flag ```-l``` or ```--license``` default ```None```

  Absolute or relative path to file containing new license
  
### Placeholders
User can specify in license files placeholders which will be processed and replaced. Some placeholders are present by default:

* **```filepath```**  - absolute path currently processed file,
* **```filename```**  - file name of currently processed file,
* **```datetime```**  - current system date

if user specifies directory, where is git root, more default values will be available

* Flag ```-g``` or ```--git``` git root directory

#### Custom placeholders

* Flag ```-o``` or ```--option``` (can be used multiple times)

  Value should be in form of ```NAME:VALUE```

#### Using placeholders in license file
Placeholders need to be wrapped in braces to be recognized. E.g. ```{filename}```.
Placeholders can be also formated using [this specification](https://docs.python.org/2/library/string.html#format-specification-mini-language).
  
### New license
User can specify new license which will replace old one. If no license is specified old license will be removed.

* Flag ```-l``` or ```--license``` default ```None```

  Absolute or relative path to file containing new license
  
### Placeholders
User can specify in license files placeholders which will be processed and replaced. Some placeholders are present by default:

* **```filepath```** - absolute path currently processed file (String)
* **```filename```** - file name of currently processed file (String)
* **```datetime```** - current system date (Date)

if user specifies directory, where is git root, more default values will be available

* Flag ```-g``` or ```--git``` git root directory:

Additional placeholders available:

* **```branch```** - current branch name (String)
* **```last_change```** - date of last change (String)
* **```last_author```** - name of the last author to make changes (String)
* **```last_email```** - email of the last author to make changes (String)

#### Custom placeholders

* Flag ```-o``` or ```--option``` (can be used multiple times)

  Value should be in form of ```NAME:VALUE```

#### Using placeholders in license file
Placeholders need to be wrapped in braces to be recognized. E.g. ```{filename}```.
Placeholders can be also formated using [this specification](https://docs.python.org/2/library/string.html#format-specification-mini-language).

##### Example 1

file ```new_license.txt``` contains following:


```txt
/*!
 *
 * Copyright (C) 2007-{datetime:%Y} Technical University of Liberec.  All rights reserved.
 * 
 * @file {filename:>20s} "{filepath}"
 */
 ```
 
 When called with
 ```bash
 python license_manager_script.py -f "./path/to/file/main.cc" -l new_license.txt
 ```
 
 will generate something like this:
 
 ```cc
 /*!
 *
 * Copyright (C) 2007-2015 Technical University of Liberec.  All rights reserved.
 * 
 * @file              main.cc "/usr/jan-hybs/flow123d/path/to/file/main.cc"
 */
 
 ... file content goes here
 ```
 
 
##### Example 2

file ```new_license.txt``` contains following:


```txt
/*!
 *
 * Copyright (C) 2007-{datetime:%Y} Technical University of Liberec.  All rights reserved.
 * 
 * @author '{last_author:~>40s} ({last_email})'
 * @file   '{filename:~^40s}'
 * @branch '{branch:~<40s}'
 */
 ```
 
 When called with
 ```bash
 python license_manager_script.py -f "./path/to/git/src/main.cc" -l new_license.txt -g "./path/to/git/"
 ```
 
 will generate something like this:
 
 ```cc
/*!
 *
 * Copyright (C) 2007-2015 Technical University of Liberec.  All rights reserved.
 * 
 * @author '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Jan Hybs (jan.hybs@tul.cz)'
 * @file   '~~~~~~~~~~~~~~~~main.cc~~~~~~~~~~~~~~~~~'
 * @branch 'JHy_ist_formatter~~~~~~~~~~~~~~~~~~~~~~~'
 */
 
 ... file content goes here
 ```
