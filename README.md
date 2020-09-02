# GithubSanatize
with this little script you are able to filter your code for personal information and private data before every commit
![Unittest 3.6 - 3.8](https://github.com/Lightmoll/GithubSanatize/workflows/Unittest%203.6%20-%203.8/badge.svg)

# Features
 * Automatic .git and .gitignore detection
 * E-Mail and Sensitive word filter
 * Two Scanning Modes
 * Colored Output

# Usage
run the script with Python 3.6+ or using ./ghs.py on linux

```
usage: ghs.py [-h] [-d] [-v] [-s] [-a] [--scan-git]
              folderPath [folderPath ...]

code privacy sanitizer, it automatically ignores all .git and in .gitignore
specified folders

positional arguments:
  folderPath            enter a folder or file of your source code

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug
  -v, --verbose-output  shows more, possible faulty results
  -s, --sort            sort occurrences by importance
  -a, --all             scan all files regardless of their file extension
  --scan-git            scan the entire folder structure regardless of any
                        .gitignore and .git
```

# Contribution
All new feature implementations or performance improvements are very much welcome!
Simply fork this repo and open a pull request or create an issue.
