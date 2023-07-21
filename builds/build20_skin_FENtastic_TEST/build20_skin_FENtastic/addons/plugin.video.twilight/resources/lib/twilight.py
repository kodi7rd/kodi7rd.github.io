# -*- coding: utf-8 -*-
import sys
from modules.router import routing, sys_exit_check, remake_properties_check

routing(sys)
if sys_exit_check(): sys.exit(1)
remake_properties_check()
