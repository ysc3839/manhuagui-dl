import json, os, errno, threading

import requests
import execjs

from utils import find_between, headers

servers = [
    'i.hamreus.com:8080',
    'us.hamreus.com:8080',
    'dx.hamreus.com:8080',
    'eu.hamreus.com:8080',
    'lt.hamreus.com:8080'
]

LZjs = r'''var LZString=(function(){var f=String.fromCharCode;var keyStrBase64="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";var baseReverseDic={};function getBaseValue(alphabet,character){if(!baseReverseDic[alphabet]){baseReverseDic[alphabet]={};for(var i=0;i<alphabet.length;i++){baseReverseDic[alphabet][alphabet.charAt(i)]=i}}return baseReverseDic[alphabet][character]}var LZString={decompressFromBase64:function(input){if(input==null)return"";if(input=="")return null;return LZString._0(input.length,32,function(index){return getBaseValue(keyStrBase64,input.charAt(index))})},_0:function(length,resetValue,getNextValue){var dictionary=[],next,enlargeIn=4,dictSize=4,numBits=3,entry="",result=[],i,w,bits,resb,maxpower,power,c,data={val:getNextValue(0),position:resetValue,index:1};for(i=0;i<3;i+=1){dictionary[i]=i}bits=0;maxpower=Math.pow(2,2);power=1;while(power!=maxpower){resb=data.val&data.position;data.position>>=1;if(data.position==0){data.position=resetValue;data.val=getNextValue(data.index++)}bits|=(resb>0?1:0)*power;power<<=1}switch(next=bits){case 0:bits=0;maxpower=Math.pow(2,8);power=1;while(power!=maxpower){resb=data.val&data.position;data.position>>=1;if(data.position==0){data.position=resetValue;data.val=getNextValue(data.index++)}bits|=(resb>0?1:0)*power;power<<=1}c=f(bits);break;case 1:bits=0;maxpower=Math.pow(2,16);power=1;while(power!=maxpower){resb=data.val&data.position;data.position>>=1;if(data.position==0){data.position=resetValue;data.val=getNextValue(data.index++)}bits|=(resb>0?1:0)*power;power<<=1}c=f(bits);break;case 2:return""}dictionary[3]=c;w=c;result.push(c);while(true){if(data.index>length){return""}bits=0;maxpower=Math.pow(2,numBits);power=1;while(power!=maxpower){resb=data.val&data.position;data.position>>=1;if(data.position==0){data.position=resetValue;data.val=getNextValue(data.index++)}bits|=(resb>0?1:0)*power;power<<=1}switch(c=bits){case 0:bits=0;maxpower=Math.pow(2,8);power=1;while(power!=maxpower){resb=data.val&data.position;data.position>>=1;if(data.position==0){data.position=resetValue;data.val=getNextValue(data.index++)}bits|=(resb>0?1:0)*power;power<<=1}dictionary[dictSize++]=f(bits);c=dictSize-1;enlargeIn--;break;case 1:bits=0;maxpower=Math.pow(2,16);power=1;while(power!=maxpower){resb=data.val&data.position;data.position>>=1;if(data.position==0){data.position=resetValue;data.val=getNextValue(data.index++)}bits|=(resb>0?1:0)*power;power<<=1}dictionary[dictSize++]=f(bits);c=dictSize-1;enlargeIn--;break;case 2:return result.join('')}if(enlargeIn==0){enlargeIn=Math.pow(2,numBits);numBits++}if(dictionary[c]){entry=dictionary[c]}else{if(c===dictSize){entry=w+w.charAt(0)}else{return null}}result.push(entry);dictionary[dictSize++]=w+entry.charAt(0);enlargeIn--;w=entry;if(enlargeIn==0){enlargeIn=Math.pow(2,numBits);numBits++}}}};return LZString})();String.prototype.splic=function(f){return LZString.decompressFromBase64(this).split(f)};'''

def dlfile(s, url, _headers, dirname, filename):
    r = s.get(url, headers=_headers)

    with open(dirname + '/' + filename, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print('%s: OK!' % filename)

def get_pic(url):
    s = requests.Session()

    r = s.get(url, headers=headers)

    js = find_between(r.text, r'["\x65\x76\x61\x6c"]', '</script>')
    info = execjs.compile(LZjs).eval(js)
    info = find_between(info, 'cInfo=', '||{};')
    info = json.loads(info)

    print(info)

    name = info['cname']
    path = info['path']
    pages = info['len']

    dir_name = '%s-%sp' % (name, pages)
    try:
        os.mkdir(dir_name)
    except OSError as e:
        if e.errno != errno.EEXIST: raise

    args_list = []
    i = 0
    for filename in info['files']:
        i += 1
        if filename.endswith('.webp'):
            filename = filename[:-5]

        pic_url = 'http://{}{}{}'.format(servers[0], path, filename)
        print(pic_url)

        _headers = headers
        _headers['referer'] = url

        ext = os.path.splitext(filename)[1]
        args_list.append((s, pic_url, _headers, dir_name, '%s%s' % (i, ext)))

    threads = [threading.Thread(target=dlfile, args=a) for a in args_list]
    [t.start() for t in threads]
    [t.join() for t in threads]

if __name__ == '__main__':
    _url = 'http://www.manhuagui.com/comic/9414/94568.html'

    get_pic(_url)
