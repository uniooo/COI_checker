# COI_checker
An automatic COI checker to find the conflict of interest for conference submissions.

Forked from [Hanchen-Wang/COI_checker](https://github.com/Hanchen-Wang/COI_checker).

Now it can batch check, and some existing bugs have been fixed.

## Usage

```
python find_coi.py --xml_path <xml_path> --search_years <search_years> --pc_file <pc_file>
```
Example:
```
python find_coi.py --xml_path ./data/ --search_years 10 --pc_file ./data/pc_members.xlsx
```

If need to check co-authers in last 3 years or >= 4 times in last 10 years:
```
python find_coi.py --xml_path ./data/ --search_years 3 --times_and_years 4 10 --pc_file ./data/pc_members.xlsx
```

<xml_path> is the path of downloaded DBLP author files. Current, this checker only supports the xml format. I provide serveral downloaded pages of the professors in the data folder.

'search_years' is a string with the number of years you want to check. e.g., 3.

'times_and_years' is optional. It is two string with the number of co-auther times and years. e.g., 4 10.
 
<pc_file> is a xlsx file contains the information of PC members. You can build this by copying the coi name list from CMT and pasting in Excel. An example PC member file is provided in the data folder.

> Currently this checker is under alpha test. If you have any issue, please contact me.
