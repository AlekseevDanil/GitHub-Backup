# Backup your GitHub 🗃

## Overwiev
The script that is in this repository helps to backup all your *gists* and *repositories*, as well as all the branches in them with just one command!

The [GitHub API](https://docs.github.com/en/rest) technology is used to interact with the account, and the standard libraries [python](https://www.python.org)>=3.8

## Quickstart
To work with the code, you will need a [GitHub developer token](https://github.com/settings/tokens).\
Make sure you give full control scopes to **repo** and **gist**

Clone this repository to your local computer, go to the project directory and enter this command in terminal:

```bash
python savegit.py -t <YOUR GITHUB TOKEN>
```
And that's it! You will see the backup of all your repositories and gists begin.

More information can be found by running this command in terminal:

```bash
python savegit.py --help
```

## Contributing
Long-term discussion and bug reports are maintained via GitHub Issues. Code review is done via GitHub Pull Requests.\
I will be glad for your support!
