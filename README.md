Based on: http://twistedmatrix.com/documents/current/words/examples/ircLogBot.py
----

To Run:

Setup bot configuration in config.py

The file has a `Config` class and three subclasses. You may select any
of the subclasses and update the bot's attributes, plus any other config
values you wish to change.

Modify run.py and change `default` (in `config = config_modes.get('default')()`) to your desired config mode: (`'default'`, `'dev'`,
'test'`, `'deploy'`)

Now run the bot:
    $ python run.py

Commands:
Some quick commands you can send to the bot in a _PM_:
`.help`
`.startclass` in the bot's pm.
`.endclass` in bot's pm.
`.pingall` - pingall: [message]
