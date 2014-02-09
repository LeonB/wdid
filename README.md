# What Did I Do?

`wdid` (What Did I Do) is a little python script that reads the [zeitgeist](zeitgeist-project.com)
activities / logs and creates an ascii table with all the stuff you did in a
particular period.

The script tries to be smart about the acitivities and combines different events
if it thinks they relate.

This script contains workflow specific logic so I would be very supprised if
this would be useful for someone else.

# Example

```
$ bin/wdid
+-------------------------+---------------------+---------------------+----------+
|             description |        start        |         end         | duration |
+-------------------------+---------------------+---------------------+----------+
| ~/Workspaces/prive/wdid | 2014-02-09 00:01:06 | 2014-02-09 01:01:15 | 1:00:09  |
|       stackoverflow.com | 2014-02-09 00:54:30 | 2014-02-09 00:59:40 | 0:05:10  |
| ~/Workspaces/prive/wdid | 2014-02-09 10:28:46 | 2014-02-09 12:27:09 | 1:58:23  |
+-------------------------+---------------------+---------------------+----------+
|                         |                     |                     | 3:03:42  |
+-------------------------+---------------------+---------------------+----------+
```

``` bash
$ bin/wdid 2014-02-08 08:00
+----------------------------+---------------------+---------------------+----------+
|                description |        start        |         end         | duration |
+----------------------------+---------------------+---------------------+----------+
|    ~/Workspaces/prive/wdid | 2014-02-08 12:30:23 | 2014-02-08 12:41:17 | 0:10:54  |
| ~/Workspaces/prive/ansible | 2014-02-08 13:38:51 | 2014-02-08 13:41:03 | 0:02:12  |
|                  google.nl | 2014-02-08 14:11:35 | 2014-02-08 14:14:30 | 0:02:55  |
|                 dashku.com | 2014-02-08 14:29:32 | 2014-02-08 14:31:59 | 0:02:27  |
|            gist.github.com | 2014-02-08 14:38:41 | 2014-02-08 14:43:58 | 0:05:17  |
|    ~/Workspaces/prive/wdid | 2014-02-08 14:56:35 | 2014-02-08 15:49:38 | 0:53:03  |
|            docs.python.org | 2014-02-08 15:41:52 | 2014-02-08 15:43:53 | 0:02:01  |
|    ~/Workspaces/prive/wdid | 2014-02-08 15:55:01 | 2014-02-08 15:57:51 | 0:02:50  |
|            docs.python.org | 2014-02-08 15:56:00 | 2014-02-08 15:58:21 | 0:02:21  |
|    ~/Workspaces/prive/wdid | 2014-02-08 17:48:23 | 2014-02-08 17:51:52 | 0:03:29  |
|         mathias-kettner.de | 2014-02-08 20:06:45 | 2014-02-08 20:09:14 | 0:02:29  |
|    ~/Workspaces/prive/wdid | 2014-02-08 20:21:46 | 2014-02-08 20:59:18 | 0:37:32  |
|          stackoverflow.com | 2014-02-08 20:44:39 | 2014-02-08 20:48:17 | 0:03:38  |
|    ~/Workspaces/prive/wdid | 2014-02-08 21:08:21 | 2014-02-08 22:16:44 | 1:08:23  |
|          mattdickenson.com | 2014-02-08 21:25:06 | 2014-02-08 21:28:01 | 0:02:55  |
|    ~/Workspaces/prive/wdid | 2014-02-08 22:37:21 | 2014-02-08 23:57:26 | 1:20:05  |
+----------------------------+---------------------+---------------------+----------+
|                            |                     |                     | 4:42:31  |
+----------------------------+---------------------+---------------------+----------+
```

See the [documentation of hamster-cli](https://github.com/projecthamster/hamster/blob/master/src/hamster-cli#L350)
for an explanation of the possible (datetime) parameters.

# Dependencies

- [zeitgeist.vim](https://bazaar.launchpad.net/~zeitgeist-dataproviders/zeitgeist-datasources/git/download/head:/vim/zeitgeist.vim/zeitgeist.vim)
- [chrome zeitgeist plugin](https://chrome.google.com/webstore/detail/zeitgeist-plugin/cckhkmhbknngejnoepfopckjlbnpookg)

## TODO

- filter event_types (document/website)

## Thanks

- [Project hamster](https://github.com/projecthamster/hamster/) (I copied the
  datetime paramter parsing from hamster-cli)
- [PrettyTable](https://pypi.python.org/pypi/PrettyTable)
