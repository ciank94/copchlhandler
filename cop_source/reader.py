import copernicusmarine as cop
import os
from .logger_config import setup_logger

logger = setup_logger('reader')

class ChlObsData:
    def __init__(self, dataID):
        """Initialize the copDataID class.

        :param dataID: The data identifier.
        :type dataID: str
        """
        logger.info(f"================={self.__class__.__name__}=====================")
        logger.info(f"Initializing {self.__class__.__name__}")
        logger.info(f"DataID: {dataID}")
        cmems_obs_glo_bgc_plankton_files = [
            # Level 3 datasets
            "cmems_obs-oc_glo_bgc-plankton_my_l3-olci-4km_P1D",
        ]
        if dataID in cmems_obs_glo_bgc_plankton_files:
            logger.info(f"dataID matches item in list of cmems_obs_glo_bgc_plankton_files")
        else:
            logger.warning(f"list of cmems_obs_glo_bgc_plankton_files: {cmems_obs_glo_bgc_plankton_files}")
            raise ValueError(
                f"dataID does not match list of cmems_obs_glo_bgc_plankton_files, "
                "please add to list if needed"
            )
        self.dataID = dataID
        split_name = dataID.replace('_', '-').split('-')
        if "P1D" in split_name:
            self.frequency = "daily"
        elif "P1M" in split_name:
            self.frequency= "monthly"
        
        if "l3" in split_name:
            self.level = "3"
        elif "l4" in split_name:
            self.level = "4"

        if "nrt" in split_name:
            self.period = "near-real-time"
        elif "my" in split_name:
            self.period = "multi-year"
        
        if "4km" in split_name:
            self.resolution = "4km"
        elif "300m" in split_name:
            self.resolution = "300m"
        
        self.file_prefix = f"chl_obs_{self.frequency}_L{self.level}_{self.period}_{self.resolution}"
        logger.info(f"Frequency: {self.frequency}")
        logger.info(f"Level: {self.level}")
        logger.info(f"Period: {self.period}")
        logger.info(f"Resolution: {self.resolution}")
        logger.info(f"File prefix: {self.file_prefix}")
        return
    

class Configuration:
    def __init__(self, parse_file):
        logger.info(f"================={self.__class__.__name__}=====================")
        logger.info(f"Initializing {self.__class__.__name__}")
        self.parse_file = parse_file # instance of cmems data class
        if not hasattr(self.parse_file, 'file_prefix') or self.parse_file.file_prefix is None:
            raise AttributeError(f"File prefix is not set")
        return

    def configure_path(self, config_path, output_path):
        # check output path
        if not os.path.exists(output_path):
            raise ValueError(f"Output path does not exist: {output_path}")
        self.output_path = output_path
        logger.info(f"Output path: {output_path}")
        self.credentials_file=config_path + ".copernicusmarine-credentials"
        # check credentials file
        if not os.path.exists(self.credentials_file):
            raise ValueError(f"Credentials file does not exist: {self.credentials_file}")
        logger.info(f"Credentials file: {self.credentials_file}")
        return

    def configure_time(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        logger.info(f"Start date: {self.start_date}")
        logger.info(f"End date: {self.end_date}")
        return

    def configure_domain(self, lon_bounds, lat_bounds):
        self.lon_bounds = lon_bounds
        self.lat_bounds = lat_bounds
        logger.info(f"Longitude bounds: {self.lon_bounds}")
        logger.info(f"Latitude bounds: {self.lat_bounds}")
        return

    def configure_variable(self, variables):
        # Retrieve the dataset using the data ID
        self.variables = variables
        logger.info(f"Variables: {self.variables}")
        config_prefix = self.parse_file.file_prefix + "_" + self.start_date[:10] + "_to_" + self.end_date[:10] + ".nc"
        self.output_file = os.path.join(self.output_path, config_prefix)
        logger.info(f"Output path: {self.output_file}")
        return

class DownloadData:
    def __init__(self, config):
        logger.info(f"================={self.__class__.__name__}=====================")
        logger.info(f"Initializing {self.__class__.__name__}")
        self.config = config
        self.request_data()
        return

    def request_data(self):
         cop.subset(
            dataset_id=self.config.parse_file.dataID,
            variables=self.config.variables,
            start_datetime=self.config.start_date,
            end_datetime=self.config.end_date,
            minimum_longitude=self.config.lon_bounds[0],
            maximum_longitude=self.config.lon_bounds[1],
            minimum_latitude=self.config.lat_bounds[0],
            maximum_latitude=self.config.lat_bounds[1],
            #minimum_depth=self.min_depth,
            #maximum_depth=self.max_depth,
            output_filename=self.config.output_file,
            credentials_file=self.config.credentials_file,
            force_download=True,
        )