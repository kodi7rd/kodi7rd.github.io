from resources.modules.n_trans import srt

    
def translate_now(txt):
    fixed_sub=srt.parse(txt)
    all_text=[]
    count=0
    for items in fixed_sub:
        
        all_text.append(items.content)
        count+=1
    
    return '(1)'.join(all_text)
    
def translate_all(txt):
    
    sub_file=txt
 
    text=translate_now(sub_file)


    from gtn.google_trans_new import google_translator  
      
    translator = google_translator()  


    all_text_p1=[]
    all_data=''

    counter=0




    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]

    ax2=split_string(text,3000)
    f_sub_pre=''
    xx=0

    for items in ax2:
        
         
         translation=translator.translate(items, lang_tgt='he')
         f_sub_pre=f_sub_pre+translation
         xx+=1
    f_sub_pre=f_sub_pre.replace('( 1)','(1)').replace('(1 )','(1)').replace('( 1 )','(1)').replace(' 1)','(1)').replace('(1 ','(1)')

    fixed_sub=srt.parse(sub_file)
    all_text=[]
    count=0
    f_sub_pre_arr=f_sub_pre.split('(1)')

    i=0
    all_items=[]



    for items in fixed_sub:
        
        
        items.content=f_sub_pre_arr[i]
        
        all_items.append(items)
       
        i+=1

    f_result=srt.compose(all_items)
    return  (f_result)