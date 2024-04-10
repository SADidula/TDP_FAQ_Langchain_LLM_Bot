from typing import NoReturn
from models.configurations import Configurator

class Web_Loader:
    """initialize all the components
    in the init function any required url can be added for scrapping purpose
    """    
    def __init__(self, config: Configurator) -> NoReturn:        
        # load all the urls
        self.web_loader_urls: list[str] = config.get_configurations_list('faq configurations')
        
        # load only faq
        self.faq_url: str = config.get_configurations_value('faq configurations', 'faq_url')
            
    def get_sitemap(self) -> list[str]:
        return self.web_loader_urls

    def get_faq_page(self) -> str:
        return self.faq_url
    