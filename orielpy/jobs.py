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

    logger.info("Logging system status on defined job interval\n"+ \
    "diskInfo = "+json.dumps(json_disk)+"\n"+ \
    "fansTemps = "+json.dumps(json_sysfiles)+"\n"+ \
    "cpuLoad = "+json.dumps(json_cpu)+"\n"+ \
    "memoryInfo = "+json.dumps(json_mem)+"\n"+ \
    "swapInfo = "+json.dumps(json_swap)+"\n"+ \
    "volumeInfo = "+json.dumps(json_partition)+"\n"+ \
    "networkInfo = "+json.dumps(json_networking))
