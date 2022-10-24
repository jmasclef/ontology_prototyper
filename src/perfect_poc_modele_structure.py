
from . perfect_poc_utils import *
from . perfect_poc_json_editor import *
from copy import deepcopy as copy_deepcopy




class KeyParameters():
    def __init__(self, key_name, default_value, values_structure):
        self.key_name = key_name
        self.default_value = default_value
        self.values_structure = values_structure
        self.json_editor_item=None
        self.json_editor_array=None
        self.json_editor_object=None
        # if type(default_value) == str:
        #     self.json_editor_item = JSONEditorItemParams(key_name=key_name, type='string', default_value=None)
        #     if default_value.count(' or ')>0:
        #         self.json_editor_item.enum=default_value.split(' or ')
        # elif type(default_value)==list:
        #     self.json_editor_item = JSONEditorItemParams(key_name=key_name, type='array', default_value=None)
        # elif type(default_value)==dict:
        #     self.json_editor_item = JSONEditorArrayParams(key_name=key_name, type='array', default_value=None)




class GroupParameters():
    def __init__(self, group_name, min_set: set(), options: set(), set_strut=True, dict_struct=False):
        self.group_name = group_name
        self.min_set = min_set
        self.options = options
        if dict_struct:
            self.dict_struct = True
            self.set_struct = False
        elif set_strut:
            self.dict_struct = False
            self.set_struct = True


