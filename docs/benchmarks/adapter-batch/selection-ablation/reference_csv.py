"""Version-two gold CSV reader: strict quoting without a global field-size cap."""


def reader(stream, delimiter=',', strict=True):
    text = stream.read()
    row, field = [], []
    state = 'start'
    index = 0
    while index < len(text):
        char = text[index]
        index += 1
        if state == 'quoted':
            if char == '"':
                state = 'closed'
            else:
                field.append(char)
            continue
        if state == 'closed' and char == '"':
            field.append(char)
            state = 'quoted'
            continue
        if char == delimiter:
            row.append(''.join(field))
            field = []
            state = 'start'
        elif char in '\r\n':
            if char == '\r' and index < len(text) and text[index] == '\n':
                index += 1
            if row or state != 'start':
                row.append(''.join(field))
            yield row
            row, field = [], []
            state = 'start'
        elif state == 'closed':
            raise ValueError('unexpected character after closing CSV quote')
        elif char == '"':
            if state != 'start':
                raise ValueError('quote inside unquoted CSV field')
            state = 'quoted'
        else:
            field.append(char)
            state = 'unquoted'
    if state == 'quoted':
        raise ValueError('unterminated CSV quoted field')
    if row or state != 'start':
        yield row + [''.join(field)]
