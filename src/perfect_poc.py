import json
import time
from os.path import normpath as os_path_normpath

from . perfect_poc_lib_config import *
from . perfect_poc_lib_graph import *


class perfect_prototype():
    def __init__(self,filename:str,running_mode:int,clean_unknwon_keys=False,load_data=True):
        self.filename = os_path_normpath(filename)
        logger.debug("Normalized file name: {}".format(self.filename))
        self.running_mode=running_mode
        self.clean_unknwon_keys=clean_unknwon_keys
        self.load_data=load_data
        self.raised_errors=False
        self.configurator = self.create_configurator()
        self.onto_graph=None
        self.kb_graph=None

    def __raise_error(self,error_msg: str):
        self.raised_errors=True
        raise_error(error_msg=error_msg,running_mode=self.running_mode)

    def create_configurator(self):
        self.configurator = perfect_poc_config(prototype=self,filename=self.filename, running_mode=self.running_mode,
                                               clean_unknwon_keys=self.clean_unknwon_keys,load_data=self.load_data)
        return self.configurator

    def settings_loop_mode(self):
        first_pass= True
        while self.raised_errors or first_pass:
            if self.configurator.file_changed() or first_pass:
                if first_pass:
                    first_pass=False
                    log_level = logger.getEffectiveLevel()
                    logger.setLevel("INFO")
                    logger.info("Entering loop mode: wait for config file change, use CTRL+C to quit loop mode")
                    logger.setLevel(log_level)
                    if not self.raised_errors:
                        self.second_complete_parameters()
                else:
                    logger.info("Config file changed, reload and analyse")
                    self.create_configurator()
                    self.second_complete_parameters()
            time.sleep(1)
        if not self.raised_errors:
            # Si aucune erreur et ontology résussie, quitte
            log_level = logger.getEffectiveLevel()
            logger.setLevel("INFO")
            logger.info("Exit loop mode: configuration file is ready for next step.")
            logger.setLevel(log_level)

    def first_scan_sources(self,auto_save_configuration=True):
        """
        Scanne les fichiers sources identifiés dans la configuration, comlète la configuration avec les paramètres
        par défaut et pose les champs à définir pour la constitution de l'ontologie
        """
        logger.info("FIRST STEP - Scan sources data")
        normalised_source_filenames=[]
        for source_file in self.configurator.source_files:
            try:
                normalised_source_filenames.append(os_path_normpath(source_file))
            except:
                self.__raise_error("Impossible to normalize source filename {}".format(source_file))
                normalised_source_filenames.append(source_file)

        self.configurator.source_files=normalised_source_filenames

        for source_file in self.configurator.source_files:

            logger.debug("Trying to scan file \"{}\"".format(source_file))
            # logger.debug("From file \"{}\", create table object named \"{}\"".format(source_file, table_name))
            _, file_extension = map(lambda x: x.upper(), os.path.splitext(source_file))
            table_name = os.path.basename(source_file)[:-len(file_extension)]
            #Pour le fichier source_table en cours, créée la table
            #Créée ou récupère un dictionnaire table pour le fichier en cours
            if source_file in self.configurator.tables_dict.keys():
                table_section=self.configurator.return_named_table_section(source_file=source_file,table_name=None)
            else:
                table_section=self.configurator.create_table_section(source_file=source_file,table_name=table_name,
                                                                 load_data=False)

            #Le paramètres csv et json existent-t'il ? si non, par défaut
            csv_separator = table_section.table_data_options[CSV_SEPARATOR_KEY] \
                if CSV_SEPARATOR_KEY in table_section.table_data_options.keys() else CSV_SEPARATOR_DEFAULT

            json_rows_key = table_section.table_data_options[JSON_ROWS_KEY] \
                if JSON_ROWS_KEY in table_section.table_data_options.keys() else JSON_DEFAULT_ROWS_KEY

            json_table_name_key = table_section.table_data_options[JSON_TABLE_NAME_KEY] \
                if JSON_TABLE_NAME_KEY in table_section.table_data_options.keys() else JSON_DEFAULT_TABLE_NAME_KEY

            self.configurator.tables_dict[source_file] = copy_deepcopy(table_section.table_params)
            # logger.debug("Table {} params: {}".format(table_name,self.configurator.configuration_dict.__str__()))

            for column_section in table_section.columns_sections.values():
                column_section.load_existing_column(alert_if_missing=False)

            try:
                #extrait les données du fichier dans un dataframe
                dataframes,table_name=read_source_file(source_file,csv_separator=csv_separator,
                                                json_table_name_key=json_table_name_key,json_rows_key=json_rows_key)
                logger.debug("For source file {} table name is {}".format(source_file,table_name))
                table_section.table_name=table_name
                if dataframes is None:
                    continue

                if table_section.source_file_extension in CSV_EXTENSIONS_LIST:
                    dataframe = next(dataframes)
                elif table_section.source_file_extension in JSON_EXTENSIONS_LIST:
                    dataframe = dataframes.pop()
                else:
                    self.__raise_error("Unknown file extension \"{}\"".format(file_extension))
                    return
                del dataframes
            except Exception as e:
                if auto_save_configuration:
                    self.configurator.save_configuration_file()
                # Cette ereur doit provoquer provoquer un stop pour éviter une destruction du fichier de configuration
                self.__raise_error("Impossible to load source file {}, error: {}".format(source_file,e.__str__()))

            #FONCTION JSON EXPAND
            first_pass=True
            for column_name in dataframe.columns:
                column_section= table_section.return_named_column_section(column_name=column_name)
                if column_section is None:
                    continue
                else:
                    if column_section.column_type==CT_JSON_EXPAND:
                        if first_pass:
                            new_dataframe = dataframe.copy()
                            first_pass=False
                        new_dataframe[column_name] = new_dataframe[column_name].apply(table_section.replace_null_line)
                            # new_dataframe[column_name]= new_dataframe[column_name].replace("null",'',regex = True)
                        try:
                            new_dataframe=new_dataframe.join(new_dataframe[column_name].apply(json.loads).apply(pandas.Series))
                        except:
                            for index,line in enumerate(new_dataframe[column_name]):
                                try:
                                    json.loads(line)
                                except:
                                    self.__raise_error("Can't read JSON value \"{}\" for column \"{}.{}\" in line {}".format(line,table_name,column_name,index))

            if not first_pass:
                dataframe=new_dataframe.copy()

            logger.debug("From file \"{}\", scan columns {}".format(source_file,", ".join(dataframe.columns.tolist())))
            for column_name in dataframe.columns:
                column_section= table_section.return_named_column_section(column_name=column_name)
                if column_section is None:
                    logger.info(" -> Create new params for column {}".format(column_name))
                    column_section = table_section.create_column_section(column_name=column_name)
                    column_section.scan_data_init_column(dataframe[column_name])

                else:
                    logger.info(" -> Found existing params for column {}".format(column_name))
                    if column_section.column_type != CT_IGNORE:
                        # Affiche ce message si les paramètres de la colonne existe et si elle n'est pas CT_IGNORE
                        logger.info("Parameters for column \"{}.{}\" are existing, column is ignored"
                                    .format(table_section.table_name, column_name))

            # logger.debug("Table {} params: {}".format(table_name,self.configurator.configuration_dict.__str__()))
        self.scan_json_structs()

        if auto_save_configuration:
            self.configurator.save_configuration_file()
        logger.info("FIRST STEP - Finished")
        return

    def scan_json_structs(self,auto_save_configuration=True):
        """

        """
        logger.info("JSON STEP - Scan json structs")

        for table_section in self.configurator.tables_sections:
            for column_section in table_section.columns_sections.values():
            # for column_name,column_params in table[COLUMNS_KEY].items():
                column_params=column_section.column_params
                if not column_section.check_column_type():
                    continue
                elif column_section.is_ignored():
                    continue
            # Le paramètres csv et json existent-t'il ? si non, par défaut
            csv_separator = table_section.table_data_options[CSV_SEPARATOR_KEY] \
                if CSV_SEPARATOR_KEY in table_section.table_data_options.keys() else CSV_SEPARATOR_DEFAULT

            json_rows_key = table_section.table_data_options[JSON_ROWS_KEY] \
                if JSON_ROWS_KEY in table_section.table_data_options.keys() else JSON_DEFAULT_ROWS_KEY

            json_table_name_key = table_section.table_data_options[JSON_TABLE_NAME_KEY] \
                if JSON_TABLE_NAME_KEY in table_section.table_data_options.keys() else JSON_DEFAULT_TABLE_NAME_KEY

            try:
                #extrait les données du fichier dans un dataframe
                dataframes,table_name=read_source_file(table_section.source_file,csv_separator=csv_separator,
                                                json_table_name_key=json_table_name_key,json_rows_key=json_rows_key)
                logger.debug("For source file {} table name is {}".format(table_section.source_file,table_name))
                table_section.table_name=table_name
                if dataframes is None:
                    continue
            except Exception as e:
                if auto_save_configuration:
                    self.configurator.save_configuration_file()
                # Cette ereur doit provoquer provoquer un stop pour éviter une destruction du fichier de configuration
                self.__raise_error("Impossible to load source file {}, error: {}".format(table_section.source_file,e.__str__()))
            for df_index, dataframe in enumerate(dataframes):
                for column_name in dataframe.columns:
                    column_section= table_section.return_named_column_section(column_name=column_name)
                    if column_section is None:
                        # logger.warning(" -> No params found in config file for data column {}".format(column_name))
                        continue
                    else:
                        if column_section.is_json_struct():
                            # Affiche ce message si les paramètres de la colonne existe et si elle n'est pas CT_IGNORE
                            logger.debug(" -> Found CT_JSON_STRUCT column {}".format(column_name))
                            json_df=dataframe[column_name]
                            for index, line in enumerate(json_df):
                                filtered_line= table_section.replace_null_line(line,replace_with='{}')
                                json_line=json.loads(filtered_line)
                                self.configurator.scan_json_struct(json_dict=json_line,
                                                                   parent_class=table_section.target_class_name)


            # logger.debug("Table {} params: {}".format(table_name,self.configurator.configuration_dict.__str__()))

        dtp_keys_to_remove=[key for key in self.configurator.additional_dtp_params.keys()
                            if key not in self.configurator.automatic_json_dtp]
        op_keys_to_remove=[key for key in self.configurator.additional_op_params.keys()
                           if key not in self.configurator.automatic_json_op]
        for key in dtp_keys_to_remove:
            logger.debug("Remove unused DataType Property {}".format(key))
            del(self.configurator.additional_dtp_params[key])
        for key in op_keys_to_remove:
            logger.debug("Remove unused Object Property {}".format(key))
            del(self.configurator.additional_op_params[key])

        for key in self.configurator.additional_dtp_params.keys():
            xsd_type= self.configurator.additional_dtp_params[key][ADDITIONAL_DTP_XSD_TYPE_KEY]
            if isinstance(xsd_type,list):
                self.configurator.additional_dtp_params[key][ADDITIONAL_DTP_XSD_TYPE_KEY] = Most_Common(xsd_type)

        if auto_save_configuration:
            self.configurator.save_configuration_file()
        logger.info("JSON STEP - Finished")
        return

    def second_complete_parameters(self,auto_save_configuration=True):
        logger.info("SECOND STEP - Prepare data parameters for building graphs")
        self.raised_errors=False
        unset_keys=[key for key,value in self.configurator.ontology_params.items()
                    if type(value)==str and "MANDATORY" in value]
        for key in unset_keys:
            error_msg="Global ontology parameter \"{}\" in section \"{}\" is not correctly set up.".format(key,ONTOLOGY_PARAMS_KEY)
            self.__raise_error(error_msg)

        #Réinitialise le dictionnaire des prédicats
        self.configurator.predicates_dict=dict()

        for table_section in self.configurator.tables_sections:
            for column_section in table_section.columns_sections.values():

                if not column_section.check_column_type():
                    continue
                elif column_section.is_ignored():
                    continue
                #Dans cette section, avant l'appel à complete_column_params(), réaliser les opérations qui

                column_section.complete_column_params()

            table_section.search_primary_keys()

        undeclared_class_error_msg="Undeclared class {} as {} for {}"
        for additional_class_name, additional_class_param in self.configurator.additional_classes_params.items():
            for class_name in additional_class_param[ADDITIONAL_CLASS_SUBCLASS_OF_KEY]:
                if not self.configurator.check_declared_class_name(class_name) and ':' not in class_name:
                    self.__raise_error(undeclared_class_error_msg.format(class_name,"subclass",additional_class_name))
        for additional_dtp_name, additional_dtp_param in self.configurator.additional_dtp_params.items():
            for class_name in additional_dtp_param[ADDITIONAL_DTP_DOMAINS_KEY]:
                if not self.configurator.check_declared_class_name(class_name) and ':' not in class_name:
                    self.__raise_error(undeclared_class_error_msg.format(class_name,"domain",additional_dtp_name))
        for additional_op_name, additional_op_param in self.configurator.additional_op_params.items():
            for class_name in additional_op_param[ADDITIONAL_OP_DOMAINS_KEY]:
                if not self.configurator.check_declared_class_name(class_name) and ':' not in class_name:
                    self.__raise_error(undeclared_class_error_msg.format(class_name,"domain",additional_op_name))
            for class_name in additional_op_param[ADDITIONAL_OP_RANGES_KEY]:
                if not self.configurator.check_declared_class_name(class_name) and ':' not in class_name:
                    self.__raise_error(undeclared_class_error_msg.format(class_name,"range",additional_op_name))


        if auto_save_configuration:
            self.configurator.save_configuration_file()
        if self.raised_errors:
            logger.error("SECOND STEP - FAILED - Data parameters are not ready, complete parameters")
            return False
        else:
            logger.info("SECOND STEP - SUCCESS - Parameters are ready for building ontology graph")
            return True

    def third_build_ontology(self,serialize_ontology=True,auto_save_configuration=True):
        self.raised_errors=False

        logger.info("THIRD STEP - Prepare ontology parameters for building ontology graph")

        self.configurator.check_configuration_defaults()

        onto_graph=perfect_graph(base_namespace=self.configurator.ontology_base_namespace,
                                 uri=self.configurator.ontology_base_uri,
                                 running_mode=self.running_mode,
                                 core_prefixes=self.configurator.modele.LIBRARIES.keys())

        #Par défaut importe l'ontologie
        self.configurator.check_kb_nested_params()

        #Charge les paramètres globaux dans le graph: prefixs, comments, labels, imports, équivalences
        onto_graph.set_ontology_global_params(global_params_dict=self.configurator.ontology_params)

        # Déclaration des classes additionelles
        onto_graph.set_additional_classes(additional_classes_dict=self.configurator.additional_classes_params)

        # Déclaration des objects properties additionelles
        onto_graph.set_additional_object_properties(additional_op_dict=self.configurator.additional_op_params)

        # Déclaration des datatype properties additionelles
        onto_graph.set_additional_datatype_properties(additional_dtp_dict=self.configurator.additional_dtp_params)

        #Déclaration des classes de tables
        for table_section in self.configurator.tables_sections:
            table_class_name=class_name_factory(table_section.table_type_params[TABLE_TARGET_CLASS_NAME_KEY])
            onto_graph.visu_add_node(class_name=table_class_name)
            table_section.table_type_params[TABLE_TARGET_CLASS_NAME_KEY] = table_class_name
            if table_class_name.count(':') == 1:
                prefix, name = table_class_name.split(':')
                if prefix in self.configurator.ontology_params[ONTOLOGY_NAMESPACES_KEY].keys():
                    logger.warning("Can not check existence of class \"{}\" prefixed class \"{}:{}\""
                                       .format(name, prefix,name))
                else:
                    self.raise_error("Undeclared prefix \"{}\ used in table {}, complete ontology namespaces section."
                                     .format(prefix,table_section.table_name))
            else:
                #Définit la classe, son label et sa hiérarchie
                onto_graph.create_table_graph(table_type_params_dict=table_section.table_type_params)

            for column_section in table_section.columns_sections.values():
                column_params = column_section.column_params
                if column_section.is_ignored():
                    continue
                elif column_section.is_primary_key():
                    #Rien à faire: la classe de la table est définie plus haut, les autres paramètres seront utilisés
                    #pour les entités durant la production de la kb
                    continue
                # Pour les colonnes qui pointent vers des clés, Vérifie que la table et concept cibles existent

                elif column_section.is_object_property() or column_section.is_datatype_property():
                    #Predicates
                    subject = onto_graph.return_uriref(column_section.predicate_name)
                    # subject = rdflib.URIRef(onto_graph.base_namespace[column_section.predicate_name])
                    # Labels
                    onto_graph.set_labels(subject,labels_dict=column_params[COLUMN_LABELS_KEY])

                    # Functional property
                    if column_section.is_functional_property():
                        onto_graph.set_new_functional_property(subject)
                    # Domains
                    domain = onto_graph.return_uriref(table_section.target_class_name)
                    # domain = rdflib.URIRef(onto_graph.base_namespace[table_section.target_class_name])
                    onto_graph.set_domain(subject,domain)
                    # is subproperty of
                    onto_graph.set_parents_property(subject, parents_list=column_params[COLUMN_SUBPROPERTY_OF_KEY])
                    if column_section.is_object_property():
                        if not column_section.check_other_target_class_name():
                            error_msg = "Class name \"{}\" attached to object property column \"{}.{}\" not found." \
                                .format(column_section.target_class_name,
                                        column_section.TableSection.table_name.upper(), column_section.column_name)
                            self.__raise_error(error_msg)
                            continue
                        onto_graph.set_new_object_property(subject)
                        # Range
                        if column_section.check_other_target_class_name():
                            range = onto_graph.return_uriref(column_section.target_class_name)
                            # range = rdflib.URIRef(onto_graph.base_namespace[column_section.target_class_name])
                            onto_graph.set_range(subject, range)
                        if column_section.is_object_property_key():
                            if self.configurator.is_additional_class_name(column_section.target_class_name):
                            # C'est une classe externe de type classe additionnelle
                            # Dans ce cas il faut vérifier la formulation des labels des entités
                                column_section.check_entity_labels()

                        #Visualization
                        onto_graph.visu_add_link(predicate_name=column_section.predicate_name,
                                                 source_name=table_section.target_class_name,
                                                 target_name=column_section.target_class_name)

                        # InverseOf
                        if column_section.build_inverseOf_property():
                            inverse_of_predicate = INVERT_OF_PREDICATE_PREFIX+column_section.predicate_name
                            inverse_of_subject = onto_graph.return_uriref(inverse_of_predicate)
                            # inverse_of_subject = rdflib.URIRef(onto_graph.base_namespace[inverse_of_predicate])
                            onto_graph.set_new_inversion_of_object_property(inverse_of_subject,subject)
                            onto_graph.set_labels(inverse_of_subject, labels_dict=column_params[COLUMN_INVERSE_OF_LABELS_KEY])
                            #Visualization
                            onto_graph.visu_add_link(predicate_name=inverse_of_predicate,
                                                     target_name=table_section.target_class_name,
                                                     source_name=column_section.target_class_name)



                    elif column_section.is_datatype_property():
                        # XSD Types Range
                        xsd_range=column_section.read_datatype_property_range()
                        if xsd_range is not None:
                            onto_graph.set_new_datatype_property(subject)
                            onto_graph.set_range(subject, xsd_range)

                elif column_section.is_classes_list():
                    try:
                        conversions_pipe = column_params[COLUMN_CONVERSIONS_PIPE]
                    except:
                        logger.warning("Missing params section \"{}\" in column \"{}.{}\"".format(
                            COLUMN_CONVERSIONS_PIPE,table_section.table_name,column_section.column_name))
                    try:
                        names_set = set(eval(column_params[DATA_LIST_KEY]))
                    except:
                        error_msg="Classes list use the \"{}\" content which is missing or incorrect in column \"{}.{}\""
                        self.__raise_error(error_msg
                                .format(COLUMN_CONVERSIONS_PIPE,table_section.table_name,column_section.column_name))
                        continue
                    for class_name in names_set:
                        if (':' in class_name and (class_name[0] != ':')):
                            error_msg="Column \"{}.{}\" - Classes lists name \"{}\" can't contain character \':\'"
                            logger.warning(error_msg.format(table_section.table_name,column_section.column_name,
                                                            class_name))
                            continue
                        real_class_name=class_name_factory(class_name)
                        if real_class_name is not None:
                            logger.debug("Create class {} for class list column \"{}.{}\""
                                         .format(real_class_name,table_section.table_name,column_section.column_name))
                            label=value_factory(real_class_name,xsd_type=None,conversions_pipe=conversions_pipe)
                            onto_graph.visu_add_node(class_name=real_class_name)
                            subject = onto_graph.base_namespace[real_class_name]
                            labels = {'en': label,'fr': label}
                            onto_graph.set_new_class(subject)
                            # Class Hierarchy - subclassOf table class
                            onto_graph.set_parents_class(subject, parents_list=column_params[COLUMN_SUBCLASS_OF_KEY])
                            onto_graph.set_labels(subject,labels_dict=labels)


        self.onto_graph = onto_graph
        with open("./visualization/data.json","w",encoding=DEFAULT_ENCODING) as f:
            dataset={ "nodes": onto_graph.visu_nodes_list(),"links": onto_graph.visu_links_list() }
            f.write('json_dataset = \'{}\';'.format(json.dumps(dataset,ensure_ascii=True,sort_keys=True)))

        if auto_save_configuration:
            self.configurator.save_configuration_file()

        if self.raised_errors:
            logger.error("THIRD STEP - Ontology paramaters are not correct, please complete.")


        if serialize_ontology and not self.raised_errors:
            logger.info("THIRD STEP - Paramaters are correct, ontology graph is built, now serialize.")
            destination = self.configurator.ontology_output_file_params[ONTOLOGY_OUTPUT_FILE_NAME_KEY]
            destination = os_path_normpath(destination)
            format = self.configurator.ontology_output_file_params[ONTOLOGY_OUTPUT_FILE_FORMAT_KEY]
            onto_graph.graph.serialize(destination=destination,format=format)
            logger.info("THIRD STEP -  SUCCESS, ontology graph is serialized in file {}".format(destination))

        return not self.raised_errors

    def kb_from_json_struct(self, kb_graph: perfect_graph, json_dict: dict, parent_entity: str = None):
        for key, value in json_dict.items():
            value_type = type(value)
            if value_type in {float, int, bool, str} and self.configurator.is_additional_dtp_predicate(key):
                # key est une datatype property pour uuid
                if ((value_type==str) and (value in SKIPPED_VALUES)) or value is None:
                    continue
                predicate_name=predicate_name_factory(key)
                xsd_type = self.configurator.additional_dtp_params[predicate_name][ADDITIONAL_DTP_XSD_TYPE_KEY]
                conv_pipe= self.configurator.additional_dtp_params[predicate_name][ADDITIONAL_DTP_CONVERSIONS_PIPE]
                predicate = kb_graph.related_ontology_base_namespace[predicate_name]
                if xsd_type in XSD_CONF_RDFLIB_CONVERTER.keys():
                    value=value_factory(value=value,xsd_type=xsd_type, conversions_pipe=conv_pipe)
                    object = rdflib.Literal(value, datatype=XSD_CONF_RDFLIB_CONVERTER[xsd_type])
                    kb_graph.add_to_graph((parent_entity,predicate,object))
                else:
                    self.__raise_error("Unknown XSD Type for additional datatype property {}".format(predicate_name))
            elif (value_type in {int, str, dict}) and self.configurator.is_additional_class_name(key):
                # Création d'entité du type de la classe associé à key, uuid = uuid(classe,value)
                # Le line subject est lié object property à l'entité créée
                # Le label de l'entité créée est value
                # Si c'est un dict => c'est tout le dict qui sert pour l'eval de l'uuid et de label
                # Si c'est un dict, ensuite appel récursif
                class_name = class_name_factory(key)
                predicate_name = predicate_name_factory(key)
                adc_params=self.configurator.additional_classes_params[class_name]
                conv_pipe = adc_params[ADDITIONAL_CLASS_CONVERSIONS_PIPE]
                if self.configurator.is_additional_op_predicate(predicate_name):
                    uuid=uuid_generator(class_name,str(value))
                    if uuid is None:
                        continue
                    value = value_factory(value=value, xsd_type=None, conversions_pipe=conv_pipe)
                    entity = kb_graph.return_uriref(str(uuid))
                    # entity = rdflib.URIRef(kb_graph.base_namespace[str(uuid)])
                    entity_type = rdflib.URIRef(kb_graph.related_ontology_base_namespace[class_name])
                    predicate= kb_graph.related_ontology_base_namespace[predicate_name]
                    kb_graph.set_type(entity,entity_type)
                    kb_graph.add_to_graph((parent_entity,predicate,entity))
                    # logger.debug((parent_entity,predicate,entity))
                    if value_type==dict:
                        d_label=dict_label(dict_name=value)
                        labels = {'en': d_label, 'fr': d_label}
                        self.kb_from_json_struct(kb_graph=kb_graph,json_dict=value,parent_entity=entity)
                    else:
                        local_label= first_char_upper(str(value))
                        labels = {'en': local_label, 'fr': local_label}
                    kb_graph.set_labels(subject=entity, labels_dict=labels)

                    # Extra URI field
                    if ADDITIONAL_CLASS_EXTRA_URI_MASK_KEY in adc_params:
                        extra_uri_template = adc_params[ADDITIONAL_CLASS_EXTRA_URI_MASK_KEY]
                        if (type(extra_uri_template) is str) \
                                and (extra_uri_template.count(ADDITIONAL_CLASS_EXTRA_URI_MASK) > 0):
                            predicate_name=predicate_name_factory(ADDITIONAL_CLASS_EXTRA_URI_PREDICATE)
                            extra_uri_predicate = rdflib.URIRef(kb_graph.related_ontology_base_namespace[predicate_name])
                            extra_uri=extra_uri_template.replace(ADDITIONAL_CLASS_EXTRA_URI_MASK,str(value))
                            object = rdflib.Literal(extra_uri, datatype=XSD_RDFLIB_ANYURI)
                            kb_graph.add_to_graph((entity,extra_uri_predicate,object))
                else:
                    self.__raise_error("Missing predicate {} for class {}. Rerun config loop to repair.".format(predicate_name,class_name))
                    logger.debug("Known predicates : {}".format(set(self.configurator.additional_op_params.keys())))

            elif value_type == list:
                if len(value) == 0:
                    continue
                class_name = class_name_factory(key)
                # class_name = first_char_upper(key)

                if any([isinstance(item, dict) for item in value]):
                    # c'est une liste comprenant au moins un dictionnaire alors la clé parente est une classe
                    # Appel récursif de la fonction item par item
                    if not self.configurator.is_additional_class_name(class_name):
                        self.__raise_error("Dictionnary value needs to refer to a class, missing class for {}"
                                           .format(class_name))
                        continue
                if self.configurator.is_additional_class_name(class_name):
                    predicate = kb_graph.related_ontology_base_namespace[predicate_name_factory(key)]
                    entity_type = rdflib.URIRef(kb_graph.related_ontology_base_namespace[class_name])
                    conv_pipe = self.configurator.additional_classes_params[class_name][ADDITIONAL_CLASS_CONVERSIONS_PIPE]
                    for item in value:
                        # Pour chaque dictionnaire de la liste, applique le scan
                        uuid = uuid_generator(class_name, str(item))
                        if uuid is None:
                            continue
                        entity = kb_graph.return_uriref(str(uuid))
                        # entity = rdflib.URIRef(kb_graph.base_namespace[str(uuid)])
                        kb_graph.set_type(entity,entity_type)
                        kb_graph.add_to_graph((parent_entity,predicate,entity))
                        if type(item) == dict:
                            d_label = dict_label(dict_name=item)
                            labels = {'en': d_label, 'fr': d_label}
                            self.kb_from_json_struct(kb_graph=kb_graph, json_dict=item, parent_entity=entity)
                        else:
                            item = value_factory(value=item, xsd_type=None, conversions_pipe=conv_pipe)
                            local_label=first_char_upper(str(item))
                            labels = {'en': local_label, 'fr': local_label}
                        kb_graph.set_labels(subject=entity,labels_dict=labels)

                elif self.configurator.is_additional_dtp_predicate(key):
                    predicate_name = predicate_name_factory(key)
                    xsd_type = self.configurator.additional_dtp_params[predicate_name][ADDITIONAL_DTP_XSD_TYPE_KEY]
                    conversions_pipe = self.configurator.additional_dtp_params[predicate_name][ADDITIONAL_DTP_CONVERSIONS_PIPE]
                    predicate = kb_graph.related_ontology_base_namespace[predicate_name]
                    if xsd_type not in XSD_CONF_RDFLIB_CONVERTER.keys():
                        self.__raise_error("Unknown XSD Type for additional datatype property {}".format(predicate_name))
                        continue
                    for item in value:
                        if ((type(item) == str) and (item in SKIPPED_VALUES)) or item is None:
                            continue
                        item=value_factory(value=item,xsd_type=xsd_type,conversions_pipe=conversions_pipe)
                        if item is not None:
                            object = rdflib.Literal(item, datatype=XSD_CONF_RDFLIB_CONVERTER[xsd_type])
                            kb_graph.add_to_graph((parent_entity, predicate, object))
                else:
                    logger.warning("Unknown model for JSON key: {}".format(key))
            else:
                if value is not None and value!='':
                    logger.debug("Unknwon type {} for value {}".format(value_type, value))

    def fourth_build_kb(self,serialize_kb=True,auto_save_configuration=True):
        logger.info("LAST STEP - Prepare kb parameters for building kb graph")
        self.raised_errors=False

        unset_keys=[key for key,value in self.configurator.kb_params.items()
                    if type(value)==str and ("MANDATORY" in value)]
        if unset_keys.__len__()>0:
            for key in unset_keys:
                error_msg="Global parameter \"{}\" in section \"{}\" is not correctly set up.".format(key,KB_PARAMS_KEY)
                self.__raise_error(error_msg)
            self.__raise_error("LAST STEP - Can not build graph, must stop.")
            return False

        kb_graph = perfect_graph(base_namespace=self.configurator.kb_base_namespace,
                                 uri=self.configurator.kb_base_uri,
                                 running_mode=self.running_mode,
                                 core_prefixes=self.configurator.modele.LIBRARIES.keys())

        # Par défaut importe l'ontologie
        self.configurator.check_kb_nested_params()

        # Charge les paramètres globaux dans le graph, contruit l'espace des noms en incluant ceux de l'ontologie
        kb_graph.set_prefixes(prefixes_dict=self.configurator.ontology_namespaces)
        kb_graph.set_kb_global_params(global_params_dict=self.configurator.kb_params)
        logger.debug("Loaded namespaces: {}".format(self.configurator.ontology_namespaces))
        kb_graph.related_ontology_base_namespace= rdflib.Namespace(self.configurator.ontology_base_namespace)

        for table_section in self.configurator.tables_sections:
            # PHASE CONTROLE DES CLES PRIMAIRES - TOUR DES CLES PRIMAIRES POUR TROUVER CELLE DE LA TABLE ET CELLES
            # DES CLASSES ADDITIONELLES
            table_section.search_primary_keys()
            #Le paramètres csv et json existent-t'il ? si non, par défaut
            csv_separator = table_section.table_data_options[CSV_SEPARATOR_KEY] \
                if CSV_SEPARATOR_KEY in table_section.table_data_options.keys() else CSV_SEPARATOR_DEFAULT

            json_rows_key = table_section.table_data_options[JSON_ROWS_KEY] \
                if JSON_ROWS_KEY in table_section.table_data_options.keys() else JSON_DEFAULT_ROWS_KEY

            json_table_name_key = table_section.table_data_options[JSON_TABLE_NAME_KEY] \
                if JSON_TABLE_NAME_KEY in table_section.table_data_options.keys() else JSON_DEFAULT_TABLE_NAME_KEY
            dataframes, table_name =  table_section.read_source_file(csv_separator=csv_separator,
                                                json_table_name_key=json_table_name_key,json_rows_key=json_rows_key)
            limited_pk_found_set=set()
            limited_pk_found_achieved=False
            self.raised_errors=False
            table_failed=False


            for df_index,dataframe in enumerate(dataframes):

                # FONCTION JSON EXPAND
                first_pass = True
                for column_name in dataframe.columns:
                    column_section = table_section.return_named_column_section(column_name=column_name)
                    if column_section is None:
                        self.__raise_error(" -> No params found in config file for data column {}".format(column_name))
                        continue
                    else:
                        if column_section.column_type == CT_JSON_EXPAND:
                            if first_pass:
                                new_dataframe = dataframe.copy()
                                first_pass = False
                            new_dataframe = new_dataframe.join(
                                new_dataframe[column_name].apply(json.loads).apply(pandas.Series))
                if not first_pass:
                    dataframe = new_dataframe.copy()

                if table_failed:
                    break
                if limited_pk_found_achieved:
                    logger.info("All primary keys found.")
                    break
                logger.info('Reading block n°{} of {} lines in file {}'
                            .format(df_index,PANDAS_CHUNKSIZE,table_section.source_file))
                for index,line in dataframe.iterrows():
                    if table_failed:
                        break
                    if (table_section.limited_primary_keys_set):
                        if (str(line[table_section.primary_key_column]) not in table_section.limited_pk_set):
                            continue
                        else:
                            limited_pk_found_set.add(line[table_section.primary_key_column])
                            if (table_section.limited_pk_set.__len__()==limited_pk_found_set.__len__()):
                                limited_pk_found_achieved=True
                                break

                    # L'uuid est calculé au niveau de la ligne et non dans le bloc clé-primaire
                    # Dans le cas contraire, selon l'ordre de traitement des colonnes, l'uuid ne serait pas correct
                    # Traité l'uuid au niveau ligne évite ce risque

                    uuid=table_section.uuid_construct(df_line=line,line_index=index)
                    if uuid is None:
                        continue
                    line_subject = kb_graph.base_namespace[str(uuid)]
                    target_class_name=table_section.target_class_name
                    line_type= kb_graph.related_ontology_base_namespace[target_class_name]
                    kb_graph.set_type(subject=line_subject, type=line_type)

                    for column_section in table_section.columns_sections.values():
                        if column_section.is_ignored():
                            continue

                        if column_section.is_primary_key():
                            if column_section.check_entity_labels():
                                # Construct line entity Labels with column values
                                kb_graph.set_labels(line_subject, labels_dict=column_section.build_entity_labels(line))
                            else:
                                table_failed=True
                                continue

                        if column_section.is_datatype_property() or column_section.is_object_property():
                            #Le prédicat est pris dans le namespace de l'ontologie
                            predicate = kb_graph.related_ontology_base_namespace[column_section.predicate_name]
                        if column_section.is_datatype_property():
                            value= column_section.read_value(line)
                            if value is None:
                                continue
                            else:
                                column_datatype_property_range=column_section.read_datatype_property_range()
                                if column_datatype_property_range is None:
                                    continue
                                else:
                                    object = rdflib.Literal(value, datatype=column_datatype_property_range)

                                # La colonne définit une propriété associée à une entité de la classe de la table
                                # Dans ce cas c'est le subject défini au niveau de la ligne qu'il faut relever
                                kb_graph.add_to_graph((line_subject, predicate, object))

                        if column_section.is_object_property():
                            # L'uuid de l'objet se calcule au niveau de la colonne en cours
                            # On déclare les prédicats qui seront associés entités à créer
                            uuid= column_section.uuid_construct(df_line=line,line_index=index)
                            if uuid is None:
                                continue
                            else:
                                object = kb_graph.return_uriref(str(uuid))
                                # object = rdflib.URIRef(kb_graph.base_namespace[str(uuid)])
                                kb_graph.add_to_graph((line_subject, predicate, object))

                        if column_section.is_object_property_key():
                            # C'est une classe externe soit issue d'une autre table soit une classe additionnelle
                            if column_section.check_other_additional_class_name() \
                                    and not column_section.check_entity_labels():
                                # Contrôle la formulation des labels de l'entité de classe externe à créer
                                table_failed = True
                                continue
                            local_entity_uuid=column_section.uuid_construct(df_line=line,line_index=index)
                            if local_entity_uuid is None:
                                continue

                            #Définit le type de l'entité qui doit être déclarée du type de la classe externe
                            #Subject devient object: on va parler des entités créées dans le prédicat précédent
                            local_entity_subject = object
                            local_entity_type=rdflib.URIRef(kb_graph.related_ontology_base_namespace[column_section.target_class_name])
                            # kb_graph.set_type(subject=local_entity_subject,type=local_entity_type)
                            kb_graph.set_type(subject=object,type=local_entity_type)

                            #Les labels d'entité sont définis ici si c'est une classe additionelle
                            # Si non, c'est la kb de l'autre table qui les définira
                            if column_section.check_other_additional_class_name():
                                # Construct line entity Labels with column values
                                local_entity_labels_dict= column_section.build_entity_labels(line)
                                kb_graph.set_labels(local_entity_subject, labels_dict=local_entity_labels_dict)
                        if column_section.is_json_struct():
                            value = column_section.read_value(line)
                            filtered_line = table_section.replace_null_line(value, replace_with='{}')
                            json_line = json.loads(filtered_line)
                            if len(json_line)>0:
                                self.kb_from_json_struct(kb_graph=kb_graph,json_dict=json_line,parent_entity=line_subject)
                            else:
                                continue

                        if column_section.is_classes_list():
                            #Attribue l'entité en cours à la classe donnée
                            value = column_section.read_value(line,apply_value_factory=False)
                            if value is None:
                                continue

                            class_name= class_name_factory(value)
                            if class_name!='':
                                line_type=kb_graph.related_ontology_base_namespace[class_name]
                                kb_graph.set_type(subject=line_subject, type=line_type)


        if auto_save_configuration:
            self.configurator.save_configuration_file()

        if serialize_kb and not self.raised_errors:
            logger.info("LAST STEP - Paramaters are correct, KB graph is built, now serialize.")
            destination = self.configurator.kb_output_file_params[KB_OUTPUT_FILE_NAME_KEY]
            destination = os_path_normpath(destination)
            format = self.configurator.kb_output_file_params[KB_OUTPUT_FILE_FORMAT_KEY]
            kb_graph.graph.serialize(destination=destination,format=format)
            logger.info("LAST STEP - KB graph is serialized in file {}".format(destination))
        elif self.raised_errors:
            logger.info("LAST STEP - Failed Paramaters are correct, KB graph is built, now serialize.")

        self.kb_graph=kb_graph
        return not self.raised_errors
