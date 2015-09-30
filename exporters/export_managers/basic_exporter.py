import yaml
from exporters.export_managers.base_exporter import BaseExporter
from exporters.export_managers.bypass import S3Bypass
from exporters.persistence.persistence_config_dispatcher import PersistenceConfigDispatcher


class BasicExporter(BaseExporter):
    """
    Basic export manager reading configuration a json file. It has bypass support.
    """

    def __init__(self, configuration):
        super(BasicExporter, self).__init__(configuration)

    @staticmethod
    def from_file_configuration(filepath):
        conf_string = open(filepath).read()
        return BasicExporter(yaml.safe_load(conf_string))

    @staticmethod
    def from_persistence_configuration(persistence_uri):
        conf_string = PersistenceConfigDispatcher(persistence_uri).config
        return BasicExporter(conf_string)

    @property
    def bypass_cases(self):
        return [S3Bypass(self.config)]