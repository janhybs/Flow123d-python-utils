# Flow123d-py-profiler-transform

Takes file in json profiler format created in project [Flow123d](https://github.com/flow123d/flow123d) and
converts it to different format.

## Examples
List all avaiable formatters:

```bash
> python main.py -l
```
```
- CSVFormatter        
- SimpleTableFormatter
```

Transform json file ```foo.json``` to csv format file ```bar.csv```:

```bash
> python main.py -i 'foo.json' -f 'CSVFormatter' -o 'bar.csv'
```
```bar.csv file generated```

Print json file ```foo.json``` in simple table format with extra paddings around cells:

```bash
> python main.py -i 'foo.json' -f 'SimpleTableFormatter' -s 'padding:5'
```
