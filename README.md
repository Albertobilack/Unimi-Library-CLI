# Unimi-Library-CLI 

Simple CLI script to reserve spots at University of Milan (UNIMI) Library



![Static Badge](https://img.shields.io/badge/semver-1.0.0-blue)




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
py -m UnimiLibrary book -date 2024-09-23 -floor ground -start 13:00 -end 21:00
```
## Usage

For usage instructions, please refer to the built-in manual by accessing the help message within the package

display help message

```bash
py -m UnimiLibrary [book | list | freespot | quick] -h
```


## Roadmap

- Display active reservations

- Delete active reservations


## Contributing

Contributions are always welcome! For major changes, please open an issue first
to discuss what you would like to change.



## License

[MIT](https://choosealicense.com/licenses/mit/)


## Authors

- [@Albertobilack](https://github.com/Albertobilack)