import rdflib

from . perfect_poc_utils import *

def return_uriref(string_name,namespaces,base_namespace,running_mode:int):
    if (':' not in string_name):
        return rdflib.URIRef(base_namespace[string_name])
    else:
        try:
            prefix, ext = string_name.split(":")
        except:
            raise_error("Bad syntax for short uri name {}".format(string_name),running_mode=running_mode)
            return None
        if (prefix not in namespaces) and (prefix.__len__() > 0):
            raise_error('Undeclared namespace for prefix \"{}\": declare prefix and namespace in the ontology namespaces section.'.format(prefix),running_mode=running_mode)
            return None
        if prefix.__len__()==0:
            namespace= base_namespace
        else:
            namespace = rdflib.Namespace(namespaces[prefix])
        return rdflib.URIRef(namespace[ext])

def __declare_comments(uri, comments_dict, graph:rdflib.Graph):
    for lang, comment in comments_dict.items():
        graph.add((rdflib.URIRef(uri), rdflib.RDFS.comment, rdflib.Literal(comment, lang=lang)))


class VisuNode():
    def __init__(self,predicate:str,group:str,weight:int=None):
    # def __init__(self,id,name,label,group,weight):
        self.id=predicate
        self.name=predicate
        self.label=predicate
        self.group=group
        if weight is None:
            weight=''
        self.runtime=weight

    def json_dumps(self):
        try:
            return json.dumps(self.__dict__, ensure_ascii=True, encodings=DEFAULT_ENCODING)
        except Exception as error:
            logger.error("Unable to dump json link line for visualisation with predicate {}".format(self.type))
            logger.error(error)
            return '{}'

class VisuLink():
    def __init__(self,predicate:str,source:str=None, target:str=None):
        self.type=predicate+' >>'
        self.source=source
        self.target=target

    def json_dumps(self):
        try:
            return json.dumps(self.__dict__, ensure_ascii=True, encodings=DEFAULT_ENCODING)
        except Exception as error:
            logger.error("Unable to dump json link line for visualisation with predicate {}".format(self.type))
            logger.error(error)
            return '{}'

