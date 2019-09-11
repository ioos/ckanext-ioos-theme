from rdflib import Namespace, Literal
from ckanext.dcat.profiles import RDFProfile
from ckanext.ioos_theme.plugin import get_pkg_item

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
SCHEMA = Namespace('http://schema.org/')

class IOOSDCATProfile(RDFProfile):
    '''
    IOOS extensions to DCAT profile to add standard names to DCAT output
    '''

    def graph_from_dataset(self, dataset_dict, dataset_ref):
        g = self.g

        try:
            std_names = get_pkg_item(dataset_dict, 'cf_standard_names')
        except:
            # TODO: add logging, etc
            pass

        if (std_names is not None and
           hasattr(std_names, '__iter__')):
            for standard_name in sorted(std_names):
                g.add((dataset_ref, SCHEMA.variableMeasured,
                        Literal(standard_name)))
