# osx-trash-manager

Keep a history of trashed files and delete ones older than a month.

Designed to be placed in your cron table or occasionally run manually.

## Usage

Just launch it without arguments.

It will analiyze the content of `~/.Trash/`, store new filenames in a sqlite3 db
named `~/.Trash.db`, and delete files or folders trashed more than 30 days ago.
