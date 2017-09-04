import re, json, os, errno

import requests

from utils import find_between, find_between_r, headers
from get_pic import get_pic

def get_chapter_info(text):
    regex = r'<li><a href="([^"]*)" title="([^"]*)"[^>]*><span>[^>]*<i>([^"]*)</i></span></a></li>'

    l = []
    matches = re.finditer(regex, text)
    for match in matches:
        url = match.group(1)
        title = match.group(2)
        pages = match.group(3)

        l.append((url, title, pages))

    l.reverse()
    return l

def get_comic_info(comic_id):
    r = requests.get('http://www.manhuagui.com/comic/%s/' % comic_id, headers=headers)

    title = find_between(r.text, '<div class="book-title">', '</div>')
    title = re.sub('<[^>]*>', '', title).strip()
    intro = find_between(r.text, '<div id="intro-all" class="none">', '</div>')
    intro = re.sub('<[^>]*>', '', intro).strip()

    print(title)
    print(intro)

    try:
        os.mkdir(title)
    except OSError as e:
        if e.errno != errno.EEXIST: raise
    os.chdir(title)

    index = 0
    i = 0
    while True:
        index = r.text.find(r'''<div class="chapter-list cf mt10" id='chapter-list-0'>''', index + 1)
        if index != -1:
            chapter_title = find_between_r(r.text, '<span>', '</span>', end=index)
            chapter_text = find_between(r.text, r'''<div class="chapter-list cf mt10" id='chapter-list-0'>''', '</div>', index)
            print(chapter_title)
            l = get_chapter_info(chapter_text)

            try:
                os.mkdir(chapter_title)
            except OSError as e:
                if e.errno != errno.EEXIST: raise
            os.chdir(chapter_title)

            for chapter in l:
                get_pic('http://www.manhuagui.com/%s' % chapter[0])
            #with open('chapter-%s-%s.txt' % (i, chapter_title), 'w') as f:
                #json.dump(l, f)
            break
            i += 1

            os.chdir('..')
        else:
            break

    os.chdir('..')

if __name__ == '__main__':
    #comic_id = int(input('Comic ID:'))
    comic_id = 9414

    get_comic_info(comic_id)