class perfect_graph(rdflib.Graph):
    def __init__(self,base_namespace:str,uri:str,running_mode:int,core_prefixes:set):
        self.raised_errors=False
        self.graph=rdflib.Graph()
        self.base_namespace=rdflib.Namespace(base_namespace)
        self.uri=rdflib.Namespace(uri)
        # triple = (rdflib.URIRef(self.uri), rdflib.RDF.type, rdflib.OWL.Ontology)
        self.graph.add((rdflib.URIRef(self.uri), rdflib.RDF.type, rdflib.OWL.Ontology))
        self.graph.bind(prefix="", namespace=self.base_namespace)
        self.namespaces=None
        self.running_mode=running_mode
        #Utilisé seulement pour la production de la kb
        self.related_ontology_base_namespace=None
        self.core_prefixes=core_prefixes
        self.visu_nodes_dict = dict()
        self.visu_links_dict = dict()
        return

    def visu_nodes_list(self):
        return [node.__dict__ for node in self.visu_nodes_dict.values()]

    def visu_links_list(self):
        return [link.__dict__ for link in self.visu_links_dict.values()
                if (link.target in self.visu_nodes_dict) and (link.source in self.visu_nodes_dict)]

    def visu_add_node(self,class_name):
        # SECTION VISUALISATION
        if class_name is not None:
            logger.debug("Visu Add Class node {}".format(class_name))
            node=VisuNode(predicate=class_name,group=VISU_OBJECTS_GROUP_NAME)
            # self.visu_object_nodes_dict[predicate]= node
            self.visu_nodes_dict[class_name]= node

    def visu_add_link(self,predicate_name,source_name=None,target_name=None):
        if predicate_name is None or (source_name is None and target_name is None):
            self.__raise_error("Request for empty link to create")
            return
        # Les domains et les ranges ne jouent que sur les links
        if predicate_name in self.visu_links_dict:
            link= self.visu_links_dict[predicate_name]
        else:
            link = VisuLink(source=None, target=None, predicate=predicate_name)

        if target_name is not None:
            link.target = target_name
        if source_name is not None:
            link.source = source_name

        self.visu_links_dict[predicate_name] = link

    def __raise_error(self,error_msg: str):
        self.raised_errors=True
        raise_error(error_msg=error_msg,running_mode=self.running_mode)

    def add_to_graph(self,*args, **kwargs):
        self.graph.add(*args, **kwargs)

    def return_uriref(self,string_name):
        value = return_uriref(string_name=string_name,namespaces=self.namespaces,base_namespace=self.base_namespace,
                              running_mode=self.running_mode)
        if value is None:
            self.raised_errors=True
        return value

    def set_ontology_global_params(self,global_params_dict:dict):

        # Charge les prefixs dans le graph, contruit l'espace des noms
        self.set_prefixes(prefixes_dict=global_params_dict[ONTOLOGY_NAMESPACES_KEY])

        # Charge les classes d'equivalence dans le graph
        self.set_equivalences(equivalences_dict=global_params_dict[ONTOLOGY_EQUIVALENT_CLASSES_KEY])

        # Charge les imports dans le graph
        self.set_imports(imports_list=global_params_dict[ONTOLOGY_IMPORTS_KEY])

        # Charge les labels dans le graph
        self.set_labels(rdflib.URIRef(self.uri),labels_dict=global_params_dict[ONTOLOGY_LABELS_KEY])

        # Charge les commentaires dans le graph
        self.set_comments(self.uri,comments_dict=global_params_dict[ONTOLOGY_COMMENTS_KEY])

    def set_kb_global_params(self,global_params_dict:dict):
        # Charge les prefixs dans le graph, contruit l'espace des noms
        self.set_prefixes(prefixes_dict=global_params_dict[KB_NAMESPACES_KEY])

        # Charge les imports dans le graph
        self.set_imports(imports_list=global_params_dict[KB_IMPORTS_KEY])

        # Charge les labels dans le graph
        self.set_labels(rdflib.URIRef(self.uri),labels_dict=global_params_dict[KB_LABELS_KEY])

        # Charge les commentaires dans le graph
        self.set_comments(self.uri,comments_dict=global_params_dict[KB_COMMENTS_KEY])


    def set_prefixes(self,prefixes_dict:dict):
        self.namespaces = dict()
        for prefix, namespace in prefixes_dict.items():
            if namespace == "":
                continue
            self.namespaces[prefix] = rdflib.Namespace(namespace)
            self.graph.bind(prefix=prefix, namespace=self.namespaces[prefix])
        return self.namespaces

    def set_equivalences(self,equivalences_dict:dict):
        for source, target in equivalences_dict.items():
            subject = self.return_uriref(source)
            object = self.return_uriref(target)
            if subject is None or object is None:
                return
            triple = (subject, rdflib.OWL.equivalentClass, object)
            self.graph.add(triple)

    def set_parents_class(self, subject, parents_list:list):
        refer_to_core_classes=False
        core_prefixes_set=set(self.core_prefixes)
        for class_name in parents_list:
            if class_name.count(':') == 1:
                prefix, _ = class_name.split(':')
                if prefix in core_prefixes_set:
                    refer_to_core_classes = True
            object = self.return_uriref(class_name)
            if object is None:
                return

            triple = (subject, rdflib.RDFS.subClassOf, object)
            self.graph.add(triple)
        if not refer_to_core_classes:

            logger.warning("Class {} lacks of references to {} core ontologies.".format(subject,core_prefixes_set))

    def set_parents_property(self, subject, parents_list:list):
        for property_name in parents_list:
            object = self.return_uriref(property_name)
            if object is None:
                return
            triple = (subject, rdflib.RDFS.subPropertyOf, object)
            self.graph.add(triple)

    def set_new_class(self, subject):
        triple = (subject, rdflib.RDF.type, rdflib.OWL.Class)
        self.graph.add(triple)
        logger.debug("RDFLib graph Add Class {}".format(subject))

    def set_type(self, subject, type):
        triple = (subject, rdflib.RDF.type, type)
        self.graph.add(triple)

    def set_labels(self,subject,labels_dict:dict):
        for lang, label in labels_dict.items():
            self.graph.add((subject, rdflib.RDFS.label, rdflib.Literal(label, lang=lang)))

    def set_comments(self,uri, comments_dict):
        for lang, comment in comments_dict.items():
            self.graph.add((rdflib.URIRef(uri), rdflib.RDFS.comment, rdflib.Literal(comment, lang=lang)))

    def set_imports(self,imports_list:list):
        subject=rdflib.URIRef(self.uri)
        for import_value in imports_list:
            self.graph.add((subject, rdflib.OWL.imports, rdflib.URIRef(import_value)))

    def set_domain(self,subject,domain):
        triple = (subject, rdflib.RDFS.domain, domain)
        self.graph.add(triple)
        logger.debug("RDFLib Add Domain {} to class {}".format(domain,subject))

    def set_range(self,subject, range):
        triple = (subject, rdflib.RDFS.range, range)
        self.graph.add(triple)
        logger.debug("RDFLib Add Range {} to class {}".format(range,subject))

    def set_new_datatype_property(self,subject):
        triple = (subject, rdflib.RDF.type, rdflib.OWL.DatatypeProperty)
        self.graph.add(triple)

    def set_new_object_property(self,subject):
        triple = (subject, rdflib.RDF.type, rdflib.OWL.ObjectProperty)
        self.graph.add(triple)

    def set_new_inversion_of_object_property(self,subject,object):
        self.set_new_object_property(subject)
        triple = (subject, rdflib.OWL.inverseOf,object)
        self.graph.add(triple)
        #Les domains et les ranges ne jouent que sur les links
        predicate=extract_predicate_from_uri(object)
        inv_predicate=extract_predicate_from_uri(subject)
        if predicate in self.visu_links_dict.keys():
            link = self.visu_links_dict[predicate]
            inv_link = VisuLink(source=link.target, target=link.source, predicate=inv_predicate)
            self.visu_links_dict[inv_predicate]=inv_link

    def set_new_functional_property(self,subject):
        triple = (subject, rdflib.RDF.type, rdflib.OWL.FunctionalProperty)
        self.graph.add(triple)

    def set_additional_classes(self,additional_classes_dict:dict):
        for additional_class_name, additional_class in additional_classes_dict.items():
            self.visu_add_node(additional_class_name)
            if (':' in additional_class_name and (additional_class_name[0] != ':')):
                continue
            subject = self.base_namespace[additional_class_name]
            self.set_new_class(subject)
            # Class Hierarchy
            try:
                self.set_parents_class(subject, parents_list=additional_class[ADDITIONAL_CLASS_SUBCLASS_OF_KEY])
            except:
                self.__raise_error("Missing key \"{}\" in additional class struture for class {}"
                                   .format(ADDITIONAL_CLASS_SUBCLASS_OF_KEY,additional_class_name))

            # Class Labels
            self.set_labels(subject,additional_class[ADDITIONAL_CLASS_LABELS_KEY])

            #Extra URI field
            if ADDITIONAL_CLASS_EXTRA_URI_MASK_KEY in additional_class:
                extra_uri_template=additional_class[ADDITIONAL_CLASS_EXTRA_URI_MASK_KEY]
                if type(extra_uri_template) is not str:
                    self.__raise_error("Any URI Mask must be a string for additionnal class {}"
                                       .format(additional_class_name))
                    continue
                if extra_uri_template.count(ADDITIONAL_CLASS_EXTRA_URI_MASK)>0:
                    predicate=self.base_namespace[predicate_name_factory(ADDITIONAL_CLASS_EXTRA_URI_PREDICATE)]
                    self.set_new_datatype_property(predicate)
                    self.set_domain(subject=predicate,domain=subject)
                    self.set_range(subject=predicate,range=XSD_RDFLIB_ANYURI)
                    self.set_labels(subject=predicate,labels_dict=ADDITIONAL_CLASS_EXTRA_URI_LABELS)
                else:
                    self.__raise_error("Any URI Mask needs url with \"{}\" syntax for additionnal class {}"
                                       .format(ADDITIONAL_CLASS_EXTRA_URI_MASK,additional_class_name))
                    continue


    def set_additional_datatype_properties(self,additional_dtp_dict:dict):
        for additional_dtp_name, additional_dtp in additional_dtp_dict.items():
            subject = self.base_namespace[additional_dtp_name]
            self.set_new_datatype_property(subject)
            # DataType Property Hierarchy
            try:
                self.set_parents_property(subject, parents_list=additional_dtp[ADDITIONAL_DTP_SUBPROPERTY_OF_KEY])
            except:
                self.__raise_error("Missing key \"{}\" in additional datatype property struture for \"{}\""
                                   .format(ADDITIONAL_DTP_SUBPROPERTY_OF_KEY,additional_dtp_name))

            # DataType Property Domains
            if ADDITIONAL_DTP_DOMAINS_KEY in additional_dtp:
                for class_name in additional_dtp[ADDITIONAL_DTP_DOMAINS_KEY]:
                    domain = self.return_uriref(class_name)
                    if domain is not None:
                        self.set_domain(subject,domain)
            else:
                self.__raise_error("Missing key \"{}\" in additional datatype property struture for \"{}\""
                                   .format(ADDITIONAL_DTP_DOMAINS_KEY,additional_dtp_name))

            # DataType Property Ranges
            try:
                xsd_range = XSD_CONF_RDFLIB_CONVERTER[additional_dtp[ADDITIONAL_DTP_XSD_TYPE_KEY]]
            except:
                self.__raise_error("Unknown XSD type \"{}\" in additional datatype property struture for \"{}\""
                                   .format(additional_dtp[ADDITIONAL_DTP_XSD_TYPE_KEY], additional_dtp_name))

            try:
                self.set_range(subject,xsd_range)
            except:
                self.__raise_error("Missing key \"{}\" in additional datatype property struture for \"{}\""
                                   .format(ADDITIONAL_DTP_XSD_TYPE_KEY,additional_dtp_name))

            # Labels
            self.set_labels(subject,additional_dtp[ADDITIONAL_DTP_LABELS_KEY])

    def set_additional_object_properties(self,additional_op_dict:dict):
        for additional_op_name, additional_op in additional_op_dict.items():
            subject = self.base_namespace[additional_op_name]
            self.set_new_object_property(subject)

            # Object Property Hierarchy
            try:
                self.set_parents_property(subject, parents_list=additional_op[ADDITIONAL_OP_SUBPROPERTY_OF_KEY])
            except:
                self.__raise_error("Missing key \"{}\" in additional object property struture for \"{}\""
                                   .format(ADDITIONAL_DTP_SUBPROPERTY_OF_KEY,additional_op))

            # Object Property Domains
            if ADDITIONAL_OP_DOMAINS_KEY in additional_op.keys():
                for class_name in additional_op[ADDITIONAL_OP_DOMAINS_KEY]:
                    domain = self.return_uriref(class_name)
                    if class_name == "pmmodel:PMObject":
                        print(domain)
                    # domain = rdflib.URIRef(self.base_namespace[class_name])
                    if domain is not None:
                        self.set_domain(subject,domain)
                        self.visu_add_link(predicate_name=additional_op_name,source_name=class_name)
            else:
                self.__raise_error("Missing key \"{}\" in additional object property struture for \"{}\""
                                   .format(ADDITIONAL_DTP_DOMAINS_KEY,additional_op))

            # Object Property Ranges
            if ADDITIONAL_OP_RANGES_KEY in additional_op.keys():
                for class_name in additional_op[ADDITIONAL_OP_RANGES_KEY]:
                    range = rdflib.URIRef(self.base_namespace[class_name])
                    self.set_range(subject,range)
                    self.visu_add_link(predicate_name=additional_op_name, target_name=class_name)
            else:
                self.__raise_error("Missing key \"{}\" in additional object property struture for \"{}\""
                                   .format(ADDITIONAL_OP_RANGES_KEY,additional_op))

            #InverseOf
            if additional_op[ADDITIONAL_OP_BUILD_INVERSEOF_KEY]:
                inverseOf_predicate = INVERT_OF_PREDICATE_PREFIX + additional_op_name
                inverseOf_subject = self.base_namespace[inverseOf_predicate]
                self.set_new_inversion_of_object_property(inverseOf_subject, subject)


            # Labels
            self.set_labels(subject,additional_op[ADDITIONAL_OP_LABELS_KEY])
            if additional_op[ADDITIONAL_OP_BUILD_INVERSEOF_KEY]:
                self.set_labels(inverseOf_subject, additional_op[ADDITIONAL_OP_INVERSEOF_LABELS_KEY])

    def create_table_graph(self,table_type_params_dict:dict):
        subject = self.base_namespace[table_type_params_dict[TABLE_TARGET_CLASS_NAME_KEY]]
        # Class
        self.set_new_class(subject)
        # Hierarchy
        self.set_parents_class(subject, parents_list=table_type_params_dict[TABLE_CLASS_SUBCLASS_OF_KEY])
        # Labels
        self.set_labels(subject,labels_dict=table_type_params_dict[TABLE_TARGET_CLASS_LABELS_KEY])
