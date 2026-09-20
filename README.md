# gs-tools-py

#### Gyakuten Saiban (Ace Attorney: Trilogy) data manipulation tools.
<div align="center">
	<a href="https://github.com/Veydzher/gs-tools-py/blob/master/LICENSE">
		<img src="https://img.shields.io/github/license/Veydzher/gs-tools-py.svg?"/>
	</a>
</div>

## Information
This program allows you to do the following:
* Decode an encrypted/a decrypted `.mdt` files to `.json`.
* Encode `.json` file back to encrypted/decrypted `.mdt` file.
* Export strings from `.mdt` file or decoded `.json` file to `.csv` file.
* Import string from `.csv` file back to `.mdt` file or decoded `.json` file.


## Supported Games
The following games were tested so far:
* Phoenix Wright: Ace Attorney Trilogy

P.S: The list might expand.

## Usage
```
GSMdtTools.exe [-h] {decode,encode,export,import} ...

arguments:
    decode      decode encrypted/decrypted .mdt file to .json file
    encode      encode .json file to encrypted/decrypted .mdt
    export      export strings from .mdt/.json file to .csv file
    import      import strings from .csv file to .mdt/.json file

options:
  -h, --help    show this help message and exit
```

## Warning
- The program is stil a work in progress and may generate files that are not 1:1 to the originals.
- The program has only been tested with USA ``(*_u.mdt)`` dialog scripts and might need extra character conversion information to work with scripts from other regions.

## Thanks
* [funkkiy](https://github.com/funkkiy) for his program as a reference.
