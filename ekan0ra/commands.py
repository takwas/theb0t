"""
    Commands recognisable by our bot.
"""


commands = {
    '.help' : 'list all the commands',
    '!' : 'Queue yourself to ask a question during a session',
    '!!' : 'Remove yourself from question queue during a session',
    '!-' : 'Remove yourself from question queue during a session',
    '.givemelogs' : 'Give you a fpaste link with the latest log',
    '.clearqueue' : 'Clear the ask question queue',
    '.next' : 'ping the person in the queue to ask question',
    '.masters' : 'returns the list of all the masters',
    '.add [nick]' : 'adds the nick to masters list',
    '.rm [nick]' : 'removes the nick from masters list',
    '.startclass' : 'start logging the class',
    '.endclass' : 'ends logging the class',
    '.pingall [message]' : 'pings the message to all',    
    '.link [portal]' : 'Returns the link of the portal'
}
