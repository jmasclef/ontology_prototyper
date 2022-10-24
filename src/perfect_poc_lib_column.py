
import pandas

from yaml import safe_load, safe_dump,dump,load
from unicodedata import category as unicodedata_category, normalize as unicodedata_normalize
from . perfect_poc_modele_structure import *

class ColumnSection(dict):
    def __init__(self, table_section, column_name: str):
        self.table_section=table_section
        self.configuration=table_section.configuration
        self.modele=self.configuration.modele
        self.column_name = column_name

    def load_existing_column(self,alert_if_missing=True):
        try:
            self.column_params = self.table_section.table_params[TABLE_COLUMNS_KEY][self.column_name]
            self.column_type =  self.column_params[COLUMN_TYPE_KEY]

        except:
            if alert_if_missing:
                logger.error("Impossible to load correct parameters for column \"{}.{}\", column is ignored."
                             "Delete column and re-run the scan step or correct basic column parameters.")
            return False

        return True

    def raise_error(self, error_msg: str):
        self.table_section.raise_error(error_msg=error_msg)

    def check_column_type(self):
        if self.column_type not in self.modele.COLUMNS_TYPES_LIST:
            if self.column_type==COLUMN_TYPE_DEFAULT:
                error_msg = "Column \"{}.{}\" has an undefined type identifier." \
                    .format(self.table_section.table_name,self.column_name)
            else:
                error_msg="Column \"{}.{}\" has an unknown type identifier \"{}\"."\
                    .format(self.table_section.table_name,self.column_name,self.column_type)
            self.raise_error(error_msg)
            return False
        else:
            return True

    # def check_xsd_type(self):
    #     if COLUMN_XSD_TYPE_KEY not in self.column_params:
    #         self.__raise_error("No XSD type for column \"{}.{}\"."
    #                            .format(self.table_section.table_name, self.column_name))
    #         return False
    #     elif self.column_params[COLUMN_XSD_TYPE_KEY] not in XSD_ACCEPTED_TYPES_SET:
    #         self.__raise_error("Unknown XSD type \"{}\" for column {}.{}."
    #                            .format(self.column_params[COLUMN_XSD_TYPE_KEY], self.table_section.table_name,
    #                                    self.column_name))
    #         return False
    #     else:
    #         return True

    def is_ignored(self):
        return (self.column_type==CT_IGNORE) or (self.column_type==CT_JSON_EXPAND)

    def is_primary_key(self):
        return self.column_type==CT_PRIMARY_KEY

    def is_json_struct(self):
        return self.column_type==CT_JSON_STRUCT

    def is_object_property_key(self):
        return self.column_type==CT_OBJECT_PROPERTY_KEY

    def is_object_property_value(self):
        return self.column_type==CT_OBJECT_PROPERTY_VALUE

    def is_datatype_property_key(self):
        return self.column_type==CT_DATATYPE_PROPERTY_KEY

    def is_datatype_property_value(self):
        return self.column_type==CT_DATATYPE_PROPERTY_VALUE

    def is_classes_list(self):
        return self.column_type==CT_CLASSES_LIST_KEY

    def is_datatype_property(self):
        return self.column_type in {CT_DATATYPE_PROPERTY_KEY, CT_DATATYPE_PROPERTY_VALUE}

    def is_object_property(self):
        if self.column_type in {CT_OBJECT_PROPERTY_KEY, CT_OBJECT_PROPERTY_VALUE}:
            return True
        else:
            return False

    def is_functional_property(self):
        try:
            return self.column_params[COLUMN_FUNCTIONAL_PROPERTY_KEY]
        except:
            return False

    def build_inverseOf_property(self):
        try:
            return self.column_params[COLUMN_INVERSE_OF_KEY]
        except:
            return False

    def check_entity_labels(self,already_warned=list()):
        for lang, label in self.column_params[KB_ENTITIES_LABELS_STRUCT_KEY].items():
            for word in re.findall('\{.*?\}', label):
                column_name=word[1:-1]
                if not self.table_section.contains_column_section(column_name) and (column_name not in already_warned):
                    already_warned.append(column_name)
                    error_msg = "Column \"{}\" not found in the label formulation \"{}\" for entities \"{}\""
                    logger.error(error_msg.format(word[1:-1], lang, self.target_class_name))
                    error_msg = " --> Occured in column \"{}.{}\""
                    self.raise_error(error_msg.format(self.table_section.table_name,self.column_name))
        return True if already_warned.__len__()==0 else False

    def build_entity_labels(self,df_line:pandas.Series):
        entity_labels_dict=dict()
        for lang, label in self.column_params[KB_ENTITIES_LABELS_STRUCT_KEY].items():
            entity_label = label
            for word in re.findall('\{.*?\}', label):
                column_name=word[1:-1]
                if self.table_section.contains_column_section(column_name):
                    # value= first_char_upper(str(df_line[column_name]))
                    value= first_char_upper(str(self.table_section.columns_sections[column_name].read_value(df_line)))
                else:
                    #pas de message d'erreur sinon production d'erreur à chaque création d'entité
                    #laisse l'etiquette introuvable dans le label
                    value=word
                entity_label = entity_label.replace(word, value)

            entity_labels_dict[lang]=entity_label
        return entity_labels_dict

    def scan_data_init_column(self, dataframe_column):
        """
        SECTION COMPLIQUEE
        COMPATIBILITE CSV JSON AVEC LES NAN ET NULL QUI DECLENCHENT DES TYPES FLOAT OU STRING
        """
        try:
            values_set = set(dataframe_column.dropna().tolist())
        except:
            self.raise_error("If JSON_EXPAND column, seems to be too deep to expand, use CT_JSON_STRUCTURE")
            sys.exit()
        if self.table_section.source_file_extension in CSV_EXTENSIONS_LIST:
            # Pour les CSV supprime les entrées \N qui sont pris comme np.nan en JSON
            for skip_value in self.table_section.specific_skipped_values_set:
                try:
                    values_set.remove(skip_value)
                except:
                    pass
        values_set_len = values_set.__len__()

        # Définit un type inconnu par défaut
        xsd_type = XSD_TYPE_UNKNOWN_LABEL
        if (xsd_type == XSD_TYPE_UNKNOWN_LABEL):
            try:
                # Détection d'ints transformés en float ou strings selon le format CSV ou JSON
                if ((self.source_file_extension in JSON_EXTENSIONS_LIST) and (
                all([int(v) == v for v in values_set]))) \
                        or (
                        (self.source_file_extension in CSV_EXTENSIONS_LIST) and (
                all([str(int(v)) == str(v) for v in values_set]))):
                    xsd_type = XSD_CONF_INT_TYPE
                    values_set = {int(v) for v in values_set}
                    # logger.info(COLUMN_TYPE_CHANGE_INFO.format(self.table_name, self.column_name, xsd_type))
            except:
                pass
        if (xsd_type == XSD_TYPE_UNKNOWN_LABEL):
            try:
                # Détection de floats transformés en strings pour le format CSV, le pb n'existe pas pour JSON
                if ((self.source_file_extension in CSV_EXTENSIONS_LIST) and (
                all([str(float(v)) == str(v) for v in values_set]))):
                    xsd_type = XSD_CONF_FLOAT_TYPE
                    values_set = {float(v) for v in values_set}
                    # logger.info(COLUMN_TYPE_CHANGE_INFO.format(self.table_name, self.column_name, xsd_type))
            except:
                pass
        # Détecte les sets binaires
        if (values_set_len in {1,2}) and (values_set in BOOLEAN_SETS_LIST):
            xsd_type = XSD_CONF_BOOLEAN_TYPE
            # logger.info(COLUMN_TYPE_CHANGE_INFO.format(self.table_section.table_name, self.column_name, xsd_type))
        sample_data = self.__extract_sample_data(values_set)
        if (xsd_type == XSD_TYPE_UNKNOWN_LABEL):
            if all([(self.__read_date(value,cast_to_short_date=True)[1] == XSD_CONF_DATE_TYPE) for value in values_set]):
                (_,xsd_type) = self.__read_date(sample_data,cast_to_short_date=False)

        pandas_dtype = str(dataframe_column.dtype)
        if xsd_type == XSD_TYPE_UNKNOWN_LABEL:
            if pandas_dtype in XSD_TYPES_CONVERSION:
                xsd_type = XSD_TYPES_CONVERSION[pandas_dtype]
            else:
                xsd_type = XSD_CONF_STRING_TYPE
        self.column_params = dict()
        self.column_params[COLUMN_TYPE_KEY] = COLUMN_TYPE_DEFAULT
        self.column_params[SAMPLE_DATA_KEY] = sample_data
        self.column_params[DATA_DIVERSITY_KEY] = values_set_len
        self.column_params[DATA_LIST_KEY] = str(values_set) if values_set_len <= 20 else ""
        self.column_params[COLUMN_XSD_TYPE_KEY] = xsd_type

        # Ajoute les paramètres de colonne à la table

        self.configuration.tables_dict[self.table_section.source_file][TABLE_COLUMNS_KEY][self.column_name]=copy_deepcopy(self.column_params)



    def read_datatype_property_range(self,xsd_type=None):
        """
        Extrait la bonne valeur paramètre RDFLib à partir d'un type xsd défini dans la colonne
        Prend l'expression dans configurateur, vérifie si elle est connue, la transcrit par dictionnaire
        xsd_type est une expression alternative à celle de la colonne
        """
        if xsd_type is None:
            try:
                xsd_type=self.column_params[COLUMN_XSD_TYPE_KEY]
            except:
                error_msg = "Missing xsd type \"{}\" for {}.{}."
                logger.error(error_msg.format(COLUMN_XSD_TYPE_KEY,self.table_section.table_name, self.column_name))
                return None

        if xsd_type in XSD_CONF_RDFLIB_CONVERTER.keys():
            return XSD_CONF_RDFLIB_CONVERTER[xsd_type]
        else:
            error_msg = "Unknown xsd type \"{}\" for {}.{}."
            logger.error(error_msg.format(self.column_params[COLUMN_XSD_TYPE_KEY],
                                          self.table_section.table_name, self.column_name))
            self.raise_error("Pick one in {}".format(XSD_CONF_RDFLIB_CONVERTER.keys()))
            return None

    def complete_column_params(self,clean_unknwon_keys=False):
        """
        Définit les valeurs par défaut selon les types de colonnes
        """
        if self.column_type == CT_IGNORE:
            self.skip_column = True
            return
        else:
            self.skip_column = False

        #Récupère les paramètres associés au type de colonne et vérifie leur valeur par défaut
        expected_keys_list=self.modele.column_type_min_keys(column_type=self.column_type)

        if expected_keys_list is None:
            if self.column_type==COLUMN_TYPE_DEFAULT:
                self.raise_error("column \"{}.{}\" type for column is not defined."
                                 .format(self.table_section.table_name,self.column_name))
            else:
                self.raise_error("Unknown column type \"{}\" for column \"{}.{}\"."
                             .format(self.column_type,self.table_section.table_name, self.column_name))
            return

        unexpected_keys_list =self.column_params.keys() - expected_keys_list

        for key in expected_keys_list:
            # Fixe les clés manquantes à leur valeur par défaut
            self.column_params[key]= init_struct(self.modele,self.column_params,key)

        if self.is_primary_key():
            # Contrôle la formulation des labels des entités
            self.target_class_name = self.table_section.target_class_name
            self.check_entity_labels()

        if self.is_object_property() or self.is_datatype_property():
            if self.is_object_property():
                # Le nom de la classe cible est externe à la table
                if not self.check_other_target_class_name():
                    #La classe cible du nom a été trouvée, ok
                    # self.target_class_name = self.column_params[COLUMN_TARGET_CLASS_NAME_KEY]
                # else:
                    #Pas de classe cible por le nom donné
                    if self.target_class_name is not None and class_name_factory(self.target_class_name)!='':
                        if self.target_class_name.count(':')==0:
                            logger.info("No table found for class {}, create a dedicated Additional Class."
                                        .format(self.target_class_name))
                            self.table_section.configuration.set_additional_class_params(class_name=self.target_class_name)
                    else:
                        self.raise_error("Bad target class name \"{}\" for column \"{}.{}\"."
                             .format(self.target_class_name,self.table_section.table_name, self.column_name))

                if self.is_object_property_key():
                    # Contrôle la formulation des labels des entités s'il s'agit d'une classe additionelle
                    if self.check_other_additional_class_name():
                        #Il s'agit d'une classe additionelle, retire la clé des clés inutiles
                        if KB_ENTITIES_LABELS_STRUCT_KEY in unexpected_keys_list:
                            unexpected_keys_list.remove(KB_ENTITIES_LABELS_STRUCT_KEY)
                        self.column_params[KB_ENTITIES_LABELS_STRUCT_KEY]= init_struct(self.modele,self.column_params,KB_ENTITIES_LABELS_STRUCT_KEY)
                        self.check_entity_labels()

            if self.is_datatype_property():
                # Pour une DTP, la classe cible est celle de la table en cours
                self.target_class_name = self.table_section.target_class_name

                # Vérifie que le type xsd est connu
                self.read_datatype_property_range()
                # self.check_xsd_type()

                if self.is_datatype_property_key():
                    # La valeur de la DTP est stockée dans une autre table, vérifie que la table existe
                    if not self.check_other_target_table_name():
                        self.raise_error("Missing values table named \"{}\" for datatype property key column \"{}.{}\""
                                    .format(self.target_class_name,self.table_section.table_name,self.column_name))

            # Contrôle la syntaxe du target class name (pour le range)
            if self.target_class_name is None or class_name_factory(self.target_class_name) == '':
                self.raise_error("Bad class name \"{}\" for column \"{}.{}\"."
                                 .format(self.target_class_name,self.table_section.table_name, self.column_name))

            # Définit l'intitulé du prédicat
            if self.column_params[COLUMN_PREDICATE_NAME_KEY] == '':
                self.construct_predicate_name()
            else:
                self.predicate_name = self.column_params[COLUMN_PREDICATE_NAME_KEY]

            # Contrôle l'intitulé du prédicat
            if self.predicate_name is None or regex_predicate_and_class_names(self.predicate_name) == '':
                self.raise_error("Bad predicate name \"{}\" for column \"{}.{}\"."
                                 .format(self.predicate_name, self.table_section.table_name, self.column_name))

            # Administre un dictionnaire visant à détecter les doublons de prédicats
            if self.predicate_name in self.configuration.predicates_dict.keys():
                self.raise_error("Duplicate predicate name \"{}\" in table \"{}\" already existing in table \"{}\""
                                 .format(self.predicate_name,self.table_section.table_name,
                                         self.configuration.predicates_dict[self.predicate_name]))
            else:
                self.configuration.predicates_dict[self.predicate_name]=self.table_section.table_name

            if not isinstance(self.column_params[COLUMN_FUNCTIONAL_PROPERTY_KEY], bool):
                self.column_params[COLUMN_FUNCTIONAL_PROPERTY_KEY]=True

            if self.column_params[COLUMN_LABELS_KEY]==dict():
                self.column_params[COLUMN_LABELS_KEY]=default_labels(target_name=self.predicate_name)

            if self.build_inverseOf_property():
                self.column_params.setdefault(COLUMN_INVERSE_OF_LABELS_KEY, dict())
                if self.column_params[COLUMN_INVERSE_OF_LABELS_KEY] == dict():
                    inversOf_predicate = INVERT_OF_PREDICATE_PREFIX + self.predicate_name
                    self.column_params[COLUMN_INVERSE_OF_LABELS_KEY] = default_labels(target_name=inversOf_predicate)

        unexpected_keys_list = unexpected_keys_list - COLUMN_DATA_KEYS_SET
        if unexpected_keys_list.__len__()>0:
            logger.debug("Useless keys \"{}\" in column \"{}.{}\"."
                         .format(unexpected_keys_list,self.table_section.table_name, self.column_name))
            if clean_unknwon_keys:
                for key in unexpected_keys_list:
                    del self.column_params[key]
                logger.info("Useless keys deleted")
            else:
                logger.debug("Use \"--clean_keys\" option to delete useless keys.")

        return

    def construct_predicate_name(self,avoid_duplicate=True):
        # Désaccentue column_name
        name = ''.join(c for c in unicodedata_normalize('NFD', self.column_name) if unicodedata_category(c) != 'Mn')
        for key, value in CHARACTERS_SUBSTITION_LIST.items():
            name = name.replace(key, value)
        name = regex_predicate_and_class_names(name)
        words_list = [word for word in name.split() if word not in WORDS_TO_REMOVE]
        #Pour les prédicats, retire la majuscule sur le premier mot
        predicate_name = ''.join([words_list[0].lower()] + [word.capitalize() for word in words_list[1:]])
        if avoid_duplicate:
            duplicate_index=1
            while predicate_name in self.configuration.predicates_dict.keys():
                duplicate_index+=1
                predicate_name=predicate_name+str(duplicate_index)
        self.predicate_name = predicate_name_factory(predicate_name)
        self.column_params[COLUMN_PREDICATE_NAME_KEY] = self.predicate_name

    def __extract_sample_data(self,values_set: set()):
        """
        Extrait une donnée représentative (non vide, non nulle)
        """
        sample_data_set = values_set.copy()
        sample_data = None
        while len(sample_data_set) > 0:
            sample_data = sample_data_set.pop()
            if (sample_data != "") and (sample_data != 0):
                break
        return sample_data

    def uuid_construct(self,df_line: pandas.Series, line_index: int):
        """
        Les uuid sont construits par concaténation du nom de la classe et de l'ID donné par la table source
        """

        value = df_line[self.column_name]

        if (value is None) or pandas.isna(value) or (value in self.table_section.specific_skipped_values_set):
            logger.warning("Null primary key value \"{}\" in table {} at line {} (begin at 0) for object property entity in column {}." \
                .format(value, self.table_section.table_name, line_index,self.column_name))
            return None

        if self.column_type == XSD_CONF_INT_TYPE:
            # Les entiers sont parfois lus de la forme "4.0" au lieu de "4", retirer la section décimales
            uuid = uuid_generator(self.target_class_name, int(value))
        else:
            uuid = uuid_generator(self.target_class_name, value)

        # logger.debug("Build uuid column \"{}.{}\" from class {} and id {} uuid={}"
        #              .format(self.table_section.table_name,self.column_name,self.target_class_name, value,uuid))
        return uuid

    def check_other_target_class_name(self):
        """
        Vérifie que la target class name de la colonne en cours contient le nom d'une classe déclarée
        """
        self.target_class_name = init_struct(self.modele,self.column_params, COLUMN_TARGET_CLASS_NAME_KEY)

        if self.target_class_name == COLUMN_TARGET_CLASS_NAME_DEFAULT or self.target_class_name == '':
            self.target_class_name = None
            self.raise_error("Target class name for column \"{}.{}\" is not defined"
                             .format(self.table_section.table_name,self.column_name))
            return False
        else:
            self.target_class_name = class_name_factory(self.target_class_name)
            if self.target_class_name == '':
                self.target_class_name = None
                self.raise_error("Target class name for column \"{}.{}\" contains only forbidden chars for class name"
                                 .format(self.table_section.table_name, self.column_name))
                return False
            return self.configuration.check_declared_class_name(class_name=self.target_class_name)

    def check_other_target_table_name(self):
        """
        Recherche une table dont la classe racine est la target classe name de la colonne en cours
        """
        self.target_class_name = init_struct(self.modele,self.column_params, COLUMN_TARGET_CLASS_NAME_KEY)
        if self.target_class_name == COLUMN_TARGET_CLASS_NAME_DEFAULT or self.target_class_name == '':
            self.target_class_name = None
            self.raise_error("Target table name for column \"{}.{}\" is not defined"
                             .format(self.table_section.table_name,self.column_name))
            return False
        else:
            self.target_class_name = class_name_factory(self.target_class_name)
            if self.target_class_name == '':
                self.target_class_name = None
                self.raise_error("Target class name for column \"{}.{}\" contains only forbidden chars for class name"
                                 .format(self.table_section.table_name, self.column_name))
            #Vérifie si le nom de la table existe dans la configuration, pas dans les objets (synchro)
            return self.table_section.configuration.is_table_target_class_name(class_name=self.target_class_name)


    def check_other_additional_class_name(self):
        """
        Recherche la target classe name de la colonne en cours dans les classes additionelles
        """
        return self.target_class_name in self.configuration.additional_classes_params.keys()

    def __has_conversion_pipe(self):
        return (self.column_params[COLUMN_CONVERSIONS_PIPE].__len__()>0)


    def read_value(self,df_line:pandas.Series,apply_value_factory=True):
        """
        Interprète une donnée du dump pour la projeter dans le graph:
        * Ignore les valeurs comme identifiées à ignorer (specific_skipped_values et None n/a nan etc.)
        * Applique le pipe de conversion de la colonne si existant
        """
        #ETAPE 1 Extrait une valeur
        value = df_line[self.column_name]
        #ETAPE 2 Valeur connue comme étant à ignorer ?
        if (value in self.table_section.specific_skipped_values_set) or pandas.isna(value):
            return None
        else:
            if apply_value_factory:
            # Non, applique le pipe de conversion de la colonne en cours s'il en existe un
                return value_factory(value=value,xsd_type=self.column_params[COLUMN_XSD_TYPE_KEY],
                                 conversions_pipe=self.column_params[COLUMN_CONVERSIONS_PIPE])
            else:
                return value

    def __read_date(self, string_to_test: str, cast_to_short_date=False):
        """
        Evalue la possibilité de faire d'une chaîne, une date.
        Retourne une date ou None
        """
        return read_date(string_to_test, cast_to_short_date=cast_to_short_date)