class StructureParameters():
    def __init__(self, MAJOR, MINOR, PATCH,running_mode):
        self.running_mode=running_mode
        # Niveau 0 de la structure
        self.MAIN_STRUCTURE = set()
        self.ADDITIONAL_CLASSES_SUB_STRUCTURE = set()
        self.ADDITIONAL_DTP_SUB_STRUCTURE = set()
        self.ADDITIONAL_OP_SUB_STRUCTURE = set()
        self.LIBRARIES= {'pmcore':'http://www.perfect-memory.com/ontology/pmcore/1.1',
                         'pmmodel':'http://www.perfect-memory.com/ontology/pmmodel/1.1'}
        # Paramètres d'une clé précisant sa valeur à l'init et sa structure enfant si imbriquée
        self.KEY_STRUCTURE_PARAMETERS = dict()
        # Paramètres de groupes de clés précisant les éléments minimums et optionnels
        self.GROUP_STRUCTURE_PARAMETERS = dict()
        #Dictionnaire des colonnes (complété par version)
        self.COLUMNS_PARAMS_KEYS=dict()
        self.TABLE_KEYS=dict()
        self.TABLE_PARAMS_KEYS=dict()
        self.COLUMNS_TYPES_LIST= set()

        if MAJOR == 0 and MINOR == 1:
            self.init_v010()


    def add_key_init_parameters(self, key_name, key_default_value, values_struture=None):
        if key_name in self.KEY_STRUCTURE_PARAMETERS:
            key_parameters = self.KEY_STRUCTURE_PARAMETERS[key_name]
            key_parameters.key_name = key_name
            key_parameters.default_value = key_default_value
            key_parameters.values_structure = values_struture
        else:
            key_params = KeyParameters(key_name=key_name, default_value=key_default_value, values_structure=values_struture)
            self.KEY_STRUCTURE_PARAMETERS[key_name] = key_params

    def add_group_parameters(self, group_name, min_set: set(), options=set(), set_strut=True, dict_struct=False):
        if group_name in self.GROUP_STRUCTURE_PARAMETERS:
            group_parameters = self.GROUP_STRUCTURE_PARAMETERS[group_name]
            group_parameters.group_name = group_name
            group_parameters.min_set = min_set
            group_parameters.options = options
            group_parameters.dict_struct = dict_struct
            group_parameters.set_strut = True if (set_strut and (not dict_struct)) else False
        else:
            group_parameters = GroupParameters(group_name, min_set, options, set_strut, dict_struct)
            self.GROUP_STRUCTURE_PARAMETERS[group_name] = group_parameters

    def column_type_min_keys(self,column_type:str)->list:
        if column_type in self.COLUMNS_PARAMS_KEYS:
            return self.COLUMNS_PARAMS_KEYS[column_type]
        else:
            return None

    def init_v010(self):
        # NESTED STRUCTURES
        self.MAIN_STRUCTURE = {ADDITIONAL_CLASSES_KEY, ADDITIONAL_DTP_KEY, ADDITIONAL_OP_KEY, KB_PARAMS_KEY,
                               ONTOLOGY_PARAMS_KEY, SOURCE_FILES_KEY, TABLES_LIST_KEY}
        self.ADDITIONAL_CLASSES_SUB_STRUCTURE = {ADDITIONAL_CLASS_LABELS_KEY, ADDITIONAL_CLASS_SUBCLASS_OF_KEY,
                                                 ADDITIONAL_CLASS_CONVERSIONS_PIPE}
        self.ADDITIONAL_DTP_SUB_STRUCTURE = {ADDITIONAL_DTP_LABELS_KEY, ADDITIONAL_DTP_SUBPROPERTY_OF_KEY,
                                            ADDITIONAL_DTP_XSD_TYPE_KEY, ADDITIONAL_DTP_DOMAINS_KEY,
                                            ADDITIONAL_DTP_IS_FUNCTIONAL, ADDITIONAL_DTP_CONVERSIONS_PIPE}
        self.ADDITIONAL_OP_SUB_STRUCTURE = {ADDITIONAL_OP_LABELS_KEY, ADDITIONAL_OP_SUBPROPERTY_OF_KEY,
                                            ADDITIONAL_OP_RANGES_KEY, ADDITIONAL_OP_DOMAINS_KEY,
                                            ADDITIONAL_OP_IS_FUNCTIONAL_KEY}
        # self.add_group_parameters(ADDITIONAL_CLASSES_KEY, min_set=ADDITIONAL_CLASSES_SUB_STRUCTURE)

        ONTOLOGY_PARAMS_STRUCTURE = {ONTOLOGY_NAME_KEY, ONTOLOGY_OUTPUT_FILE_KEY, ONTOLOGY_NAMESPACES_KEY,
                                     ONTOLOGY_BASE_NAMESPACE_KEY, ONTOLOGY_BASE_URI_KEY, ONTOLOGY_COMMENTS_KEY,
                                     ONTOLOGY_LABELS_KEY, ONTOLOGY_EQUIVALENT_CLASSES_KEY, ONTOLOGY_IMPORTS_KEY,
                                     ONTOLOGY_LIBRARIES_KEY}
        self.add_group_parameters(ONTOLOGY_PARAMS_KEY, min_set=ONTOLOGY_PARAMS_STRUCTURE)

        ONTOLOGY_OUTPUT_FILE_STRUCTURE = {ONTOLOGY_OUTPUT_FILE_NAME_KEY, ONTOLOGY_OUTPUT_FILE_FORMAT_KEY}
        self.add_group_parameters(ONTOLOGY_OUTPUT_FILE_KEY, min_set=ONTOLOGY_OUTPUT_FILE_STRUCTURE)

        KB_PARAMS_STRUCTURE = {KB_BASE_NAMESPACE_KEY, KB_NAMESPACES_KEY, KB_BASE_URI_KEY, KB_COMMENTS_KEY,
                               KB_IMPORTS_KEY, KB_LABELS_KEY, KB_OUTPUT_FILE_KEY,KB_NAME_KEY}
        self.add_group_parameters(KB_PARAMS_KEY, min_set=KB_PARAMS_STRUCTURE)

        KB_OUTPUT_FILE_STRUCTURE = {KB_OUTPUT_FILE_NAME_KEY, KB_OUTPUT_FILE_FORMAT_KEY}
        self.add_group_parameters(KB_OUTPUT_FILE_KEY, min_set=KB_OUTPUT_FILE_STRUCTURE)

        self.add_group_parameters(SOURCE_FILES_KEY, min_set=list())
        # self.add_group_parameters(TABLES_LIST_KEY, min_set=dict())
        # self.add_group_parameters(ADDITIONAL_CLASSES_KEY, min_set=dict())

        #Structure de clés d'une table
        TABLES_LIST_VALUES_STRUCTURE = {TABLE_NAME_KEY, TABLE_COLUMNS_KEY, TABLE_DATA_OPTIONS_KEY, TABLE_TYPE_KEY, TABLE_TYPE_PARAMS_KEY }
        self.TABLE_KEYS=TABLES_LIST_VALUES_STRUCTURE

        # self.add_group_parameters(TABLES_LIST_KEY, min_set=TABLES_LIST_SUB_STRUCTURE, dict_struct=True)

        TABLE_CLASS_SUB_STRUCTURE={TABLE_TARGET_CLASS_LABELS_KEY,TABLE_TARGET_CLASS_NAME_KEY,TABLE_CLASS_SUBCLASS_OF_KEY}
        TABLE_DT_VALUES_SUB_STRUCTURE={TABLE_TARGET_PREDICATE}

        TABLES_DATA_OPTIONS_STRUCTURE = {SPECIFIC_SKIPPED_VALUES_KEY, STOP_ON_DUPLICATE_PRIMARY_KEY,
                                         COLUMN_LIMITED_PK_LIST_KEY, CSV_SEPARATOR_KEY}
        self.add_group_parameters(TABLE_DATA_OPTIONS_KEY, min_set=TABLES_DATA_OPTIONS_STRUCTURE)

        COLUMNS_LIST_VALUES_STRUCTURE = {COLUMN_TYPE_KEY, COLUMN_CONVERSIONS_PIPE}

        self.add_key_init_parameters(SOURCE_FILES_KEY, list())
        self.add_key_init_parameters(ADDITIONAL_CLASSES_KEY, dict(),values_struture=self.ADDITIONAL_CLASSES_SUB_STRUCTURE)
        self.add_key_init_parameters(ADDITIONAL_DTP_KEY, dict(),values_struture=self.ADDITIONAL_DTP_SUB_STRUCTURE)
        self.add_key_init_parameters(ADDITIONAL_OP_KEY, dict(),values_struture=self.ADDITIONAL_OP_SUB_STRUCTURE)
        self.add_key_init_parameters(KB_PARAMS_KEY, dict())
        self.add_key_init_parameters(ONTOLOGY_PARAMS_KEY, dict())
        self.add_key_init_parameters(TABLES_LIST_KEY, dict(),values_struture=TABLES_LIST_VALUES_STRUCTURE)

        # self.add_key_init_parameters(ADDITIONAL_CLASSES_SUB_STRUCTURE, dict())

        self.add_key_init_parameters(ADDITIONAL_CLASS_LABELS_KEY, dict())
        self.add_key_init_parameters(ADDITIONAL_CLASS_CONVERSIONS_PIPE, list())
        self.add_key_init_parameters(ADDITIONAL_CLASS_SUBCLASS_OF_KEY, list())
        self.add_key_init_parameters(ADDITIONAL_DTP_LABELS_KEY, dict())
        self.add_key_init_parameters(ADDITIONAL_DTP_SUBPROPERTY_OF_KEY, list())
        self.add_key_init_parameters(ADDITIONAL_DTP_XSD_TYPE_KEY, list()) #Approche statistique du typage de données
        # self.add_key_init_parameters(ADDITIONAL_DTP_XSD_TYPE_KEY, XSD_CONF_STRING_TYPE)
        self.add_key_init_parameters(ADDITIONAL_DTP_DOMAINS_KEY, list())
        self.add_key_init_parameters(ADDITIONAL_DTP_IS_FUNCTIONAL, True)
        self.add_key_init_parameters(ADDITIONAL_DTP_CONVERSIONS_PIPE, list())
        self.add_key_init_parameters(ADDITIONAL_OP_LABELS_KEY, dict())
        self.add_key_init_parameters(ADDITIONAL_OP_SUBPROPERTY_OF_KEY, list())
        self.add_key_init_parameters(ADDITIONAL_OP_RANGES_KEY, list())
        self.add_key_init_parameters(ADDITIONAL_OP_DOMAINS_KEY, list())
        self.add_key_init_parameters(ADDITIONAL_OP_IS_FUNCTIONAL_KEY, True)

        self.add_key_init_parameters(ONTOLOGY_NAME_KEY, ONTOLOGY_NAME_DEFAULT)
        self.add_key_init_parameters(ONTOLOGY_NAMESPACES_KEY, dict())
        self.add_key_init_parameters(ONTOLOGY_BASE_NAMESPACE_KEY, ONTOLOGY_BASE_NAMESPACE_DEFAULT)
        self.add_key_init_parameters(ONTOLOGY_BASE_URI_KEY, ONTOLOGY_BASE_URI_DEFAULT)
        self.add_key_init_parameters(ONTOLOGY_COMMENTS_KEY, ONTOLOGY_COMMENTS_DEFAULT)
        self.add_key_init_parameters(ONTOLOGY_LABELS_KEY, ONTOLOGY_LABELS_DEFAULT)
        self.add_key_init_parameters(ONTOLOGY_EQUIVALENT_CLASSES_KEY, dict())
        self.add_key_init_parameters(ONTOLOGY_IMPORTS_KEY, list())
        self.add_key_init_parameters(ONTOLOGY_LIBRARIES_KEY, True)
        self.add_key_init_parameters(ONTOLOGY_OUTPUT_FILE_KEY, dict() )

        self.add_key_init_parameters(ONTOLOGY_OUTPUT_FILE_NAME_KEY, ONTOLOGY_OUTPUT_FILE_NAME_DEFAULT)
        self.add_key_init_parameters(ONTOLOGY_OUTPUT_FILE_FORMAT_KEY, ONTOLOGY_OUTPUT_FILE_FORMAT_DEFAULT)

        self.add_key_init_parameters(KB_NAME_KEY, KB_NAME_DEFAULT)
        self.add_key_init_parameters(KB_BASE_NAMESPACE_KEY, KB_BASE_NAMESPACE_DEFAULT)
        self.add_key_init_parameters(KB_NAMESPACES_KEY, dict())
        self.add_key_init_parameters(KB_BASE_URI_KEY, KB_BASE_URI_DEFAULT)
        self.add_key_init_parameters(KB_COMMENTS_KEY, KB_COMMENTS_DEFAULT)
        self.add_key_init_parameters(KB_IMPORTS_KEY, list())
        self.add_key_init_parameters(KB_LABELS_KEY, KB_LABELS_DEFAULT)
        self.add_key_init_parameters(KB_OUTPUT_FILE_KEY, dict())

        self.add_key_init_parameters(KB_OUTPUT_FILE_NAME_KEY, KB_OUTPUT_FILE_NAME_DEFAULT)
        self.add_key_init_parameters(KB_OUTPUT_FILE_FORMAT_KEY, KB_OUTPUT_FILE_FORMAT_DEFAULT)

        self.add_key_init_parameters(TABLE_COLUMNS_KEY, dict(),values_struture=COLUMNS_LIST_VALUES_STRUCTURE)

        #Définit les paramètres au niveau tables
        self.add_key_init_parameters(TABLE_DATA_OPTIONS_KEY, dict())
        self.add_key_init_parameters(TABLE_TARGET_CLASS_LABELS_KEY, dict())
        self.add_key_init_parameters(TABLE_TARGET_CLASS_NAME_KEY, str())
        self.add_key_init_parameters(TABLE_NAME_KEY, str())
        self.add_key_init_parameters(TABLE_TYPE_KEY, TABLE_TYPE_DEFAULT)
        self.add_key_init_parameters(TABLE_TYPE_PARAMS_KEY, dict())
        self.add_key_init_parameters(TABLE_CLASS_SUBCLASS_OF_KEY, list())

        #Définit les paramètres de la section data options dans la section table
        self.add_key_init_parameters(SPECIFIC_SKIPPED_VALUES_KEY, list())
        self.add_key_init_parameters(STOP_ON_DUPLICATE_PRIMARY_KEY, True)
        self.add_key_init_parameters(COLUMN_LIMITED_PK_LIST_KEY, list())
        self.add_key_init_parameters(CSV_SEPARATOR_KEY, CSV_SEPARATOR_DEFAULT)

        #Définit les paramètres au niveau colonne
        self.add_key_init_parameters( COLUMN_CONVERSIONS_PIPE, list() )
        self.add_key_init_parameters( KB_ENTITIES_LABELS_STRUCT_KEY, KB_ENTITIES_LABELS_STRUCT_DEFAULT )
        self.add_key_init_parameters( COLUMN_LIMITED_PK_LIST_KEY, None)
        self.add_key_init_parameters( COLUMN_XSD_TYPE_KEY, None )
        self.add_key_init_parameters( COLUMN_PREDICATE_NAME_KEY, str() )
        self.add_key_init_parameters( COLUMN_SUBPROPERTY_OF_KEY, list())
        self.add_key_init_parameters( COLUMN_SUBCLASS_OF_KEY, list())
        self.add_key_init_parameters(COLUMN_TARGET_TABLE_NAME_KEY, str())
        self.add_key_init_parameters( COLUMN_TARGET_CLASS_NAME_KEY, str() )
        self.add_key_init_parameters( COLUMN_LABELS_KEY, dict())
        self.add_key_init_parameters( COLUMN_FUNCTIONAL_PROPERTY_KEY, True)
        self.add_key_init_parameters( COLUMN_TYPE_KEY, COLUMN_TYPE_DEFAULT)
        self.add_key_init_parameters(COLUMN_INVERSE_OF_KEY, False)

        self.COLUMNS_TYPES_LIST= {CT_PRIMARY_KEY, CT_DATATYPE_PROPERTY_VALUE, CT_DATATYPE_PROPERTY_KEY, CT_JSON_STRUCT,
                                  CT_OBJECT_PROPERTY_VALUE, CT_OBJECT_PROPERTY_KEY, CT_IGNORE, CT_JSON_EXPAND,
                                  CT_CLASSES_LIST_KEY}

        self.COLUMNS_PARAMS_KEYS={
            CT_PRIMARY_KEY:{KB_ENTITIES_LABELS_STRUCT_KEY, COLUMN_CONVERSIONS_PIPE, COLUMN_LIMITED_PK_LIST_KEY,
                            COLUMN_TYPE_KEY,COLUMN_XSD_TYPE_KEY},
                             # COLUMN_PREDICATE_NAME_KEY, COLUMN_XSD_TYPE_KEY},
            CT_DATATYPE_PROPERTY_VALUE:{COLUMN_LABELS_KEY, COLUMN_CONVERSIONS_PIPE, COLUMN_PREDICATE_NAME_KEY,
                                        COLUMN_SUBPROPERTY_OF_KEY, COLUMN_XSD_TYPE_KEY,COLUMN_FUNCTIONAL_PROPERTY_KEY,
                                        COLUMN_TYPE_KEY},
            CT_DATATYPE_PROPERTY_KEY:{COLUMN_LABELS_KEY, COLUMN_CONVERSIONS_PIPE, COLUMN_PREDICATE_NAME_KEY,
                                      COLUMN_SUBPROPERTY_OF_KEY, COLUMN_FUNCTIONAL_PROPERTY_KEY,
                                      COLUMN_TARGET_TABLE_NAME_KEY,COLUMN_TYPE_KEY},
            CT_OBJECT_PROPERTY_KEY: {COLUMN_LABELS_KEY, COLUMN_CONVERSIONS_PIPE,COLUMN_SUBPROPERTY_OF_KEY,
                                     COLUMN_PREDICATE_NAME_KEY,COLUMN_TARGET_CLASS_NAME_KEY,
                                     COLUMN_FUNCTIONAL_PROPERTY_KEY, COLUMN_TYPE_KEY,COLUMN_INVERSE_OF_KEY},
            CT_OBJECT_PROPERTY_VALUE:{COLUMN_CONVERSIONS_PIPE,COLUMN_LABELS_KEY,COLUMN_SUBPROPERTY_OF_KEY,
                                    COLUMN_PREDICATE_NAME_KEY,COLUMN_TARGET_CLASS_NAME_KEY,
                                      COLUMN_FUNCTIONAL_PROPERTY_KEY,COLUMN_TYPE_KEY},
            CT_CLASSES_LIST_KEY:{COLUMN_CONVERSIONS_PIPE, COLUMN_TYPE_KEY, COLUMN_SUBCLASS_OF_KEY},
            CT_IGNORE:{COLUMN_TYPE_KEY},
            CT_JSON_EXPAND:{COLUMN_TYPE_KEY},
            CT_JSON_STRUCT:{COLUMN_TYPE_KEY}
        }

        self.TABLE_PARAMS_KEYS={
            TT_DATATYPE_VALUES:{TABLE_TARGET_PREDICATE_NAME_KEY}, #En copie pour le lettrage
            TT_CLASS:{TABLE_TARGET_CLASS_LABELS_KEY,TABLE_TARGET_CLASS_NAME_KEY,TABLE_CLASS_SUBCLASS_OF_KEY}
        }

