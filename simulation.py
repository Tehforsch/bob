from typing import Dict, Any
import shutil
import config
from paramFile import getParamFile
from pathlib import Path
import filecmp
import logging
import util
from exceptions import CompilationError
import localConfig


class Simulation:
    def __init__(self, inputFolder: Path, simFolder: Path, substitutions: Dict[str, Any]) -> None:
        self.inputFolder = inputFolder
        self.folder = simFolder
        self.copyFiles()
        self.readFiles()
        self.jobFile.addLocalParameters()
        self.makeSubstitutions(substitutions)
        self.writeFiles()

    def copyFiles(self) -> None:
        shutil.copytree(self.inputFolder, self.folder)

    def readFiles(self) -> None:
        self.configFile = getParamFile(Path(self.folder, config.configFilename))
        self.inputFile = getParamFile(Path(self.folder, config.inputFilename))
        self.jobFile = getParamFile(Path(self.folder, config.jobFilename))
        self.paramFiles = [self.configFile, self.inputFile, self.jobFile]

    def writeFiles(self) -> None:
        for paramFile in self.paramFiles:
            paramFile.write()

    def makeSubstitutions(self, substitutions: Dict[str, Any]) -> None:
        for (k, v) in substitutions.items():
            self.substituteParameter(k, v)

    def substituteParameter(self, k: str, v: Any) -> None:
        paramFilesWithThisParameter = [paramFile for paramFile in self.paramFiles if k in paramFile]
        assert len(paramFilesWithThisParameter) == 1, f"Multiple files contain this parameter: {k}: {paramFilesWithThisParameter}"
        paramFile = paramFilesWithThisParameter[0]
        paramFile[k] = v

    def compileArepo(self, verbose=False) -> None:
        self.copyConfigFile()
        logging.info("Compiling arepo.")
        process = util.runCommand(config.arepoCompilationCommand, path=config.arepoDir, printOutput=verbose, shell=True)
        if process.returncode != 0:
            raise CompilationError()
        self.copyBinary()

    def copyConfigFile(self) -> None:
        targetConfigFile = Path(config.arepoDir, config.configFilename)
        if targetConfigFile.is_file():
            if filecmp.cmp(self.configFile.filename, targetConfigFile):
                logging.info("Config file identical, not copying again to preserve compilation state.")
                return None
        shutil.copyfile(self.configFile.filename, targetConfigFile)

    def copyBinary(self):
        sourceFile = Path(config.arepoDir, config.binaryName)
        targetFile = Path(self.folder, config.binaryName)
        shutil.copyfile(sourceFile, targetFile)

    def run(self, args) -> None:
        pass
