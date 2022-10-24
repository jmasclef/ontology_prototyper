import os
import pandas

from yaml import safe_load, safe_dump,dump,load
from unicodedata import category as unicodedata_category, normalize as unicodedata_normalize
from os.path import normpath as os_path_normpath
from . perfect_poc_modele_structure import *
from . perfect_poc_lib_column import ColumnSection

class TableSection():

        def __init__(self,configuration,source_file:str,table_name:str,load_data=True,clean_unknwon_keys=False):
            logger.debug("Table object creation begins for table {}.".format(table_name))
            self.source_file=os_path_normpath(source_file)
            self.table_name=table_name
            self.configuration=configuration
            self.modele=self.configuration.modele
            _, self.source_file_extension= map(lambda x: x.upper(),os.path.splitext(source_file))
            logger.debug(" - Existing keys in tables dict: {}".format(", ".join(self.configuration.tables_dict.keys())))
            logger.debug(" - Create object table named \"{}\" for file \"{}\"".format(table_name,source_file))
            if source_file in self.configuration.tables_dict.keys():
                logger.debug(" - Found existing params for this table")
                self.table_params = self.configuration.tables_dict[source_file]
            else:
                logger.debug(" - Create new params for this table")
                self.table_params = dict()

            self.table_params[TABLE_NAME_KEY] = table_name

            # logger.debug("----------------")
            # logger.debug("TABLE PARAMS 1 = {}".format(self.table_params.__str__()))
            # logger.debug("----------------")

            for key in self.modele.TABLE_KEYS:
                self.table_params[key]=init_struct(modele=self.modele,conf_dict=self.table_params,key=key)

            # logger.debug("----------------")
            # logger.debug("TABLE PARAMS 2 = {}".format(self.table_params.__str__()))
            # logger.debug("----------------")

            self.table_type_params=self.table_params[TABLE_TYPE_PARAMS_KEY]
            self.table_data_options= self.table_params[TABLE_DATA_OPTIONS_KEY]
            self.table_type=self.table_params[TABLE_TYPE_KEY]

            if self.table_params[TABLE_COLUMNS_KEY].keys().__len__()==2:
                self.table_params.setdefault(TABLE_TYPE_KEY, TABLE_TYPE_DEFAULT)
            else:
                self.table_params.setdefault(TABLE_TYPE_KEY, TT_CLASS)
                self.table_params[TABLE_TYPE_KEY]=TT_CLASS

            if self.is_class_table_type():
                # Initialise de façon récursive les clefs/valeurs pour une table TT_CLASS
                for key in self.modele.TABLE_PARAMS_KEYS[TT_CLASS]:
                    self.table_type_params[key]=init_struct(self.modele,self.table_type_params, key)
                self.target_class_name= self.table_type_params[TABLE_TARGET_CLASS_NAME_KEY]
                if (self.target_class_name == "") or (self.target_class_name is None):
                    self.__construct_class_name()
                if self.table_type_params[TABLE_TARGET_CLASS_LABELS_KEY]==dict():
                    self.table_type_params[TABLE_TARGET_CLASS_LABELS_KEY] = default_labels(self.target_class_name)
            elif self.is_datatype_values_table_type():
                #Initialise de façon récursive les clefs/valeurs pour une table TT_DATATYPE_VALUES
                for key in self.modele.TABLE_PARAMS_KEYS[TT_DATATYPE_VALUES]:
                    self.table_type_params[key]=init_struct(self.modele,self.table_type_params, key)
                self.target_class_name= None

            # logger.debug("Table options: {}".format(self.table_data_options))
            # Charge le set limited_primary_keys_set
            if self.table_data_options[COLUMN_LIMITED_PK_LIST_KEY] is None:
                self.limited_primary_keys_set=None
            else:
                self.limited_primary_keys_set = set(self.table_data_options[COLUMN_LIMITED_PK_LIST_KEY])

            self.primary_key_column = None
            self.additional_primary_keys = dict()
            self.specific_skipped_values_set = SKIPPED_VALUES.union(self.table_data_options[SPECIFIC_SKIPPED_VALUES_KEY])
            self.stop_on_duplicate_key = self.table_data_options[STOP_ON_DUPLICATE_PRIMARY_KEY]
            self.uuids_set=set()
            #Contrôle les noms des classes parentes à la classe de table
            init_struct(self.modele,self.table_type_params,TABLE_CLASS_SUBCLASS_OF_KEY)
            for parent_class in self.table_type_params[TABLE_CLASS_SUBCLASS_OF_KEY]:
                self.configuration.check_declared_class_name(class_name=parent_class)

            if load_data:
                if self.table_type not in self.modele.TABLE_PARAMS_KEYS.keys():
                    self.raise_error("Unknown table type \"{}\" for table \"{}\"".format(self.table_type, table_name))
                if self.target_class_name is None or (class_name_factory(self.target_class_name) == ''):
                    self.raise_error("Bad class name for table \"{}\".".format(self.table_section.table_name))

            logger.debug(" - For table {}, existing columns:  {}"
                  .format(table_name,", ".join(self.table_params[TABLE_COLUMNS_KEY].keys())))
            #Créée les colonnes à partir des colonnes déjà existantes et charge les informations si demandé
            # self.columns_sections=[]
            self.columns_sections=dict()
            for column_name in self.table_params[TABLE_COLUMNS_KEY].keys():
            # for column_name in self.table_params[TABLE_COLUMNS_KEY].keys():
                column_section=self.create_column_section(column_name=column_name)
                if load_data:
                    #Charge la colonne existante
                    column_section.load_existing_column()
                    #Corrige la colonne existante
                    column_section.complete_column_params(clean_unknwon_keys=clean_unknwon_keys)
                # self.columns_sections.append(column_section)
                self.columns_sections[column_name]=column_section
                logger.debug("--> load column: {}" .format(column_name))

            self.check_unexpected_keys(clean_unknwon_keys=clean_unknwon_keys)
            # logger.debug("Tables keys: {}".format(self.configuration.tables_dict.keys()))
            # logger.debug(" - Add Table \"{}\" to tables keys".format(source_file))
            # Insère la nouvelle table dans la configuration: NON fait depuis la fonction appelante
            # self.configuration.tables_dict[source_file] = self.table_params
            logger.debug("Table object creation is finished for table {}.".format(table_name))

        def check_unexpected_keys(self,clean_unknwon_keys=False):
            unexpected_keys_list = self.table_params.keys() - self.modele.TABLE_KEYS

            if unexpected_keys_list.__len__()>0:
                logger.debug("Useless keys \"{}\" in table structure \"{}\"."
                               .format(unexpected_keys_list, self.table_name))
                if clean_unknwon_keys:
                    for key in unexpected_keys_list:
                        del self.table_params[key]
                    logger.info("Useless keys deleted")
                else:
                    logger.debug("Use \"--clean_keys\" option to delete useless keys.")

        def raise_error(self, error_msg: str):
            self.configuration.raise_error(error_msg=error_msg)

        def replace_null_line(self,line: str,replace_with:str='{}'):
            if line is None or pandas.isna(line) or line in self.specific_skipped_values_set:
                return replace_with
            else:
                return line
        def read_source_file(self,csv_separator=None,json_table_name_key=None,json_rows_key=None):
            return read_source_file(source_file=self.source_file,csv_separator=csv_separator,
                                                json_table_name_key=json_table_name_key,json_rows_key=json_rows_key)

        def contains_column_section(self,column_name:str):
            #Utilise les paramètres réels et non les colonnes chargées à cause des risque de synchro
            #Cette fonction est appelée pour vérifier la syntaxe des labels des entités à un moment où toutes les
            #Colonnes ne sont pas encore chargées
            #Utiliser ça
            return column_name in self.table_params[TABLE_COLUMNS_KEY].keys()
            #Et non ça
            # return column_name in self.columns_sections.keys()


        def return_named_column_section(self,column_name:str):
            if self.contains_column_section(column_name):
                return self.columns_sections[column_name]
            else:
                #Les logs sont produits selon la situation: scanner ne fait pas d'erreur, produire la kb oui
                # logger.warning("No column found for name {} in table {}".format(column_name,self.table_name))
                # self.raise_error("No column found for name {} in table {}".format(column_name,self.table_name))
                return None

        def is_class_table_type(self):
            return (self.table_params[TABLE_TYPE_KEY] == TT_CLASS)

        def is_datatype_values_table_type(self):
            if self.table_params[TABLE_TYPE_KEY]==TT_DATATYPE_VALUES:
                if self.table_params[TABLE_COLUMNS_KEY].__len__()!=2:
                    self.raise_error("Table \"{}\" must have only two columns".format(self.table_name))
                    self.raise_error(" -- > A TT_CLASS table must have only two columns: one for ID and one for value")
                else:
                    has_primary_key= False
                    has_datatype_value = False
                    for column_params in self.table_params[TABLE_COLUMNS_KEY].values():
                        if column_params[COLUMN_TYPE_KEY]==CT_PRIMARY_KEY:
                            has_primary_key = True
                        elif column_params[COLUMN_TYPE_KEY]==CT_DATATYPE_PROPERTY_VALUE:
                            has_datatype_value = True
                    if not has_primary_key:
                        self.raise_error("Table \"{}\" must have a primary key column".format(self.table_name))
                        self.raise_error(
                            " -- > A TT_CLASS table must have a CT_PRIMARY_KEY column for storing IDs")
                        return False
                    elif not has_datatype_value:
                        self.raise_error("Table \"{}\" must have a value column".format(self.table_name))
                        self.raise_error(
                            " -- > A TT_CLASS table must have a CT_DATATYPE_PROPERTY_VALUE column for storing values")
                        return False
                    else:
                        return True
            else:
                return False

        def search_primary_keys(self):
            """
            Pour la kb, recensement des colonnes de clés primaires au sein d'une table
            """
            self.primary_key_column = None
            self.additional_primary_keys = dict()
            # PHASE CONTROLE DES CLES PRIMAIRES - TOUR DES CLES PRIMAIRES POUR TROUVER CELLE DE LA TABLE ET CELLES
            # DES CLASSES ADDITIONELLES
            for column_section in self.columns_sections.values():
                if column_section.is_primary_key():
                    # if column_section.column_params[COLUMN_ADDITIONAL_CLASS_NAME_ATTACHMENT_KEY] is None:
                        # CLE PRIMAIRE ASSOCIEE A LA TABLE OUVERTE
                    if self.primary_key_column is None:
                        self.primary_key_column = column_section.column_name
                    else:
                        error_msg="Doubled primary key column (CT_PRIMARY_KEY parameter) found for table \"{}\""
                        self.raise_error(error_msg.format(self.table_name))
                elif column_section.is_object_property_key():
                    # CLE PRIMAIRE ASSOCIEE A UNE CLASSE ADDITIONELLE INCLUSE DANS LA TABLE OUVERTE
                    self.additional_primary_keys[column_section.target_class_name] = column_section.column_name
            if self.primary_key_column is None:
                error_msg = "No primary key column (CT_PRIMARY_KEY parameter) found for table \"{}\""
                self.raise_error(error_msg.format(self.table_name))

        def uuid_construct(self, df_line:pandas.Series, line_index:int):
            ## Contruit un uuid à partir de la clé primaire de la table
            value=df_line[self.primary_key_column]

            if (value is None) or pandas.isna(value) or (value in self.specific_skipped_values_set):
                error_msg="Null primary key value \"{}\" in table {} at line {} (begin at 0)."\
                    .format(value,self.table_name,line_index)
                self.raise_error(error_msg)
                return None

            if self.table_params[TABLE_COLUMNS_KEY][self.primary_key_column][COLUMN_XSD_TYPE_KEY] == XSD_CONF_INT_TYPE:
                # Les entiers sont parfois lus de la forme "4.0" au lieu de "4", retirer la section décimales
                uuid = uuid_generator(self.target_class_name, int(value))
            else:
                uuid = uuid_generator(self.target_class_name, value)

            if uuid in self.uuids_set:
                error_msg = 'Duplicate primary key \"{}\" line {} (begin on 0) far table {}'\
                    .format(value, line_index, self.table_name)
                if self.stop_on_duplicate_key:
                    self.raise_error(error_msg)
                else:
                    logger.warning(error_msg)
            else:
                self.uuids_set.add(uuid)

            return uuid

        def __construct_class_name(self,avoid_duplicate=False):
            name = ''.join(c for c in unicodedata_normalize('NFD', self.table_name) if unicodedata_category(c) != 'Mn')
            for key, value in CHARACTERS_SUBSTITION_LIST.items():
                name = name.replace(key, value)
            name = regex_predicate_and_class_names(name)
            words_list = [ word for word in name.split() if word not in WORDS_TO_REMOVE]
            #Pour les classes, garde la majuscule sur le premier mot
            target_class_name = ''.join([first_char_upper(word) for word in words_list])

            if avoid_duplicate:
                duplicate_index = 1
                while self.configuration.check_declared_class_name(target_class_name):
                    duplicate_index += 1
                    target_class_name = target_class_name + str(duplicate_index)

            self.target_class_name = target_class_name
            self.table_type_params[TABLE_TARGET_CLASS_NAME_KEY] = target_class_name

        def create_column_section(self,column_name: str):
            return ColumnSection(self,column_name)
