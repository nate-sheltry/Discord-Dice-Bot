def italics(string):
    return f'_{string}_'

def bold(string):
    return f'**{string}**'

def bold_italics(string):
    return f'***{string}***'

def strikethrough(string):
    return f'~~{string}~~'

def inline_code(string):
    return f'`{string}`'

def code_block(string):
    return f'```{string}```'

def block_quote(string):
    return f'> {string}'

def hyperlink(name, url):
    return f'[{name}]({url})'

def mention(name):
    return f'@{name}'
