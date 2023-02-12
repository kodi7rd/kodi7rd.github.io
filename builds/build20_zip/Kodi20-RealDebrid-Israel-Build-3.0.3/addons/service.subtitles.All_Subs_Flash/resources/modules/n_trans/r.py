import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    
    'Connection': 'keep-alive',
    
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'TE': 'trailers',
}

params = (
    #('anno', '3'),
    ('client', 'gtx'),
    ('format', 'html'),
    #('v', '1.0'),
    #('key', ''),
    #('logld', 'vTE_20220105'),
    ('sl', 'auto'),
    ('tl', 'iw'),
    ('tc', '2'),
    ('sr', '1'),
    #('tk', '534305.971426'),
    ('mode', '1'),
    ('q','Hellow')
)

data = [
  ('q', 'Thor, the Thunderer,\nwill deal with these villains.'),
  ('q', 'Huh?'),
  ('q', 'Surrender now and\nI will show mercy.'),
  ('q', 'That makes one of us.'),
  ('q', 'The Mighty Thor,'),
  ('q', 'more like a mighty big id--'),
  ('q', 'Back off, blondie,'),
  ('q', 'or Florence Nightingale here'),
  ('q', 'is gonna get the worst headache of her life.'),
  ('q', 'Have you no honor?'),
  ('q', 'Not even a little.'),
  ('q', 'Then you should be familiar'),
  ('q', 'with attacking a foe from behind.'),
  ('q', 'Thank you.'),
  ('q', 'You have no powers,\nno armor, no weapons'),
  ('q', 'and yet I saw you risk your\nlife to help the wounded.'),
  ('q', 'Why?'),
  ('q', 'Because they needed my help,\nso I helped them.'),
  ('q', 'I&#39;m a paramedic. It&#39;s what I do.'),
  ('q', 'I&#39;m Jane. Jane Foster.'),
  ('q', 'I-- I am--'),
  ('q', 'Thor!'),
  ('q', 'I bear a grim message from thy father Odin.'),
  ('q', 'He calls you home. Asgard is under siege.'),
  ('q', 'Fare thee well, Jane Foster.'),
  ('q', 'Huh.'),
  ('q', 'Bye.'),
  ('q', 'Forward, my Frost Giants.\nStrike deep.'),
  ('q', 'Do not stop until the\nthrone of Asgard belongs'),
  ('q', 'to its rightful lord, Loki.'),
  ('q', 'Mmm.'),
  ('q', 'The Frost Giants march for Odin&#39;s palace.'),
]

response = requests.post('https://translate.googleapis.com/translate_a/t?client=gtx&format=html&sl=auto&mode=1&q=hellow&tl=iw&tc=2&sr=1', headers=headers).content

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.post('https://translate.googleapis.com/translate_a/t?anno=3&client=te&format=html&v=1.0&key&logld=vTE_20220105&sl=auto&tl=iw&tc=2&sr=1&tk=534305.971426&mode=1', headers=headers, data=data).content
print response