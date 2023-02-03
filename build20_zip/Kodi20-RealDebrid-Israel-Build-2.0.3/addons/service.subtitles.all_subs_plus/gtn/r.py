# -*- coding: utf-8 -*-
from google_trans_new import google_translator  
  
translator = google_translator()  
translate_text = translator.translate('สวัสดีจีน',lang_tgt='en')  
print(translate_text)