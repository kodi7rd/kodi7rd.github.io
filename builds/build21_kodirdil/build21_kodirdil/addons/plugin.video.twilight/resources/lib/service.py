# -*- coding: utf-8 -*-
from modules import service_functions
from modules.kodi_utils import Thread, xbmc_monitor, logger, local_string as ls

twilight_str = ls(32036).upper()
on_notification_actions = service_functions.OnNotificationActions()
on_settings_changed_actions = service_functions.OnSettingsChangedActions()

class TwilightMonitor(xbmc_monitor):
	def __init__ (self):
		xbmc_monitor.__init__(self)
		self.startUpServices()

	def startUpServices(self):
		try: service_functions.InitializeDatabases().run()
		except: pass
		try: service_functions.CheckSettings().run()
		except: pass
		# try: service_functions.FirstRunActions().run()
		# except: pass
		# try: service_functions.ReuseLanguageInvokerCheck().run()
		# except: pass
		Thread(target=service_functions.TraktMonitor().run).start()
		Thread(target=service_functions.CustomActions().run).start()
		Thread(target=service_functions.CustomFonts().run).start()
		# Thread(target=service_functions.PremiumExpiryCheck().run).start()

		############KODI-RD-IL###################
		try:
			from indexers import premiumize, real_debrid
			Thread(target=premiumize.active_days_notify_only()).start()
			Thread(target=real_debrid.active_days_notify_only()).start()
		except:
			pass
		#########################################

		# try: service_functions.ClearSubs().run()
		# except: pass
		# try: service_functions.AutoRun().run()
		# except: pass
		Thread(target=service_functions.DatabaseMaintenance().run).start()
		# service_functions.UpdateCheck().run()

	def onSettingsChanged(self):
		on_settings_changed_actions.run()

	def onNotification(self, sender, method, data):
		on_notification_actions.run(sender, method, data)

logger(twilight_str, 'Main Monitor Service Starting')
logger(twilight_str, 'Settings Monitor Service Starting')
TwilightMonitor().waitForAbort()
logger(twilight_str, 'Settings Monitor Service Finished')
logger(twilight_str, 'Main Monitor Service Finished')