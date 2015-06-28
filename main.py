import pkgutil
import os
import datetime

path = os.path.join(os.path.dirname(__file__), "enabled")
base_path =  os.path.basename(path)
modules = pkgutil.iter_modules(path=[path])

print datetime.datetime.now(), "running..."

for loader, mod_name, ispkg in modules:
    loaded_mod = __import__(base_path + "." + mod_name, fromlist=[mod_name])
    print "Loading", mod_name
    loaded_mod.main()
