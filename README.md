# Unimi-Library-CLI 

Simple CLI script to reserve spots at University of Milan (UNIMI) Library

![Static Badge](https://img.shields.io/badge/semver-1.1.1-blue)
## Installation

Install Unimi-Library-CLI with pip

```bash
  pip install Unimi-Library-CLI
```

Install a specific version

```bash
  pip install Unimi-Library-CLI==X.X.X
```

By deafult, `pip` will install the latest version of dependencies. However, the tested version are listed in `requirements.txt` and can be installed using

```bash
  pip install -r requirements.txt
```
## Example

```bash
python -m UnimiLibrary book -date 2024-09-23 -floor ground -start 13:00 -end 21:00
```
## Configuration

Before using the package, you need to configure the values in the config file by running

```bash
python -m UnimiLibrary config -name NAME -email EMAIL -password PASSWORD -cf CODICEFISCALE -start HH:MM -end HH:MM -floor [{ground, first}]
```

| Argument | Value         | Info/Format       | Example       |
| ------------- | ------------- | ------------- | ------------- |
| -name | NAME  | Last name + First name, first letter must be uppercase, wrapped in double quotes | "Rossi Mario" |
| - email | EMAIL  | Unimi institutional email | nome.cognome@studenti.unimi.it |
| -password | PASSWORD | Unimi account password | ABCDE123 |
| -cf | CODICEFISCALE | must be uppercase | WRBJDC66C65B642X |
| -start | HH:MM | reservation's start time, 24-hour format | 13:00 |
| -end | HH:MM | reservation's start time, 24-hour format | 21:00|
| -floor | ground/first | target floor | ground |


Please note that all values must be properly configured for the package to function correctly. This entire setup is required only once, and you can modify individual parameters later if needed.
## Usage

For more in-depth usage instructions, please refer to the built-in manual by accessing the help message within the package using

```bash
python -m UnimiLibrary [book | list | freespot | quick | config] -h
```

## Roadmap

- Display active reservations

- Delete active reservations
## Contributing

Contributions are always welcome! For major changes, please open an issue first
to discuss what you would like to change.
## License

This project is licensed under the terms of the `MIT` license
## Authors

- [@Albertobilack](https://github.com/Albertobilack)