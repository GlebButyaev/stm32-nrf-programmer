#!/usr/bin/env python3
import configparser
import subprocess
import os


def stmprog(report: dict, config: configparser) -> None:
    try:
        hexpath = os.path.abspath(os.getcwd()) + "\\prog\\"
        # argstr = " -c port=SWD mode=UR freq=4000 -w " + hexpath + config.get("PROGRAMMING", "stm_file") + " -v"
        res = subprocess.call([config.get("PROGRAMMING", "stm_prog_cli"),
            '-c port=SWD mode=UR freq=4000',
            '-w ' + hexpath + config.get("PROGRAMMING", "stm_file")+' ',
            '-v'])
        if res:
            raise RuntimeError(f"STM32, ошибка программирования {res}")
        report["progfw"]["stm"] = "oк"
        print("STM32 programming - ok")
    except Exception as E:
        report["progfw"]["stm"] = str(E)
        # print(E)
        raise E


def nrfprog(report: dict, config: configparser) -> None:
    try:
        hexpath = os.path.abspath(os.getcwd()) + "\\prog\\"
        res = subprocess.call([config.get("PROGRAMMING", "nrf_prog_cli"),
           "-openprj" + hexpath + config.get("PROGRAMMING", "nrf_jflash"),
           "-open" + hexpath + config.get("PROGRAMMING", "nrfsd_file"),
           "-connect", "-auto", "-exit"])
        if res:
            raise RuntimeError(f"nRF, ошибка программирования SD {res}")
        res = subprocess.call([config.get("PROGRAMMING", "nrf_prog_cli"),
           "-openprj" + hexpath + config.get("PROGRAMMING", "nrf_jflash"),
           "-open" + hexpath + config.get("PROGRAMMING", "nrfapp_file"),
           "-connect", "-programverify", "-exit"])
        if res:
            raise RuntimeError(f"nRF, ошибка программирования приложения {res}")
        report["progfw"]["nrf"] = "ok"
        print("nRF programming - ok")
    except Exception as E:
        report["progfw"]["nrf"] = str(E)
        # print(E)
        raise E