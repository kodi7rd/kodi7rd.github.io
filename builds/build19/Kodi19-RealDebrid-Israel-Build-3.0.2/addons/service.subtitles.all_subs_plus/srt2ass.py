# coding:utf-8
import sys
import os
import re,xbmc,json
import codecs,logging
from xbmcaddon import Addon

#import SubsceneUtilities
#def get_xbmc_setting():
MyAddon = Addon()
new = '"subtitles.font"'
value='["English QWERTY|Hebrew QWERTY"]'
query = '{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":%s}, "id":1}' % (new)
try:
  response = xbmc.executeJSONRPC(query)
  json_response=json.loads(response)

  font=json_response['result']['value'].split(".")[0]

except:
  font='ariel'

new = '"subtitles.height"'
value='["English QWERTY|Hebrew QWERTY"]'
query = '{"jsonrpc":"2.0", "method":"Settings.GetSettingValue","params":{"setting":%s}, "id":1}' % (new)
response = xbmc.executeJSONRPC(query)
json_response=json.loads(response)


def fileopen(input_file):
    encodings = ["gb2312", "gbk", 'utf-16', "cp1252",  "big5", "utf-8"]
    tmp = ''
    for enc in encodings:
        try:
            with codecs.open(input_file, mode="rb", encoding=enc) as fd:
                tmp = fd.read()
                break
        except:
            #SubsceneUtilities.log('SRT2ASS: ', enc + ' failed', 2)
            #print enc + ' failed'
            continue
    return [tmp, enc]


def srt2ass(input_file,all_setting):
    if  all_setting["background"]== 'true':
       background='3'
    else:
      background='1'

    if  all_setting["color"]== "0":
     
       color='&H00FFFFFF'#White
    elif  all_setting["color"]== "1":
      color='&H00FE0009'#blue
    elif  all_setting["color"]=="2":
      color='&H000000FF'#red
    elif  all_setting["color"]== "3":
      color='&H008E8E8E'#gray
    elif  all_setting["color"]== "4":
      color='&H0000F6FF'#yellow

    if  all_setting["background_level"]== "0":
       background_level='&HC1000000'#Bright
    if  all_setting["background_level"]== "1":
       background_level='&H82050505'#Gray
    if  all_setting["background_level"]=="2":
       background_level='&H00000000'#black

    if  all_setting["bold"]== 'true':
       bold='-1'
    else:
      bold='0'
    size=all_setting["size"]
    if '.ass' in input_file:
        return input_file
    output_file = '.'.join(input_file.split('.')[:-1])
    output_file += '.ass'
    if not os.path.isfile(input_file):
       
        return
    head_str = '''[Script Info]
; This is an Advanced Sub Station Alpha v4+ script.
Title: 
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SubStyle,{0},{1},{2},&H00FFFFFF,{3},{4},{5},0,0,0,100,100,0,0,{6},2,1,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text'''.format(font,str(size),color,background_level,background_level,bold,background)

    src = fileopen(input_file)
    tmp = src[0]
    tmp = tmp.replace("\r", "")
    lines = tmp.split("\n")
    subLines = ''
    tmpLines = ''
    lineCount = 0

    for line in lines:
        line = line.replace(u'\xef\xbb\xbf', '')
        if re.match('^\d+$', line):
            if tmpLines:
                subLines += tmpLines + "\n"
            tmpLines = ''
            lineCount = 0
            continue
        else:
            if line:
                if re.match('-?\d\d:\d\d:\d\d', line):
                    line = line.replace('-0', '0')
                    tmpLines += 'Dialogue: 0,' + line + ',SubStyle,,0,0,0,,'
                    lineCount += 1
                else:
                    if lineCount < 2:
                        tmpLines += line
                        lineCount += 1
                    else:
                        tmpLines += '\n' + line
                        lineCount += 1

    subLines += tmpLines + "\n"

    subLines = re.sub(r'-?\d(\d:\d{2}:\d{2}),(\d{2})\d', '\\1.\\2', subLines)
    subLines = re.sub(r'\s+-->\s+', ',', subLines)
    # replace style
    subLines = re.sub(r'<([ubi])>', "{\\\\\g<1>1}", subLines)
    subLines = re.sub(r'</([ubi])>', "{\\\\\g<1>0}", subLines)
    subLines = re.sub(r'<font\s+color="?#(\w{2})(\w{2})(\w{2})"?>', "{\\\\c&H\\3\\2\\1&}", subLines)
    subLines = re.sub(r'</font>', "", subLines)

    output_str = head_str + '\n' + subLines
    output_str = output_str.encode(src[1])
    
    with open(output_file, 'wb') as output:
        output.write(output_str)
    
    output_file = output_file.replace('\\', '\\\\')
    output_file = output_file.replace('/', '//')
    return output_file


#if len(sys.argv)>1:
#    for name in sys.argv[1:]:
#        srt2ass(name)
#srt2ass('./resources/lib/z2.srt')