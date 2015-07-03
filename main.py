import pkgutil
import os

from lib.util import Pushover

path = os.path.join(os.path.dirname(__file__), "enabled")
base_path = os.path.basename(path)
modules = pkgutil.iter_modules(path=[path])

Pushover.send("Statement Downloader", "running...")

for loader, mod_name, ispkg in modules:
    loaded_mod = __import__(base_path + "." + mod_name, fromlist=[mod_name])
    print "Loading", mod_name
    try:
        loaded_mod.main()
    except Exception as e:
        print "{} failed to run".format(mod_name), e
        continue
