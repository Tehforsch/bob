from typing import Dict, Any, List
import shutil
import os
import argparse
from pathlib import Path
import filecmp
import logging

from bob import localConfig, config, util
from bob.exceptions import CompilationError
from bob.paramFile import ParamFile, ConfigFile, InputFile, JobFile


class Simulation:
    def __init__(self, inputFolder: Path, simFolder: Path, substitutions: Dict[str, Any]) -> None:
        self.inputFolder = inputFolder
        self.folder = simFolder
        self.copyFiles()
        self.readFiles()
        self.makeSubstitutions(substitutions)
        self.jobFile.addLocalParameters()
        self.writeFiles()

    def copyFiles(self) -> None:
        shutil.copytree(self.inputFolder, self.folder)

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

    def compileArepo(self, verbose: bool = False) -> None:
        self.copyConfigFile()
        logging.info("Compiling arepo.")
        if config.srcArepoConfigFile.is_file():
            os.remove(config.srcArepoConfigFile)
        process = util.runCommand(config.arepoCompilationCommand, path=localConfig.arepoDir, printOutput=verbose, shell=True)
        if process.returncode != 0:
            raise CompilationError()
        self.copyBinary()
        self.copySource()

    def copyConfigFile(self) -> None:
        targetConfigFile = Path(localConfig.arepoDir, config.configFilename)
        if targetConfigFile.is_file():
            if filecmp.cmp(str(self.configFile.filename), str(targetConfigFile)):
                logging.info("Config file identical, not copying again to preserve compilation state.")
                return
        shutil.copyfile(self.configFile.filename, targetConfigFile)

    def copyBinary(self) -> None:
        sourceFile = Path(localConfig.arepoDir, config.binaryName)
        targetFile = Path(self.folder, config.binaryName)
        shutil.copy(sourceFile, targetFile)

    def copySource(self) -> None:
        for srcFile in config.srcFiles:
            source = Path(localConfig.arepoDir, srcFile)
            target = Path(self.folder, config.sourceOutputFolderName, srcFile)
            if source.is_file():
                shutil.copy(source, target)
            else:
                shutil.copytree(source, target)

    def run(self, args: argparse.Namespace) -> None:
        util.runCommand([localConfig.runJobCommand, str(self.jobFile.filename.name)], path=self.jobFile.filename.parent, shell=False, printOutput=args.verbose)
