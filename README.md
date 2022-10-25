# CMS-Downloader

1. Python script to download Content from the GUC Content Management System [CMS](https://cms.guc.edu.eg/)
2. Then rates it, this to mark it as being downloaded and not download it again. You can disable this behaviour via --no-rate argument.

![](https://i.imgur.com/oXib1qA.gif)

## Start

Create a `.env` file and put your guc username and the password on the next line, for example

```
theusername
mysupersecreatpassowrd
```

Then in a terminal do

```
pip install -r requirements.txt
python main.py
```

## Dependencies

- Python 3.10

## CLI Options

only one optional flag is supported.

- The default behaviour is to download only not rated content, then rates it.
- `--no-rate` or `--nr` Download but don't rate the content.
- `--no-download` or `--nd` only lists what's not yet downloaded from the CMS.

<!-- Images or Output text -->

## References

- thanks to [@aboueleyes](https://github.com/aboueleyes/cms-downloader-refined) i used some of his code.
