headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

def find_between(s, first, last, begin=0):
    try:
        start = s.index(first, begin) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ''

def find_between_r(s, first, last, begin=0, end=0):
    try:
        start = s.rindex(first, begin, end) + len(first)
        end = s.rindex(last, start, end)
        return s[start:end]
    except ValueError:
        return ''
