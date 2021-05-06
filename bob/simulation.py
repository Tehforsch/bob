import numpy as np
from typing import Dict, Any, List
import shutil
import os
import argparse
from pathlib import Path
import filecmp
import logging
import re

from bob import localConfig, config, util
from bob.exceptions import CompilationError
from bob.paramFile import ConfigFile, InputFile, JobFile, IcsParamFile, MiscFile
from bob.util import memoize
from bob.params import Params
from bob.snapshot import Snapshot
from bob.sources import Sources, getSourcesFromParamFile


class Simulation:
    def __init__(self, folder: Path, substitutions: Dict[str, Any]) -> None:
        self.folder = folder
        self.params = self.readFiles()
        self.params.updateParams(substitutions)
        self.params.setDerivedParams()
        self.binaryFile = Path(self.folder, config.binaryName)

    def readFiles(self) -> Params:
        self.configFile = ConfigFile(Path(self.folder, config.configFilename))
        self.inputFile = InputFile(Path(self.folder, config.inputFilename))
        self.jobFile = JobFile(Path(self.folder, config.jobFilename), localConfig.jobParams)
        paramFileList = [self.configFile, self.inputFile, self.jobFile]
        icsFilePath = Path(self.folder, config.icsParamFileName)
        if icsFilePath.is_file():
            self.icsFile = IcsParamFile(icsFilePath)
            paramFileList.append(self.icsFile)
        return Params(paramFileList)

    def compileArepo(self, quiet: bool = False) -> None:
        self.copyConfigFile()
        logging.info("Compiling arepo.")
        if config.srcArepoConfigFile.is_file():
            os.remove(config.srcArepoConfigFile)
        process = util.runCommand(config.arepoCompilationCommand, path=localConfig.arepoDir, printOutput=not quiet, shell=True)
        if process.returncode != 0:
            raise CompilationError()
        self.copyBinary()
        self.copySource()
        self.copyArepoconfig()

    def copyConfigFile(self) -> None:
        targetConfigFile = Path(localConfig.arepoDir, config.configFilename)
        if targetConfigFile.is_file():
            if filecmp.cmp(str(self.configFile.filename), str(targetConfigFile)):
                logging.info("Config file identical, not copying again to preserve compilation state.")
                return
        shutil.copyfile(self.configFile.filename, targetConfigFile)

    def copyBinary(self) -> None:
        sourceFile = Path(localConfig.arepoDir, config.binaryName)
        shutil.copy(sourceFile, self.binaryFile)

    def copySource(self) -> None:
        for srcFile in config.srcFiles:
            source = Path(localConfig.arepoDir, srcFile)
            target = Path(self.folder, config.sourceOutputFolderName, srcFile)
            if source.is_file():
                shutil.copy(source, target)
            else:
                shutil.copytree(source, target)

    def copyArepoconfig(self) -> None:
        """Copy the arepoconfig.h file. This file is generated from the Config.sh when arepo compiles
        and is necessary in the src folder if clangd is supposed to understand the code at all."""
        source = Path(localConfig.arepoDir, config.arepoConfigBuildFile)
        target = Path(localConfig.arepoDir, config.arepoConfigSrcFile)
        shutil.copy(source, target)

    def run(self, verbose: bool) -> None:
        assert self.binaryFile.is_file(), "Binary does not exist. Not starting job. Did you forget to specify -m (tell bob to compile arepo)?"
        util.runCommand([localConfig.runJobCommand, str(self.jobFile.filename.name)], path=self.jobFile.filename.parent, shell=False, printOutput=verbose)

    @property  # type: ignore
    def name(self) -> str:
        return self.folder.name

    @property  # type: ignore
    @memoize
    def log(self) -> List[str]:
        with Path(self.folder, self.jobFile["logFile"]).open("r") as f:
            return f.readlines()

    @property
    def runTime(self) -> float:
        for line in self.log[::-1]:
            match = re.match(config.runTimePattern, line)
            if match is not None:
                return float(match.groups()[0])
        # assert False, f"Could not read runtime from log. Did the simulation finish? ({str(self)})"
        return None

    def __repr__(self) -> str:
        return f"Sim{self.name}"

    @property
    def outputDir(self) -> Path:
        return Path(self.folder, self.params["OutputDir"])

    @property
    def snapshots(self) -> List[Snapshot]:
        snapshotFileBase = self.params["SnapshotFileBase"]
        snapshotGlob = "{}_*.hdf5".format(snapshotFileBase)
        snapshotFiles = list(self.outputDir.glob(snapshotGlob))

        def getNumber(name: Path) -> int:
            nameRep = str(name).replace("{}_".format(snapshotFileBase), "")
            nameRep = nameRep.replace(".hdf5", "")
            nameRep = nameRep.replace(str(self.outputDir), "")
            nameRep = nameRep.replace("/", "")
            # return int(nameRep)
            return nameRep

        snapshotFiles.sort(key=getNumber)
        return [Snapshot(self, s) for s in snapshotFiles]

    def subboxCoords(self) -> (np.ndarray, np.ndarray):
        with open(Path(self.folder, self.params["SubboxCoordinatesPath"])) as f:
            lines = f.readlines()
            assert len(lines) == 1
            minX, maxX, minY, maxY, minZ, maxZ = [float(x) for x in lines[0].split(" ")]
            return [np.array([minX, minY, minZ]), np.array([maxX, maxY, maxZ])]

    @property
    def resolution(self) -> int:
        return int(self.params["InitCondFile"].replace("ics_", ""))

    @property  # type: ignore
    def sources(self) -> Sources:
        if self.params["SX_SOURCES"] == 10:
            return Sources(Path(self.folder, self.params["TestSrcFile"]))
        elif self.params["SX_SOURCES"] == 9:
            return getSourcesFromParamFile(self)
        else:
            raise ValueError("This is not implemented yet for actual sink/star particles")

    def __hash__(self) -> int:
        return str(self.folder).__hash__()

    def __eq__(self, sim2: "Simulation") -> bool:
        return self.folder == sim2.folder
