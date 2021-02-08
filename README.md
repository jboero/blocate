# Blocate
A Q&amp;D slocate/mlocate alternative which provides basic fs indexing and search via SQLite.  Highly customizable.
Files and folders can be added to and index individually or in bulk via the bindex script.  The `find` command 
can be used to do specific index builds, by filename, type, size, etc.  Directory indexing does parallel iteration over
a `find` search result to index subdirectories.  It does not include files by default.  Sqlite file index requires 
no special permissions or ownership and defaults to current user ownership and umask.

ARG1 is search string for `blocate` or index target for `bindex`.
ARG2 is optional path to index file default `./blocate.sqlite` for `blocate` or `bindex`.

Usage:
```
bindex /path/to/file [sqlite file]
bindex /path/to/dir/ [sqlite file]
```
Searching:
```
blocate "%yoursearch%"
```

Current version 1 simply has one table with three fields:
1. ID (Inode int)
2. Parent (Inode int)
3. Name (varchar 256)

As such this only supports a single filesystem.  Simple query will only give an inode and parent inode.  
The `blocate` script will traverse up the parent inodes recursively using recursion and print the resulting path 
relative to index root.

Indexing L0 without automatic incremental options but it uses "insert or replace" so you can add to an index. 
Indexing operates in parallel with up to 4 concurrency by default.  This lets other threads handle IO while the 
SQLite database is locked. Using  `.timeout 1000` allows sqlite3 time to wait for the lock to free up.  It's not 
pretty but this is a super simple solution without requiring a dedicated database service.

Searching begins with a single query to fetch all inodes matching `blocate` arg1.  Then it traverses those paths with 
`xargs` in parallel opening the sqlite index in `read` mode to allow concurrent access.
