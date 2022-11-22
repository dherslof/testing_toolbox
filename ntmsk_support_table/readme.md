# ntmsk_support_table - Netmask Support Table
Simple table for displaying netmasks in different forms. Nice to have as 
a alias in local env. instead of having to use internet, because counting manually is time consuming. 

## Dependencies
* tabulate (pip3 install tabulate)

## Usage 
Display all 
```bash
python3 ntmsk_support_table.py -D
```

Display specific
```bash
python3 ntmsk_support_table -d <bitmask_without_/_prefix>
```

### Example
Display netmask **/22** in different forms
```bash
$ python3 ntmsk_support_table.py -d 22
╒═══════════════════╤══════════════════╤════════════╤═════════════════════════════════════╕
│  Bitmask (bits)   │ Dotted Decimal   │ Hex        │ Binary                              │
╞═══════════════════╪══════════════════╪════════════╪═════════════════════════════════════╡
│ /22               │ 255.255.252.0    │ 0xfffffc00 │ 11111111 11111111 11111100 00000000 │
╘═══════════════════╧══════════════════╧════════════╧═════════════════════════════════════╛
```
