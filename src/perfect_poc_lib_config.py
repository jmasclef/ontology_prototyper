import os
import json
import hashlib

from yaml import safe_load, safe_dump,dump,load
from os.path import normpath as os_path_normpath
from . perfect_poc_modele_structure import *
from . perfect_poc_lib_table import TableSection

class perfect_poc_config(dict):
    configuration_dict = dict()

    def __init__(self,prototype,filename:str,running_mode:int,clean_unknwon_keys=False,load_data=True):
        self.prototype=prototype
        self.running_mode=running_mode
        self.raised_errors=False
        self.hash_trace=None
        self.filename=os_path_normpath(filename)
        self.modele = StructureParameters(MAJOR=0, MINOR=1, PATCH=0,running_mode=self.running_mode)
        self.configuration_dict=dict()
        self.__load_configuration_file()
        self.check_configuration_defaults()
        self.tables_sections = []
        self.predicates_dict=dict()
        #SECTIONS
        self.ontology_params=self.configuration_dict[ONTOLOGY_PARAMS_KEY]
        self.ontology_output_file_params=self.configuration_dict[ONTOLOGY_PARAMS_KEY][ONTOLOGY_OUTPUT_FILE_KEY]
        self.kb_params=self.configuration_dict[KB_PARAMS_KEY]
        self.kb_output_file_params=self.configuration_dict[KB_PARAMS_KEY][KB_OUTPUT_FILE_KEY]
        self.additional_classes_params=self.configuration_dict[ADDITIONAL_CLASSES_KEY]
        self.additional_dtp_params=self.configuration_dict[ADDITIONAL_DTP_KEY]
        self.additional_op_params=self.configuration_dict[ADDITIONAL_OP_KEY]
        self.tables_dict=self.configuration_dict[TABLES_LIST_KEY]
        self.source_files=self.configuration_dict[SOURCE_FILES_KEY]

        if self.ontology_params.setdefault(ONTOLOGY_LIBRARIES_KEY,True):
            # onto_namespaces=self.configurator.ontology_params[ONTOLOGY_NAMESPACES_KEY]
            # onto_imports=self.configurator.ontology_params[ONTOLOGY_IMPORTS_KEY]
            for prefix,uri in self.modele.LIBRARIES.items():
                if prefix not in self.ontology_params[ONTOLOGY_NAMESPACES_KEY]:
                    self.ontology_params[ONTOLOGY_NAMESPACES_KEY][prefix]=correct_uri(uri,ending_char='#')
                if correct_uri(uri,ending_char=None) not in self.ontology_params[ONTOLOGY_IMPORTS_KEY]:
                    self.ontology_params[ONTOLOGY_IMPORTS_KEY].append(correct_uri(uri,ending_char=None))

        #Enregistre la liste des prédicats créés automatiquement par analyse des JSON STRUCTs pour suppression des inutiles rencontrés
        self.automatic_json_dtp=set()
        self.automatic_json_op=set()

        normalised_source_filenames=[]
        for source_file in self.configuration_dict[SOURCE_FILES_KEY]:
            try:
                normalised_source_filenames.append(os_path_normpath(source_file))
            except:
                self.__raise_error("Impossible to normalize source filename {}".format(source_file))
                normalised_source_filenames.append(source_file)

        self.source_files=normalised_source_filenames
        self.configuration_dict[SOURCE_FILES_KEY]=normalised_source_filenames

        #ONTOLOGIE
        self.ontology_base_uri=self.ontology_params[ONTOLOGY_BASE_URI_KEY]
        self.ontology_base_namespace=self.ontology_params[ONTOLOGY_BASE_NAMESPACE_KEY]
        self.ontology_namespaces=self.ontology_params[ONTOLOGY_NAMESPACES_KEY]
        self.ontology_imports=self.ontology_params[ONTOLOGY_IMPORTS_KEY]
        #KB
        self.kb_base_uri=self.kb_params[KB_BASE_URI_KEY]
        self.kb_base_namespace=self.kb_params[KB_BASE_NAMESPACE_KEY]
        self.kb_namespaces=self.kb_params[KB_NAMESPACES_KEY]
        self.kb_imports=self.kb_params[KB_IMPORTS_KEY]
        self.correct_all_uris()

        # Contrôle les noms des classes parentes aux classes additionelles
        for additional_class in self.additional_classes_params.values():
            for parent_class in additional_class[ADDITIONAL_CLASS_SUBCLASS_OF_KEY]:
                self.check_declared_class_name(class_name=parent_class)

        unexpected_keys_list = self.configuration_dict.keys() - self.modele.MAIN_STRUCTURE

        if unexpected_keys_list.__len__()>0:
            logger.warning("Useless keys \"{}\" in config file root structure.".format(unexpected_keys_list))
            if clean_unknwon_keys:
                for key in unexpected_keys_list:
                    del self.configuration_dict[key]
                logger.info("Useless keys deleted")
            else:
                logger.info("Use \"--clean_keys\" option to delete useless keys.")

        for table_source_file,table_params in self.tables_dict.items():
                table_section= self.create_table_section(source_file=table_source_file,load_data=load_data,
                                        clean_unknwon_keys=clean_unknwon_keys, table_name=table_params[TABLE_NAME_KEY])
                if table_section is not None:
                    self.tables_sections.append(table_section)
                else:
                    self.raise_error("Could not load table from file \"{}\", fix or remove filename".format(table_source_file))
                    sys.exit()

        self.save_configuration_file()
        self.file_changed()

    def raise_error(self,error_msg: str):
        self.raised_errors=True
        self.prototype.raised_errors=True
        raise_error(error_msg=error_msg,running_mode=self.running_mode)

    def check_kb_nested_params(self):
        if self.ontology_params[ONTOLOGY_BASE_URI_KEY] not in self.kb_params[KB_IMPORTS_KEY]:
            self.kb_params[KB_IMPORTS_KEY].append(self.ontology_params[ONTOLOGY_BASE_URI_KEY])
        if self.ontology_params[ONTOLOGY_BASE_NAMESPACE_KEY] not in self.kb_params[KB_NAMESPACES_KEY].values():
            self.kb_params[KB_NAMESPACES_KEY][KB_ONTOLOGY_PREFIX] = self.ontology_params[ONTOLOGY_BASE_NAMESPACE_KEY]

    def check_configuration_defaults(self):
        #Met à jour les champs manquants avec les champs par défaut
        for key in self.modele.MAIN_STRUCTURE:
            self.configuration_dict[key]= init_struct(self.modele,self.configuration_dict,key=key)

        #Met à jour les liens noms de fichiers de sortie si besoin
        ontology_params_section = self.configuration_dict[ONTOLOGY_PARAMS_KEY]
        ontology_output_file_section = ontology_params_section[ONTOLOGY_OUTPUT_FILE_KEY]

        if ((ontology_output_file_section[ONTOLOGY_OUTPUT_FILE_NAME_KEY]==ONTOLOGY_OUTPUT_FILE_NAME_DEFAULT)
                and (ontology_params_section[ONTOLOGY_NAME_KEY]!=ONTOLOGY_NAME_DEFAULT)):
            ontology_filename= filter_root_filename_string(ontology_params_section[ONTOLOGY_NAME_KEY])
            ontology_output_file_section[ONTOLOGY_OUTPUT_FILE_NAME_KEY] = ontology_filename+DEFAULT_OUTPUT_FILE_EXT

        kb_params_section=self.configuration_dict[KB_PARAMS_KEY]
        kb_output_file_section=kb_params_section[KB_OUTPUT_FILE_KEY]

        if ((kb_output_file_section[KB_OUTPUT_FILE_NAME_KEY]==KB_OUTPUT_FILE_NAME_DEFAULT)
                and (kb_params_section[KB_NAME_KEY]!=KB_NAME_DEFAULT)):
            kb_filename= filter_root_filename_string(kb_params_section[KB_NAME_KEY])
            kb_output_file_section[KB_OUTPUT_FILE_NAME_KEY] = kb_filename+DEFAULT_OUTPUT_FILE_EXT

    def return_named_table_section(self,source_file:str=None,table_name:str=None):
        """
        Retourne une structure table soit par son nom soit par son fichier source
        """
        for table_section in self.tables_sections:
                if table_name is not None and table_section.table_name==table_name:
                    return table_section
                if source_file is not None and table_section.source_file==source_file:
                    return table_section
        else:
            return None

    def correct_all_uris(self):
        if self.ontology_base_namespace!=ONTOLOGY_BASE_NAMESPACE_DEFAULT:
            self.ontology_base_namespace=correct_uri(self.ontology_base_namespace, ending_char='#')
            if self.ontology_base_uri==ONTOLOGY_BASE_URI_DEFAULT:
                self.ontology_base_uri = correct_uri(self.ontology_base_namespace, ending_char=None)

        if self.ontology_base_uri!=ONTOLOGY_BASE_URI_DEFAULT:
            self.ontology_base_uri=correct_uri(self.ontology_base_uri, ending_char=None)
            if self.ontology_base_namespace==ONTOLOGY_BASE_NAMESPACE_DEFAULT:
                self.ontology_base_namespace = correct_uri(self.ontology_base_uri, ending_char='#')

        if self.kb_base_uri!=KB_BASE_URI_DEFAULT:
            self.kb_base_uri=correct_uri(self.kb_base_uri, ending_char=None)
            if self.kb_base_namespace == KB_BASE_NAMESPACE_DEFAULT:
                self.kb_base_namespace = correct_uri(self.kb_base_uri, ending_char='/')
        if self.kb_base_namespace!=KB_BASE_NAMESPACE_DEFAULT:
            self.kb_base_namespace=correct_uri(self.kb_base_namespace, ending_char='/')
            if self.kb_base_uri == KB_BASE_URI_DEFAULT:
                self.kb_base_uri = correct_uri(self.kb_base_namespace, ending_char=None)

        self.check_namespaces(section_name="ontology",namespaces_dict=self.ontology_namespaces)
        self.ontology_imports=self.correct_imports(imports_list=self.ontology_imports)
        self.check_namespaces(section_name="kb",namespaces_dict=self.kb_namespaces)
        self.kb_imports=self.correct_imports(imports_list=self.kb_imports)

        self.ontology_params[ONTOLOGY_BASE_URI_KEY]=self.ontology_base_uri
        self.ontology_params[ONTOLOGY_BASE_NAMESPACE_KEY]=self.ontology_base_namespace
        self.ontology_params[ONTOLOGY_NAMESPACES_KEY]=self.ontology_namespaces
        self.ontology_params[ONTOLOGY_IMPORTS_KEY]=self.ontology_imports
        self.kb_params[KB_BASE_URI_KEY]=self.kb_base_uri
        self.kb_params[KB_BASE_NAMESPACE_KEY]=self.kb_base_namespace
        self.kb_params[KB_NAMESPACES_KEY]=self.kb_namespaces
        self.kb_params[KB_IMPORTS_KEY]=self.kb_imports

    def check_declared_class_name(self, class_name: str(),already_warned=list()):
        if class_name.count(':') == 1:
            prefix, name = class_name.split(':')
            prefix_list = self.ontology_params[ONTOLOGY_NAMESPACES_KEY].keys()
            if prefix in prefix_list:
                if name not in already_warned:
                    already_warned.append(name)
                    logger.warning("Can not check existence of class \"{}\" prefixed class \"{}:{}\""
                                   .format(name, prefix,name))
                return True
            else:
                if prefix not in already_warned:
                    already_warned.append(prefix)
                    self.raise_error("Undeclared prefix \"{}\" in ontology namespaces section.".format(prefix))
                return False
        else:
            # Vérifie si le nom de la classe existe parmi les classes additionelles ou les classes de tables
            return self.is_additional_class_name(class_name) or self.is_table_target_class_name(class_name=class_name)

    def scan_json_struct(self,json_dict:dict,parent_class:str=None):
        for key,value in json_dict.items():
            if value is None:
                continue
            value_type=type(value)
            if value_type==float:
                if self.check_declared_class_name(class_name=key):
                    logger.debug("In dict {}".format(json_dict))
                    self.raise_error("Key {} with float value of {} can't be class id".format(key,value))
                else:
                    if not self.is_additional_dtp_predicate(key):
                        logger.debug("Create datatype property {}".format(PREDICATE_PREFIX + key))
                    self.set_additional_dtp_params(predicate_name=key, domain=parent_class,xsd_type=XSD_CONF_FLOAT_TYPE)
            elif value_type==bool:
                if self.check_declared_class_name(class_name=key):
                    logger.debug("In dict {}".format(json_dict))
                    self.raise_error("Key {} with boolean value of {} can't be class id".format(key,value))
                else:
                    if not self.is_additional_dtp_predicate(key):
                        logger.debug("Create datatype property {}".format(PREDICATE_PREFIX + key))
                    self.set_additional_dtp_params(predicate_name=key, domain=parent_class,xsd_type=XSD_CONF_BOOLEAN_TYPE)
            elif value_type==int or value_type==str:
                if value in SKIPPED_VALUES:
                    continue
                if self.check_declared_class_name(class_name=key):
                    if not self.is_additional_class_name(key):
                        logger.debug("Create class {}".format(key))
                        logger.debug("Create object property {}".format(PREDICATE_PREFIX + key))
                    self.set_additional_class_params(class_name=key)
                    self.set_additional_op_params(predicate_name=key, domain=parent_class, range=key)
                else:
                    #Par défaut si la clé n'est pas une classe alors ce sera une datatype_property
                    if not self.is_additional_dtp_predicate(key):
                        logger.debug("Create datatype property {}".format(key))
                    xsd_type= xsd_type_factory(value,test_date=True,test_float=True,test_int=True)
                    if xsd_type is not None:
                        self.set_additional_dtp_params(predicate_name=key, domain=parent_class,xsd_type=xsd_type)
            elif value_type==dict:
                if len(value)==0:
                    continue
                #une clé de dictionnaire est nécessairement une classe
                if not self.is_additional_class_name(key):
                    logger.debug("Create class {}".format(class_name_factory(key)))
                    logger.debug("Create object property {}".format(PREDICATE_PREFIX + key))
                self.set_additional_class_params(class_name=key)
                self.set_additional_op_params(predicate_name=key, domain=parent_class, range=key)
                self.scan_json_struct(value,parent_class=key)
            elif value_type==list:
                if len(value)==0:
                    continue
                if all([isinstance(item, dict) for item in value]):
                    #c'est une liste de dictionnaires alors la clé parente est une classe, les dictionnaires
                    #donneront des classes
                    if not self.is_additional_class_name(key):
                        logger.debug("Create class {}".format(class_name_factory(key)))
                        logger.debug("Create object property {}".format(PREDICATE_PREFIX + key))
                    self.set_additional_class_params(class_name=key)
                    self.set_additional_op_params(predicate_name=key,domain=parent_class,range=key,is_functional=False)
                    for item in value:
                        #Pour chaque dictionnaire de la liste, applique le scan
                        self.scan_json_struct(json_dict=item,parent_class=key)
                else:
                    #sinon par défaut la clé parente est une datatype property
                    if self.is_additional_class_name(key):
                        if not self.is_additional_class_name(key):
                            logger.debug("Create class {}".format(class_name_factory(key)))
                            logger.debug("Create object property {}".format(PREDICATE_PREFIX + key))
                        # self.set_additional_class_params(class_name=key)
                        self.set_additional_op_params(predicate_name=key, domain=parent_class, range=key,is_functional=False)
                    else:
                        if not self.is_additional_dtp_predicate(key):
                            logger.debug("Create datatype property {}".format(PREDICATE_PREFIX + key))
                        self.set_additional_dtp_params(predicate_name=key,domain=parent_class,is_functional=False)
            else:
                if value is not None and value!='':
                    logger.debug("Unknwon type {} for value {}".format(value_type,value))

    def is_table_target_class_name(self, class_name:str):
        # Vérifie si le nom de la table existe dans la configuration, pas dans les objets (synchro)
        for table_name,table_dict in self.tables_dict.items():
            try:
                if table_dict[TABLE_TYPE_PARAMS_KEY][TABLE_TARGET_CLASS_NAME_KEY] == class_name:
                    return True
            except:
                self.raise_error("Missing table target class name {} for table {} params."
                                 .format(TABLE_TARGET_CLASS_NAME_KEY,table_name))
                continue
        else:
            return False

    def is_additional_class_name(self, class_name: str()):
        return (class_name in self.additional_classes_params.keys()) \
               or (class_name_factory(class_name) in self.additional_classes_params.keys())

    def is_additional_dtp_predicate(self, dtp_predicate: str(), prefix=PREDICATE_PREFIX):
        return ((prefix+dtp_predicate) in self.additional_dtp_params.keys()) \
               or ((dtp_predicate) in self.additional_dtp_params.keys())

    def is_additional_op_predicate(self, op_predicate: str(), prefix=PREDICATE_PREFIX):
        return (prefix+op_predicate in self.additional_op_params.keys()) \
               or (op_predicate in self.additional_op_params.keys())

    def return_table_section_from_class_name(self,class_name:str):
        """
        Recherche une table à l'aide de son nom et retourne la structure ou None
        Utilise les données JSON, les objets ne sont pas forcément tous chargés au moment de l'appel
        """
        for table_params in self.configuration_dict[TABLES_LIST_KEY].values():
            if table_params[TABLE_TYPE_KEY] == TT_CLASS:
                if table_params[TABLE_TYPE_PARAMS_KEY][TABLE_TARGET_CLASS_NAME_KEY]==class_name:
                    return table_params
        else:
            return None

    def check_namespaces(self,section_name:str(),namespaces_dict:dict()):
        chars_to_filter = {'#', '/'}
        for prefix,uri in namespaces_dict.items():
            if ':' in prefix:
                self.raise_error("Error in {} namespaces parameters section: prefix \"{}\" can't contain \":\" character"
                                 .format(section_name,prefix))
            if uri[-1] not in chars_to_filter:
                self.raise_error("Error in {} namespaces parameters section: uri for prefix \"{}\" must finish with character \"#\" or \"/\""
                    .format(section_name, prefix))

    def correct_imports(self,imports_list:list()):
        new_imports_list=list()
        for uri in imports_list:
            new_imports_list.append(correct_uri(uri=uri,ending_char=None))
        return new_imports_list

    def set_additional_class_params(self,class_name:str):
        class_name=class_name_factory(class_name)
        # class_name=first_char_upper(class_name)
        if class_name in self.additional_classes_params.keys():
            local_dict=copy_deepcopy(self.additional_classes_params[class_name])
        else:
            local_dict=dict()
        local_dict.setdefault(ADDITIONAL_CLASS_LABELS_KEY, default_labels(class_name))
        local_dict.setdefault(ADDITIONAL_CLASS_SUBCLASS_OF_KEY,[])
        if (len(local_dict[ADDITIONAL_CLASS_LABELS_KEY]) == 0) or (local_dict[ADDITIONAL_CLASS_LABELS_KEY] == {}):
            local_dict[ADDITIONAL_CLASS_LABELS_KEY] = default_labels(class_name)

        self.additional_classes_params[class_name]=copy_deepcopy(local_dict)
        local_dict.clear()

    def set_additional_dtp_params(self,predicate_name:str,domain:str,xsd_type:str=None,is_functional=True):
        #ICI
        domain=class_name_factory(domain)
        predicate_name= predicate_name_factory(predicate_name)
        if predicate_name in self.additional_dtp_params.keys():
            local_dict=copy_deepcopy(self.additional_dtp_params[predicate_name])
        else:
            local_dict=dict()

        for key in self.modele.ADDITIONAL_DTP_SUB_STRUCTURE:
            local_dict[key]=init_struct(self.modele,local_dict,key)
        if domain is not None and domain not in local_dict[ADDITIONAL_DTP_DOMAINS_KEY]:
            local_dict[ADDITIONAL_DTP_DOMAINS_KEY].append(domain)
        if xsd_type is not None:
            if isinstance(local_dict[ADDITIONAL_DTP_XSD_TYPE_KEY],str):
                if local_dict[ADDITIONAL_DTP_XSD_TYPE_KEY]!=xsd_type:
                    logger.warning("CHANGE OLD XSD TYPE {} FOR {} IN ADDITIONAL DATATYPE PROPERTY {}"
                                   .format(local_dict[ADDITIONAL_DTP_XSD_TYPE_KEY],xsd_type,predicate_name))
                local_dict[ADDITIONAL_DTP_XSD_TYPE_KEY]=[local_dict[ADDITIONAL_DTP_XSD_TYPE_KEY]]
            local_dict[ADDITIONAL_DTP_XSD_TYPE_KEY].append(xsd_type)
            # local_dict[ADDITIONAL_DTP_XSD_TYPE_KEY]=xsd_type
        if len(local_dict[ADDITIONAL_DTP_LABELS_KEY]) == 0:
            local_dict[ADDITIONAL_DTP_LABELS_KEY] = default_labels(predicate_name)
        if not is_functional:
            local_dict[ADDITIONAL_DTP_IS_FUNCTIONAL] = False

        self.additional_dtp_params[predicate_name]=copy_deepcopy(local_dict)
        local_dict.clear()
        self.automatic_json_dtp.add(predicate_name)

    def set_additional_op_params(self,predicate_name:str,domain:str,range:str,is_functional=True):
        domain=class_name_factory(domain)
        range=class_name_factory(range)
        # domain=first_char_upper(domain)
        # range=first_char_upper(range)
        predicate_name= PREDICATE_PREFIX + predicate_name
        if predicate_name in self.additional_op_params.keys():
            local_dict=copy_deepcopy(self.additional_op_params[predicate_name])
        else:
            local_dict=dict()
        for key in self.modele.ADDITIONAL_OP_SUB_STRUCTURE:
            local_dict[key]=init_struct(self.modele,local_dict,key)
        if domain is not None and domain not in local_dict[ADDITIONAL_OP_DOMAINS_KEY]:
            local_dict[ADDITIONAL_OP_DOMAINS_KEY].append(domain)
        if range is not None and range not in local_dict[ADDITIONAL_OP_RANGES_KEY]:
            local_dict[ADDITIONAL_OP_RANGES_KEY].append(range)
        if len(local_dict[ADDITIONAL_OP_LABELS_KEY]) ==0:
            local_dict[ADDITIONAL_OP_LABELS_KEY]=default_labels(predicate_name)
        if not is_functional:
            local_dict[ADDITIONAL_OP_IS_FUNCTIONAL_KEY] = False

        local_dict.setdefault(ADDITIONAL_OP_BUILD_INVERSEOF_KEY,False)
        if local_dict[ADDITIONAL_OP_BUILD_INVERSEOF_KEY]:
            local_dict.setdefault(ADDITIONAL_OP_INVERSEOF_LABELS_KEY, dict())
            if len(local_dict[ADDITIONAL_OP_INVERSEOF_LABELS_KEY]) == 0:
                inverseOf_predicate= INVERT_OF_PREDICATE_PREFIX+predicate_name
                local_dict[ADDITIONAL_OP_INVERSEOF_LABELS_KEY] = default_labels(inverseOf_predicate)

        self.additional_op_params[predicate_name]=copy_deepcopy(local_dict)
        local_dict.clear()

        self.automatic_json_op.add(predicate_name)

    def create_table_section(self,source_file:str,table_name:str,load_data=True,clean_unknwon_keys=False):
        return TableSection(self, source_file, table_name, load_data=load_data, clean_unknwon_keys=clean_unknwon_keys)


    def __load_configuration_file(self):
        """
        Charge le fichier de configuration, si non trouvé essaie de le créer
        """
        filename=self.filename
        _, ext = os.path.splitext(filename)
        ext = ext.upper()
        if ext in JSON_EXTENSIONS_LIST:
            if os.path.isfile(filename):
                with open(filename, "r", encoding=DEFAULT_ENCODING) as jsonfile:
                    try:
                        self.configuration_dict = json.load(jsonfile)
                    except Exception as e:
                        logger.error("Check JSON configuration file structure, seems to be uncorrect JSON structure.")
                        # Cette ereur doit provoquer provoquer un stop pour éviter une destruction du fichier de configuration
                        raise_error("Impossible to load json file: {}".format(e.__str__()),
                                    running_mode=RUNNING_MODE_NORMAL)
                self.file_changed()
                return True
            else:
                # logger.warning("Existing configuration file \"{}\" not found, creating a template file.".format(filename))
                try:
                    with open(filename, "w", encoding=DEFAULT_ENCODING) as jsonfile:
                        json.dump(obj=self.configuration_dict, fp=jsonfile, indent='\t', sort_keys=True, ensure_ascii=False)
                    logger.info("Create empty configuration file")
                except:
                    self.raise_error("Impossible to create {}".format(filename))
                    exit()
                self.configuration_dict = dict()
        elif ext in YAML_EXTENSIONS_LIST:
            return False
        else:
            self.raise_error("\"{}\" unknown configuration file extension, use .json filename !".format(ext))
            exit()

    def file_changed(self):
        """
        Calcule la valeur de hash du fichier de configuration et retourne Vrai si elle a changé
        Utilisé pour le mode loop de modifications continues
        """
        with open(self.filename, 'rb') as conf_file:
            text=conf_file.read()
        new_hash_trace=hashlib.sha256(text).hexdigest()
        if self.hash_trace is None:
            #A l'init retourne Faux
            self.hash_trace=new_hash_trace
            return False
        elif new_hash_trace!= self.hash_trace:
            self.hash_trace=new_hash_trace
            return True
        else:
            return False

    def save_configuration_file(self,other_filename=None):
        """
        Sauve le fichier de configuration et actualise sa valeur de hash
        """
        filename=other_filename if other_filename else self.filename
        _, ext = os.path.splitext(filename)
        ext = ext.upper()
        if ext in JSON_EXTENSIONS_LIST:
            with open(filename, "w", encoding=DEFAULT_ENCODING) as jsonfile:
                json.dump(obj=self.configuration_dict, fp=jsonfile, indent='\t', sort_keys=True, ensure_ascii=False)
        elif ext in YAML_EXTENSIONS_LIST:
            with open(filename, "w", encoding=DEFAULT_ENCODING) as yamlfile:
                dump(self.configuration_dict, yamlfile, encoding=DEFAULT_ENCODING, allow_unicode=True)
        else:
            self.raise_error("\"{}\" unknown configuration file extension !")
            exit()
        self.file_changed()
