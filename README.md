###Logging IRC bot, based on: [Twisted IRC Log Bot](http://twistedmatrix.com/documents/current/words/examples/ircLogBot.py)

---

####To Run:

Setup bot configuration in **config.py**

The file has a `Config` class and three subclasses. You may select any
of the subclasses as needed, and update the bot's attributes section of
it, plus any other config values you wish to change.

Modify **run.py** and change `'default'` in `config = config_modes.get('default')()` to your desired config mode, which should be one of:

* `'default'`
* `'dev'`
* `'test'`
* `'deploy'`

Install dependencies with:

    $ pip install -r requirements.txt

Now run the bot with:

    $ python run.py

---

You can send the following commands to the bot in a _PM_:

|Command|Description|Channel|Who|
|---|---|---|---|
|`.help`|List all the commands|PM/Channel|Any user|
|`!`|Queue yourself to ask a question during a session|Channel|Any user|
|`!!`|Remove yourself from question queue during a session|Channel|Any user|
|`!-`|Remove yourself from question queue during a session|Channel|Any user|
|`.givemelogs`|Give you an fpaste link with the latest log|PM/Channel|Any user|
|`.clearqueue`|Clear the question queue|PM/Channel|Admin|
|`.showqueue`|Show the status of the question queue|PM/Channel|Admin|
|`.next`|Ping the next person in the queue to ask their question|PM/Channel|Admin|
|`.masters`|Show the list of all the masters (admins)|PM/Channel|Admin|
|`.add [nick]`|Add `nick` to masters list|PM/Channel|Admin|
|`.rm [nick]`|Remove `nick` from masters list|PM/Channel|Admin|
|`.startclass`|Start logging a class|PM|Admin|
|`.endclass`|Stop logging a class|PM|Admin|
|`.pingall [message]`|Ping present channel members with `message`|PM/Channel|Admin|
|`.link [resource]`|Show the URL of requested `resource`|PM/Channel|Any user|