def init_struct(modele:StructureParameters, conf_dict:dict, key:str):
    # Fonction récursive qui applique un modèle de structure par défaut à une structure réelle
    # Attention: la fonction produit des copies réelles en entrée et en sortie, pour éviter les problèmes
    # associant closures et garbage. Sinon, restitue les valeurs de la structure précédente en récursivité
    my_dict=copy_deepcopy(conf_dict)

    #A partir d'une clé, cherche le modèle
    if (key not in modele.KEY_STRUCTURE_PARAMETERS) and (key not in modele.GROUP_STRUCTURE_PARAMETERS):
        logger.warning("Found unknown key: {}".format(key))
        return None

    if (key in modele.KEY_STRUCTURE_PARAMETERS):
        #Fixe la valeur par défaut si manquante
        default_value=modele.KEY_STRUCTURE_PARAMETERS[key].default_value
        my_dict.setdefault(key, default_value)
        conf_dict.setdefault(key, default_value)

    if key in modele.GROUP_STRUCTURE_PARAMETERS:
        # Cette clé est identifiée dans le modèle comme une sous-structure, un groupe de clés
        for sub_key in modele.GROUP_STRUCTURE_PARAMETERS[key].min_set:
            # Passe en revue chacune des clés attendues pour cette structure,pas les clés réelles
            if sub_key in modele.GROUP_STRUCTURE_PARAMETERS:
                # Cette clé est sensée porter une sous-structure
                my_dict[key][sub_key]=init_struct(modele,my_dict[key], sub_key)
            elif sub_key in modele.KEY_STRUCTURE_PARAMETERS:
                # Cette clé est sensée porter une valeur, fixe la valeur par défaut si la valeur réelle n'existe pas
                my_dict[key].setdefault(sub_key,modele.KEY_STRUCTURE_PARAMETERS[sub_key].default_value)
    elif modele.KEY_STRUCTURE_PARAMETERS[key].values_structure is not None:
        # Cette clé porte un dictionnaire dynamique d'éléments structurés sur les données (ex: tables, colonnes)
        # Elle ne contient pas une valeur ni une structure directe mais une structure répétée sous une série de clés
        # Ex: une clé par table avec une structure table pour chaque valeur
        for value in my_dict[key].values():
            # Entre dans chaque valeur (chaque structure de table ou chaque structure de colonne)
            for sub_key in modele.KEY_STRUCTURE_PARAMETERS[key].values_structure:
                #Passe en revue chaque clé de la sous-structure modèle, pas la réelle
                if sub_key in modele.GROUP_STRUCTURE_PARAMETERS:
                    #C'est sensé être un groupe
                    value[sub_key]= init_struct(modele,value, sub_key)
                elif sub_key in modele.KEY_STRUCTURE_PARAMETERS:
                    #C'est sensé être une valeur, fixe la valeur par défaut si manquante
                    value.setdefault(sub_key,modele.KEY_STRUCTURE_PARAMETERS[sub_key].default_value)

    result=copy_deepcopy(my_dict[key])
    # conf_dict=copy_deepcopy(my_dict)
    return result

