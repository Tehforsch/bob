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
from bob.paramFile import ParamFile, ConfigFile, InputFile, JobFile
from bob.util import memoize


class Simulation:
    def __init__(self, args: argparse.Namespace, name: str, substitutions: Dict[str, Any] = None) -> None:
        self.name = name
        if args.create:
            logging.info(f"Creating sim {name}")
        else:
            logging.info(f"Loading sim {name}")
        self.folder = Path(args.simFolder, self.name)
        if args.delete:
            self.deleteFiles()
        if args.create:
            self.copyFiles(args.inputFolder)
        self.readFiles()
        if args.create:
            self.makeSubstitutions(substitutions)
        self.jobFile.addLocalParameters()
        if args.create:
            self.writeFiles()
        self.binaryFile = Path(self.folder, config.binaryName)

    def deleteFiles(self) -> None:
        shutil.rmtree(self.folder)

    def copyFiles(self, inputFolder) -> None:
        shutil.copytree(inputFolder, self.folder)

    def readFiles(self) -> None:
        self.configFile = ConfigFile(Path(self.folder, config.configFilename))
        self.inputFile = InputFile(Path(self.folder, config.inputFilename))
        self.jobFile = JobFile(Path(self.folder, config.jobFilename))
        self.paramFiles: List[ParamFile] = [self.configFile, self.inputFile, self.jobFile]

    def writeFiles(self) -> None:
        for paramFile in self.paramFiles:
            paramFile.write()

    def makeSubstitutions(self, substitutions: Dict[str, Any]) -> None:
        for (k, v) in substitutions.items():
            self.substituteParameter(k, v)

    def substituteParameter(self, k: str, v: Any) -> None:
        paramFilesWithThisParameter = [paramFile for paramFile in self.paramFiles if k in paramFile]
        assert len(paramFilesWithThisParameter) != 0, f"No file contains this parameter: {k}"
        assert len(paramFilesWithThisParameter) == 1, f"Multiple files contain this parameter: {k}: {paramFilesWithThisParameter}"
        paramFile = paramFilesWithThisParameter[0]
        paramFile[k] = v

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

    def run(self, args: argparse.Namespace) -> None:
        assert self.binaryFile.is_file(), "Binary does not exist. Not starting job. Did you forget to specify -m (tell bob to compile arepo)?"

        util.runCommand([localConfig.runJobCommand, str(self.jobFile.filename.name)], path=self.jobFile.filename.parent, shell=False, printOutput=args.verbose)

    @property
    def params(self) -> Dict[str, Any]:
        return dict((k, v) for paramFile in self.paramFiles for (k, v) in paramFile.items())

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
        assert False, f"Could not read runtime from log. Did the simulation finish? ({str(self)})"

    def __repr__(self) -> str:
        return f"Sim{self.name}"
