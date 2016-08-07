import os
import json

from . import seqresults 

package_path = __path__[0]
CONF_FILE = os.path.join(package_path,"dnanexus_conf.json")

fh = open(CONF_FILE,'r')
JSON_CONF = json.load(fh)

del package_path,fh,json
