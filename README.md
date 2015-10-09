# bottly

## NAME

bot-tly - Up your class with Butler bottly in your IRC Channel

## INSTALLATION && USAGE

Get the source code from GitHub:

     git clone git@github.com:ingydotnet/git-hub

Then run:

    python bottly/bottly.py     # possibly 'python3'

## COMMANDS

These are the commands you can use to interact with bottly.

### Admin Only

**_join <channel>_**
    Joins a specific channel.

**_leave [<channel>]_**
    Leaves a specific channel. Leave defaults to the channel the command was issued in.

**_quit_**
    Disconnects bottly from the IRC Server.

### Trusted and Admin Only

**_hush_**
    Stops bottly from responding to commands available to normal users.

**_unhush_**
    Allows bottly to respond to commands available to normal users.

**_tinyoff_**
    Turns off bottly's automatic URL shortener.

**_tinyon_**
    Turn bottly's automatic URL shortener on.

### Normal Users

**_author_**
    List information about the author.

**_contributors_**
    List information about some of the contributors

**_foo_**
    Simple command that returns "foo" mainly for testing purposes.

**_mail <user> <message>..._**
    Create a new message for bottly to deliver next time the user is online.

**_checkmail_**
    Returns recent messages bottly has waiting for you.

**_isup  <url>_**
    Returns whether a URL is up or down.

**_tiny <url>_**
    Returns a shortened URL using TinyURL, useful for when bottly's automatic URL shortener is turned off

**_uptime_**
    Returns how long bottly has been connected to the server.

### CONFIGURATIONS

Configurations are located in 'config.json' in the root folder of the project.

**_DEBUG_**
    True | False - Turns debugging mode on or off.

**_Admins_**
    Defines a list of nicks which have adminstrative access.

**_Trusted_**
    Defines a list of  nicks which have trusted access (think superuser).

**_Server_**
    Defines which IRC Server you'd like bottly to connect to.

**_Port_**
    Defines which Port you'd like bottly to try to connect on.

**_Channel_**
    Defines a list of IRC Channel you'd like bottly to connect to.

**_BotNick_**
    Defines the nick you'd like bottly to connect with.

**_Trigger_**
    Defines which character preludes the commands.

**_LogDir_**
    Defines which directory to save log files to.

**_LogFile_**
    Defines what file to write logs to.

**_Responses_**
    Defines bottly's responses to certain situations.

    quit: Message displayed when quiting the server
    leave: Message displayed when leaving a channel
    tiny_success: Message displayed on successful URL shorten
    tiny_short:  Message displayed when URL is already shorter
    tiny_failure: Message displayed on failed URL shorten
    more_mail: Message displayed when user has more mail that can be displayed at one time
    no_mail: Message displayed when user has no mail
    hush_on: Message displayed when bottly is hushed
    hush_off: Message displayed when bottly is unhushed
    autotiny_on: Message displayed when automatic URL shortener is activated
    autotiny_off: Message displayed when automatic URL shortener is deactivated
    isup_up: Message displayed when URL is working
    isup_down: Message displayed when URL is inaccessable
    deny: Message displayed when user tries to run elevated commands

## Author

Written by Andrew Dulle <k3kl3r@gmail.com>

## Status

This IRC Bot is in constant development. Being a side project, development will fluctuate but feel free to fork!  Patches/Pull Requests welcome. See the file 'notes/todo' in the main repo if you'd like to see if you can help out.

Find __bottly__ on irc.freenode.net, we're both in #nixheads if  you have any questions or ideas.


