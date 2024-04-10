from typing import NoReturn
import configparser

class Configurator:
    
    def __init__(self) -> NoReturn:
        self.configParser = configparser.RawConfigParser()
        configFilePath = r'.config'
        self.configParser.read(configFilePath)
        
    def get_configurations_value(self, section: str, option: str) -> str:
        return self.configParser[section][option]
    
    def get_configurations_list(self, section: str) -> list[str]:
        sitemap: list[str] = []
        for option in self.configParser.options(section):
            sitemap.append(self.configParser[section][option])
        return sitemap