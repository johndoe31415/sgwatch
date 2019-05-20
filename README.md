# sgwatch
sgwatch is an application that watches a directory for creation of new
(savegame) files and then, when they're stable (i.e., don't change anymore in a
certain time interval) creates unique copies of them. This allows unlimited
quicksave slots for example. The parameter is a JSON configuration file that
should be fairly self-explanatory.

## Usage
```
$ cat atom_rpg.json
{
	"directory": "~/.config/unity3d/AtomTeam/Atom",
	"regex": "Save_(?P<sgno>-?\\d+)_v10.as",
	"name": "atom_rpg",
	"restore": "Save_0_v10.as"
}

$ ./sgwatch atom_rpg.json
New savegame: Save_0_v10.as (2019-05-20T17:47:10.531628Z)
New savegame: Save_0_v10.as (2019-05-20T17:47:26.807614Z)
New savegame: Save_0_v10.as (2019-05-20T17:48:36.755556Z)
New savegame: Save_0_v10.as (2019-05-20T18:08:09.366881Z)

$ ./restore atom_rpg.json
 1) Save_0_v10.as   20.05.2019 20:08:00  0:31 h:m
 2) Save_0_v10.as   20.05.2019 19:48:03  0:51 h:m
 3) Save_0_v10.as   20.05.2019 19:47:02  0:52 h:m
 4) Save_0_v10.as   20.05.2019 19:47:01  0:52 h:m
 5) Save_0_v10.as   20.05.2019 19:45:04  0:54 h:m
[...]
```

# License
GNU GPL-3.
