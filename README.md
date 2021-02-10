I've used slocate and mlocate for years but struggle with index control and I've always been blown away that you can't control index criteria or just index directories.  There have been a few alternatives in the wild but I have my own that is super simple and uses sqlite.  Literally \~30 lines of bash each for index and locate with great performance and sqlite-safe parallel operations.  No special permissions required.

The great thing is you can just index the results of a find command, which contains anything you want.  Index is currently a simple map of inode, parent inode, and name, so searching is super quick. No cross-filesystem support - single fs only.  Future options include indexing stat data.  I have a local backup archive browsable by web application and mlocate searches can take up to 10 seconds.  This reduces most to \~300ms.

[https://github.com/jboero/blocate](https://github.com/jboero/blocate)

[https://copr.fedorainfracloud.org/coprs/boeroboy/mawenzy/package/blocate/](https://copr.fedorainfracloud.org/coprs/boeroboy/mawenzy/package/blocate/)

# Blocate

A Q&D slocate/mlocate alternative which provides basic fs indexing and search via SQLite.  Highly customizable. Files and folders can be added to an index individually or in bulk via the bindex script.  The `find` command can be used to do specific index builds, by filename, type, size, etc.  Directory indexing does parallel iteration over a `find` search result to index subdirectories.  Directory indexing does not include files by default.  Easiest way to index files is to pipe results from a `find` command.  Sqlite file index requires no special permissions or ownership and defaults to current user ownership and umask.

# Bindex

ARG1 is optional index root for `bindex` default to pwd \`.\`.ARG2 is optional path to index file default `./blocate.sqlite`.If you pass stdin to \`bindex\` then optional ARG1 is expected to be db location.Indexing without args defaults to pwd saving to default `./blocate.sqlite`: `bindex .`Indexing uses parallel which is possible with sqlite locking using a timeout of 2s.  If you are indexing to slow storage or over networks you may want to drop parallelism via env var \`$BLOCATEPARA\` or just index to tmpfs before copying to network.

    bindex
    bindex [/path/to/file] [./blocate.sqlite]
    bindex [/path/to/dir/] [./blocate.sqlite]

or index a list or `find` command from stdin:

    find . -type d -or -type f -iname '*.doc' -mtime +1 | bindex [./blocate.sqlite]

# Blocate

Optional flag \`-r\` uses REGEX instead of LIKE in database.  This requires sqlite-pcre support.ARG1 is search string or regex.  There are no implicit wildcards.ARG2 is optional path to index file default `./blocate.sqlite`

    blocate "%yoursearch%" [./blocate.sqlite]

If you have sqlite pcre installed you can use regex:

    blocate -r "YOURREGEXP" [./blocate.sqlite]

Current version 1 simply has one table with three fields:

1. ID (Inode int)
2. Parent (Inode int)
3. Name (varchar 256)

As such this only supports a single filesystem.  Simple query will only give an inode and parent inode. The `blocate` script will traverse up the parent inodes recursively using recursion and print the resulting path relative to index root.  If your index doesn't include your full path search results will be rooted as far up as they can go, so wise to index all directories first.

Indexing is L0 without automatic incremental options but it uses "insert or replace" so you can add to an index. Indexing operates in parallel with up to 4 concurrency by default.  This lets other threads handle IO while the SQLite database is locked. Using  `.timeout 1000` allows sqlite3 time to wait for the lock to free up.  It's not pretty but this is a super simple solution without requiring a dedicated database service.

Searching begins with a single query to fetch all inodes matching `blocate` arg1.  Then it traverses those paths with `parallel` \--max-procs=$BINDEXPARA the sqlite index in `read` mode to allow concurrent access.  Tuning the parallel options can have a great influence on performance, but generally it scales out very well for just a SQLite DB as long as you're using readonly.
