# osx-trash-manager

Script that keeps a history of trashed files and deletes ones older than a
month.

Designed to be placed in your cron table or occasionally run manually.

## Usage

Place the script in your `$PATH` and launch it or add to your cron table.

It will analiyze the content of `~/.Trash/`, store new filenames in a sqlite3 db
named `~/.Trash.sqlite3`, and delete files watched for more than 30 days.

## Todo

- improve exception management
- clear db entries from manually deleted files
- add filename management for ones not encoded in UTF-8
