All Subs Plus
==================

Additional info for Ktuvit.me provider

In order to get the encoded password:

1. Open "ktuvit.me" (https://www.ktuvit.me) in the browser
2. Open "developer tools" (https://developers.google.com/web/tools/chrome-devtools/open)  
(in Windows: ctrl+shift+c)
3. Enter this code in the **console**, replace these fields with your login details (MY-PASSWORD,MY@EMAIL.COM) and then execute: 

x = { value: 'MY-PASSWORD' };
loginHandler.EncryptPassword({}, x, 'MY@EMAIL.COM');
copy(x.value); // this will copy your encrtyped password to your clipboard
console.log(`Now past it in the addon's settings at the Encrypted password field`)
4. The encrypt code is now ready to paste it in kodi.

==================

Additional info for AutoSubs feature:

* Make sure that "autosubs" is enabled in the AllSubs_Plus settings.
* It is recommanded also to enable the "Force down" option.
(Otherwise if subtitles are already exist it won't load a new while using 'autosubs')
* If you want to be sure the 'autosubs' feature is running on each play, activate also the "popup" option.
* After updating the settings, restart kodi, because this addon is a service that reloading when kodi starts.
* It seems that there is relevant of the kodi default subtitles service settings for this feature, 
you can set another addon which is not AllSubs_Plus.
* Also it seems that there is relevant of the kodi "Auto download first subtitle" setting for this feature.
