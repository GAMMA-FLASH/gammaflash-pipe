from pathlib import Path
from rta_dq_pipe.output.OutputHandler import OutputHandler
from rta_dq_pipe.utils.PipeLoggerConfig import PipeLoggerConfig
from gammaflash.datasource.filesystem.GfHandler import GfHandler

class OutputToHdf5(OutputHandler):

    def __init__(self, outputLoc, overwrite, obsId, runId, suffix=""):
            super().__init__(outputLoc, obsId, runId)
            self.outputLoc = Path(self.outputLoc)
            self.outputLoc.mkdir(parents=True, exist_ok=True)
            self.gfHandler = GfHandler()
            self.overwrite = overwrite
            self.count = 0
            self.suffix = suffix
            self.filenamePrefix = self.suffix
            self.update(self.obsId, self.runId)
            self.logger = PipeLoggerConfig().getLogger(__name__)

    def update(self, obsId=None, runId=None):
        self.obsId = obsId
        self.runId = runId

        if self.runId is not None and self.obsId is not None:
            self.filenamePrefix = f"obsId_{str(self.obsId)}_runId_{str(self.runId)}_{self.suffix}"
            
        elif self.obsId is not None and self.runId is None:
            self.filenamePrefix = f"obsId_{str(self.obsId)}_{self.suffix}"

        elif self.obsId is None and self.runId is not None:
            self.filenamePrefix = f"runId_{str(self.runId)}_{self.suffix}"

    def save(self, data):

            filepath = self.outputLoc.joinpath(self.filenamePrefix)
            
            if not self.overwrite:
                filepath = Path(str(filepath) + "_" + str(self.count))
                self.count += 1

            filepath = filepath.with_suffix(".h5")

            self.logger.debug(f"Saving {filepath} Overwrite = {self.overwrite}")
            
            self.gfHandler.write(filepath, data)