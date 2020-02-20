from rdflib.namespace import Namespace, RDF
from ckanext.dcat.profiles import RDFProfile
from ckanext.ioos_theme.plugin import get_pkg_item
from rdflib import URIRef, BNode, Literal
from ckanext.dcat.profiles import RDFProfile
from geomet import wkt, InvalidGeoJSONException
from shapely.geometry import shape
import json
import geojson

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace('http://schema.org/')
TIME = Namespace('http://www.w3.org/2006/time')
LOCN = Namespace('http://www.w3.org/ns/locn#')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SPDX = Namespace('http://spdx.org/rdf/terms#')

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
SCHEMA = Namespace('http://schema.org/')

GEOJSON_IMT = 'https://www.iana.org/assignments/media-types/application/vnd.geo+json'

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

        spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
        spatial_text = self._get_dataset_value(dataset_dict, 'spatial_text')
        spatial_geom = self._get_dataset_value(dataset_dict, 'spatial')

        if spatial_uri or spatial_text or spatial_geom:
            if spatial_uri:
                spatial_ref = CleanedURIRef(spatial_uri)
            else:
                spatial_ref = BNode()

        g.add((spatial_ref, RDF.type, SCHEMA.Place))

        if spatial_text:
            g.add((spatial_ref, SKOS.prefLabel, Literal(spatial_text)))

        if spatial_geom:
            # GeoJSON
            g.add((spatial_ref,
                    LOCN.geometry,
                    Literal(spatial_geom, datatype=GEOJSON_IMT)))
            # WKT, because GeoDCAT-AP says so
            try:
                g.add((spatial_ref,
                       LOCN.geometry,
                       Literal(wkt.dumps(json.loads(spatial_geom),
                                         decimals=4),
                               datatype=GSP.wktLiteral)))
            except (TypeError, ValueError, InvalidGeoJSONException):
                pass
            try:
                gj = geojson.loads(spatial_geom)
                geo_shape = BNode()
                if gj['type'] == 'FeatureCollection':
                    features = gj['features']
                    all_features = zip(shape(f['geometry']).bounds for f
                                       in features)
                    bbox = [min(all_features[1]), min(all_features[0]),
                            max(all_features[3]), max(all_features[2])]

                    g.add((place, RDF.type))


                    g.add((spatial_ref, SCHEMA.geom, place))
                else:
                    bounds = shape(gj).bounds
                    bbox = [str(bound) for bound in bounds[1::-1] +
                                                    bounds[:1:-1]]
            except:
                pass
            else:
                bbox_str = ' '.join(bbox)
                geo_shape = BNode()
                g.add((geo_shape, RDF.type, SCHEMA.GeoShape))
                g.add((spatial_ref, SCHEMA.geo, geo_shape))
                # Add bounding box element
                g.add((geo_shape, SCHEMA.box, Literal(bbox_str)))
