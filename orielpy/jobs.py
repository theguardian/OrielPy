import orielpy
import json

from cherrystrap import logger
from orielpy.subroutines import subroutines

def logStatus():
    subcall = subroutines()

    completeStatus = []

    json_disk = subcall.diskio_subroutine()
    json_sysfiles = subcall.sysfiles_subroutine()
    json_cpu = subcall.cpuload_subroutine()
    json_mem = subcall.memload_subroutine()
    json_swap = subcall.swapload_subroutine()
    json_partition = subcall.partitions_subroutine()
    json_networking = subcall.networkload_subroutine()

    logger.info("{"+ \
    "\"note\" : \"Logging system status on defined job interval\", "+ \
    "\"diskInfo\" : "+json.dumps(json_disk)+", "+ \
    "\"fansTemps\" : "+json.dumps(json_sysfiles)+", "+ \
    "\"cpuLoad\" : "+json.dumps(json_cpu)+", "+ \
    "\"memoryInfo\" : "+json.dumps(json_mem)+", "+ \
    "\"swapInfo\" : "+json.dumps(json_swap)+", "+ \
    "\"volumeInfo\" : "+json.dumps(json_partition)+", "+ \
    "\"networkInfo\" : "+json.dumps(json_networking)+"}")
