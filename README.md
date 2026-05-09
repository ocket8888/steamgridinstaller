# steamgridinstaller
`steamgridinstaller` provides a command-line interface for easily downloading and installing your SteamgridDB collection.

## Installation
`steamgridinstaller` is packaged for use with `pip` - but it requires Python 3.10 or later!

To install, simply use `pip install .` from within the project directory. Or, if using a released wheel file, `pip install /path/to/steamgridinstaller-x.y.z-py3-none-any.whl`.

You also don't need to install it to use it - but you do need to install the prerequisite `requests` anyway.

## Usage
When installed, a runnable command `steamgrid` is provided.

`steamgrid [-h] [-o OUTPUTDIRECTORY] [-O OVERRIDE] collection ID`

**collection ID**
> The ID of the SteamgridDB collection you want to install. You can find this at the end of the URL when viewing a collection in a browser.

`steamgrid` will attempt to find games that closely resemble the names on SteamGridDB. For example, the game listed on SteamGridDB as
"*Ace Combat 7: Skies Unknown*" is known to Steam as "*ACE COMBAT™ 7: SKIES UNKNOWN*". `steamgrid` will resolve this, but it will
issue a warning letting you know it has done so. It may get things wrong and may fail to find some unlisted games. To fix this, you
must use the `-O`/`--override` option to manually specify the ID. Although I've gone to great pains to ensure that this doesn't happen
(except for unlisted games nothing I can do about that) so hopefully you won't need to.

### Options
`-h, --help`
> Show a help message and exit.

`-o, --output-directory OUTPUTDIRECTORY`
> Sets the output directory. The default location is to look for a Steam user under `~/.local/share/Steam/userdata` and
> place it there.
> This must be the path to the directory containing Steam users - NOT the folder where you want the grids to go!

`-O, --override OVERRIDE`
> Format: `name=ID`.
> Overrides an association between a (SteamgridDB) game name and a numeric (Steam) game ID. This is useful when the
> closest match is incorrect or when a game is unlisted (e.g. *The 7th Guest*) and we won't be able to find it through
> the Steam API, or for non-Steam games.

`-v, --version`
> Print version information and exit.
