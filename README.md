# Flow123d-py-profiler-transform

Takes file in json profiler format created in project [Flow123d](https://github.com/flow123d/flow123d) and
converts it to different format.

## Usage
```
Usage: profiler_formatter_script.py [options]

Options:
  -h, --help            show this help message and exit
  -i FILENAME, --input=FILENAME
                        Absolute or relative path to JSON file which will be
                        processed
  -o FILENAME, --output=FILENAME
                        Absolute or relative path output file which will be
                        generated/overwritten
  -f CLASSNAME, --formatter=CLASSNAME
                        Classname of formatter which will be used, to list
                        available formatters use option -l (--list)
  -l, --list            Prints all formatters available in folder formatters
                        (using duck-typing)
  -s STYLES, --style=STYLES
                        Additional styling options in name:value format (for
                        example separator:  default is os separator)
```
## Examples
List all avaiable formatters:

```bash
> python profiler_formatter_script.py -l
```
```
Formatter available: 
	CSVFormatter
	SimpleTableFormatter
```

Transform json file ```foo.json``` to csv format file ```bar.csv```:

```bash
> python profiler_formatter_script.py -i 'foo.json' -f 'CSVFormatter' -o 'bar.csv'
```
```bar.csv file generated```

Print json file ```foo.json``` in simple table format with extra paddings around cells:

```bash
> python profiler_formatter_script.py -i 'foo.json' -f 'SimpleTableFormatter' -s 'padding:5'
```

## Module support

by importing ```profiler_formatter_module``` you can use formatter in python code
```bash
> python

>>> import profiler_formatter_module
>>> profiler_formatter_module.ProfilerFormatter.list_formatters ()
['CSVFormatter', 'SimpleTableFormatter']
>>> profiler_formatter_module.ProfilerFormatter().convert ('foo.json', 'bar.txt')
bar.txt file generated
True
```