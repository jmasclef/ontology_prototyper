from rdflib import XSD as rdflib_XSD

#Running modes
RUNNING_MODE_DEBUG = 0
RUNNING_MODE_NORMAL = 1
RUNNING_MODE_LOOP = 2

# DEBUG_MODE=False

#XLSX vers CSV => Enregistrer Sous CSV UTF-8 (délimité par des virgules)

DEFAULT_FRENCH_LABEL=""
# DEFAULT_FRENCH_LABEL="Label pour "
DEFAULT_ENGLISH_LABEL=""
# DEFAULT_ENGLISH_LABEL="Label for "
DEFAULT_FRENCH_COMMENT="Commentaire pour "
DEFAULT_ENGLISH_COMMENT="Comment for "
DEFAULT_OUTPUT_FILE_EXT=".ttl"

# GLOBAL LEVEL PARAMETERS
SOURCE_FILES_KEY = "sources_files"
TABLES_LIST_KEY = "tables"
ADDITIONAL_CLASSES_KEY= "additional_classes"
ADDITIONAL_CLASS_LABELS_KEY = "ac_labels"
ADDITIONAL_CLASS_SUBCLASS_OF_KEY = "ac_subclass_of"
ADDITIONAL_CLASS_CONVERSIONS_PIPE= "ac_conversions_pipe"
ADDITIONAL_CLASS_EXTRA_URI_MASK_KEY= "ac_extra_uri_mask"
ADDITIONAL_CLASS_EXTRA_URI_MASK= "{ID}"
ADDITIONAL_CLASS_EXTRA_URI_PREDICATE= "extra_uri"
ADDITIONAL_CLASS_EXTRA_URI_LABELS= {'fr':'URL','en':'URL'}


ADDITIONAL_DTP_KEY= "additional_datatypes_properties"
ADDITIONAL_DTP_LABELS_KEY = "adp_labels"
ADDITIONAL_DTP_SUBPROPERTY_OF_KEY = "adp_subproperty_of"
ADDITIONAL_DTP_XSD_TYPE_KEY = "adp_xsd_type"
ADDITIONAL_DTP_DOMAINS_KEY = "adp_domains"
ADDITIONAL_DTP_CONVERSIONS_PIPE= "adp_conversions_pipe"
ADDITIONAL_DTP_IS_FUNCTIONAL= "adp_is_functional_property"
ADDITIONAL_OP_KEY= "additional_object_properties"
ADDITIONAL_OP_LABELS_KEY = "aop_labels"
ADDITIONAL_OP_SUBPROPERTY_OF_KEY = "aop_subproperty_of"
ADDITIONAL_OP_DOMAINS_KEY = "aop_domains"
ADDITIONAL_OP_RANGES_KEY = "aop_ranges"
ADDITIONAL_OP_IS_FUNCTIONAL_KEY= "aop_is_functional_property"
ADDITIONAL_OP_BUILD_INVERSEOF_KEY = "aop_build_inverseOf_property"
ADDITIONAL_OP_INVERSEOF_LABELS_KEY = "aop_inverseOf_property_labels"


ONTOLOGY_OUTPUT_FILE_KEY= "ontology_output_file"
ONTOLOGY_OUTPUT_FILE_NAME_DEFAULT= ""
ONTOLOGY_OUTPUT_FILE_NAME_KEY="ontology_file_name"
ONTOLOGY_OUTPUT_FILE_FORMAT_DEFAULT="turtle"
ONTOLOGY_OUTPUT_FILE_FORMAT_KEY="ontology_file_format"
ONTOLOGY_PARAMS_KEY = "ontology_params"
ONTOLOGY_NAME_KEY = "ontology_name"
ONTOLOGY_NAME_DEFAULT = "MANDATORY NAME OF YOUR ONTOLOGY"
ONTOLOGY_BASE_NAMESPACE_KEY = "ontology_base_namespace"
ONTOLOGY_BASE_NAMESPACE_DEFAULT = "MANDATORY BASE NAMESPACE OF YOUR ONTOLOGY (ending with #) ex: http://www.perfect-memory.com/ontology/pass-culture/1.1#"
ONTOLOGY_BASE_URI_KEY = "ontology_base_uri"
ONTOLOGY_BASE_URI_DEFAULT = "MANDATORY BASE URI OF YOUR ONTOLOGY (ending with no /#) ex http://www.perfect-memory.com/ontology/pass-culture/1.1"
ONTOLOGY_NAMESPACES_KEY = "ontology_namespaces"
ONTOLOGY_LIBRARIES_KEY = "ontology_import_libraries"
ONTOLOGY_IMPORTS_KEY = "ontology_imports"
ONTOLOGY_COMMENTS_KEY = "ontology_comments"
ONTOLOGY_LABELS_KEY = "ontology_labels"
ONTOLOGY_EQUIVALENT_CLASSES_KEY="ontology_equivalent_classes"

ONTOLOGY_COMMENTS_DEFAULT = {'en' : DEFAULT_ENGLISH_COMMENT + 'your ontology',
                              'fr' : DEFAULT_FRENCH_COMMENT+'votre ontologie'}
ONTOLOGY_LABELS_DEFAULT = {'en': DEFAULT_ENGLISH_LABEL + 'your ontology',
                           'fr':DEFAULT_FRENCH_LABEL+'votre ontologie'}


#KB LEVEL PARAMETERS
KB_PARAMS_KEY = "kb_params"
KB_NAMESPACES_KEY = "kb_namespaces"
KB_BASE_URI_KEY = "kb_base_uri"
KB_BASE_URI_DEFAULT = "MANDATORY BASE URI OF YOUR KB (without /#) ex: http://www.perfect-memory.com/profile/pass-culture/kb"
KB_BASE_NAMESPACE_KEY = "kb_base_namespace"
KB_BASE_NAMESPACE_DEFAULT = "MANDATORY BASE NAMESPACE OF YOUR KB (ending with /) ex: http://www.perfect-memory.com/profile/pass-culture/kb/"
KB_IMPORTS_KEY = "kb_imports"
KB_COMMENTS_KEY = "kb_comments"
KB_LABELS_KEY = "kb_labels"
KB_NAME_KEY = "kb_name"
KB_NAME_DEFAULT = "MANDATORY NAME OF YOUR KB"
KB_OUTPUT_FILE_KEY= "kb_output_file"
KB_OUTPUT_FILE_NAME_DEFAULT= ""
KB_OUTPUT_FILE_NAME_KEY="kb_file_name"
KB_OUTPUT_FILE_FORMAT_DEFAULT="turtle"
KB_OUTPUT_FILE_FORMAT_KEY="kb_file_format"


KB_COMMENTS_DEFAULT = {'en' : DEFAULT_ENGLISH_COMMENT + 'your kb', 'fr' : DEFAULT_FRENCH_COMMENT + 'votre kb'}
KB_LABELS_DEFAULT = {'en': DEFAULT_ENGLISH_LABEL + 'your kb', 'fr': DEFAULT_FRENCH_LABEL + 'votre kb'}

KB_ENTITIES_LABELS_STRUCT_KEY = "column_entities_labels_struct"
KB_ENTITIES_LABELS_SAMPLE = "Label {SAMPLE_COLNAME1} {SAMPLE_COLNAME2}"
KB_ENTITIES_LABELS_NONE_VALUE_STR ="NoneValue"
KB_ENTITIES_LABELS_STRUCT_DEFAULT={'en': KB_ENTITIES_LABELS_SAMPLE, 'fr': KB_ENTITIES_LABELS_SAMPLE}

KB_ONTOLOGY_PREFIX="ontology"
# TABLE LEVEL PARAMETERS
TABLE_NAME_KEY = "table_name"
TABLE_NAME_DEFAULT="TABLE NAME - MANDATORY"
TABLE_SOURCE_FILENAME_KEY="source_filename"
TABLE_TARGET_CLASS_NAME_KEY="table_class_name"
TABLE_TARGET_PREDICATE_NAME_KEY="table_predicate_name"
TABLE_TARGET_CLASS_LABELS_KEY = "table_class_labels"
TABLE_CLASS_SUBCLASS_OF_KEY="table_class_subclass_of"
TABLE_COLUMNS_KEY= "columns"
TABLE_TYPE_KEY = "table_type"
TABLE_TYPE_PARAMS_KEY="table_type_parameters"
TABLE_TARGET_PREDICATE="table_target_predicate"
#DATA OPTIONS PARAMETERS
TABLE_DATA_OPTIONS_KEY= "data_options"
SPECIFIC_SKIPPED_VALUES_KEY = "specific_skipped_values"
STOP_ON_DUPLICATE_PRIMARY_KEY = "stop_on_duplicate_primary_key"
COLUMN_LIMITED_PK_LIST_KEY= "limited_primary_keys_list"
CSV_SEPARATOR_KEY="CSV_SEPARATOR"
CSV_SEPARATOR_DEFAULT = ";"

# TT - TABLES TYPES OPTIONS
TABLE_TYPE_DEFAULT = "TT_CLASS or TT_DATATYPE_VALUES"

TT_DATATYPE_VALUES= "TT_DATATYPE_VALUES"
TT_CLASS = "TT_CLASS"

# COLUMN LEVEL PARAMETERS
COLUMN_TYPE_KEY="column_type"
COLUMN_TYPE_DEFAULT= "CT_IGNORE or CT_PRIMARY_KEY or CT_DATATYPE_PROPERTY_VALUE or CT_DATATYPE_PROPERTY_KEY or CT_OBJECT_PROPERTY_VALUE or CT_OBJECT_PROPERTY_KEY or CT_CLASSES_LIST_KEY or CT_JSON_EXPAND or CT_JSON_STRUCT"
COLUMN_PREDICATE_NAME_KEY="predicate_name"
COLUMN_INVERSE_OF_KEY="build_inverseOf_property"
COLUMN_INVERSE_OF_LABELS_KEY="inverseOf_property_labels"

COLUMN_LABELS_KEY = "column_labels"
COLUMN_TARGET_TABLE_NAME_KEY= "target_table_name"
COLUMN_TARGET_TABLE_NAME_DEFAULT= "MANDATORY TABLE NAME !"
COLUMN_TARGET_CLASS_NAME_KEY="target_class_name"
COLUMN_TARGET_CLASS_NAME_DEFAULT= "MANDATORY CLASS NAME (ADDITIONAL CLASS OR OTHER TABLE CLASS) !"
COLUMN_FUNCTIONAL_PROPERTY_KEY= "is_functional_property"
# COLUMN_PK_DATA_PROPERTY="is_also_data_property"
#CONVERSIONS
COLUMN_CONVERSIONS_PIPE="conversions_pipe"

#PIPE CONVERSION OPTIONS
CONVERSION_STR_TO_FLOAT="STR_TO_FLOAT"
CONVERSION_STR_TO_INT="STR_TO_INTEGER"
CONVERSION_EXTRACT_INTEGER_FROM_STR= "EXTRACT_INTEGERS"
CONVERSION_CAPITALIZE_SENTENCE_STR= "CAPITALIZE_SENTENCE_STR"
CONVERSION_CAPITALIZE_WORDS_STR= "CAPITALIZE_WORDS_STR"
CONVERSION_REMOVE_UNDERSCORE_STR= "REMOVE_UNDERSCORE_STR"
CONVERSION_REMOVE_PUNCT_STR= "REMOVE_PUNCT_STR"
CONVERSION_UPPER_STR= "UPPER_STR"
CONVERSION_LOWER_STR= "LOWER_STR"
COLUMN_ACCEPTED_CONVERSIONS={CONVERSION_STR_TO_FLOAT, CONVERSION_STR_TO_INT}

# CT - COLUMNS TYPES OPTIONS
CT_DATATYPE_PROPERTY_VALUE = "CT_DATATYPE_PROPERTY_VALUE"
CT_DATATYPE_PROPERTY_KEY = "CT_DATATYPE_PROPERTY_KEY"
CT_OBJECT_PROPERTY_VALUE = "CT_OBJECT_PROPERTY_VALUE"
CT_OBJECT_PROPERTY_KEY = "CT_OBJECT_PROPERTY_KEY"
CT_CLASSES_LIST_KEY = "CT_CLASSES_LIST_KEY"
CT_IGNORE = "CT_IGNORE"
CT_PRIMARY_KEY = "CT_PRIMARY_KEY"
CT_JSON_EXPAND = "CT_JSON_EXPAND"
CT_JSON_STRUCT = "CT_JSON_STRUCT"
COLUMNS_TYPES_LIST= {CT_PRIMARY_KEY, CT_DATATYPE_PROPERTY_VALUE, CT_DATATYPE_PROPERTY_KEY, CT_OBJECT_PROPERTY_VALUE,
                     CT_OBJECT_PROPERTY_KEY, CT_IGNORE, CT_JSON_EXPAND, CT_JSON_STRUCT}
SAMPLE_DATA_KEY = "info_sample_data"
# SAMPLE_DATA_TYPE_KEY = "sample_data_dtype"
DATA_DIVERSITY_KEY = "info_data_diversity"
DATA_LIST_KEY = "info_data_values_set"

COLUMN_DATA_KEYS_SET = {SAMPLE_DATA_KEY,DATA_DIVERSITY_KEY,DATA_LIST_KEY}

# SUBCLASS_OF_KEY="subclass_of"
COLUMN_SUBCLASS_OF_KEY= "subclass_of"
COLUMN_SUBPROPERTY_OF_KEY= "subproperty_of"
#CONVERSIONS PARAMETERS
PANDAS_CHUNKSIZE = 2000

INVERT_OF_PREDICATE_PREFIX='inverseOf_'
PREDICATE_PREFIX= 'has_'
CSV_EXTENSIONS_LIST=['.CSV']
YAML_EXTENSIONS_LIST=['.YAML']
JSON_EXTENSIONS_LIST=['.JSON']
JSON_ROWS_KEY= "json_rows_key"
JSON_TABLE_NAME_KEY= "json_table_name_key"
JSON_DEFAULT_ROWS_KEY = "rows"
JSON_DEFAULT_TABLE_NAME_KEY= "table"
DEFAULT_ENCODING= "UTF-8"
COLUMN_XSD_TYPE_KEY = "xsd_type"

#XSD types utilisés dans le fichier de configuration
XSD_CONF_INT_TYPE="xsd:integer"
XSD_CONF_FLOAT_TYPE="xsd:float"
XSD_CONF_BOOLEAN_TYPE="xsd:boolean"
XSD_CONF_DATE_TYPE="xsd:date"
XSD_CONF_DATETIME_TYPE="xsd:dateTime"
XSD_CONF_STRING_TYPE = "xsd:string"
# XSD_ACCEPTED_TYPES_SET={XSD_CONF_INT_TYPE,XSD_CONF_FLOAT_TYPE,XSD_CONF_BOOLEAN_TYPE,
#                         XSD_CONF_DATETIME_TYPE,XSD_CONF_DATE_TYPE,XSD_CONF_STRING_TYPE}

XSD_TYPES_CONVERSION = {
    "int64":XSD_CONF_INT_TYPE,
    "float64":XSD_CONF_FLOAT_TYPE,
    "string":XSD_CONF_STRING_TYPE
}
#XSD types utilisés
XSD_RDFLIB_INTEGER=rdflib_XSD.integer
XSD_RDFLIB_FLOAT=rdflib_XSD.float
XSD_RDFLIB_STRING=rdflib_XSD.string
XSD_RDFLIB_DATETIME=rdflib_XSD.dateTime
XSD_RDFLIB_DATE=rdflib_XSD.date
XSD_RDFLIB_BOOLEAN=rdflib_XSD.boolean
XSD_RDFLIB_ANYURI=rdflib_XSD.anyURI

XSD_CONF_RDFLIB_CONVERTER={ XSD_CONF_INT_TYPE:XSD_RDFLIB_INTEGER, XSD_CONF_FLOAT_TYPE:XSD_RDFLIB_FLOAT,
                           XSD_CONF_BOOLEAN_TYPE:XSD_RDFLIB_BOOLEAN, XSD_CONF_STRING_TYPE:XSD_RDFLIB_STRING,
                            XSD_CONF_DATETIME_TYPE:XSD_RDFLIB_DATETIME, XSD_CONF_DATE_TYPE:XSD_RDFLIB_DATE,
                            }

# XSD_ACCEPTED_TYPES_SET=XSD_CONF_RDFLIB_CONVERTER.keys()
BOOLEAN_SETS_LIST = [
    {0,1},{0,-1},
    {"true","false"},{"True","False"},{"TRUE","FALSE"},
    {"Oui","Non"},{"OUI","NON"},{"Yes","No"},{"YES","NO"}
]
BOOLEAN_FALSE_LIST = {"FALSE","NON","NO","0","FAUX"}
XSD_TYPE_UNKNOWN_LABEL="UNKNWON PANDAS DTYPE"

MISSING_SOURCE_FILES_KEY_ERROR="Missing \"{}\" key with list of sources files.".format(SOURCE_FILES_KEY)
COLUMN_TYPE_CHANGE_INFO="Column type for \"{}.{}\" was changed into {}."
UNKOWN_COLUMN_TYPE_ERROR="Column \"{}.{}\" has an unknown type identifier \"{}\" ! Column is skipped."

SKIPPED_VALUES={'','\\N', '-1.#QNAN', '1.#QNAN', '-NaN', '#NA', 'NA', 'nan', 'N/A', '#N/A N/A', 'n/a', 'NULL', 'null', '-nan', '#N/A', '1.#IND', '<NA>', '-1.#IND', 'NaN'}
CHARACTERS_SUBSTITION_LIST={"&":" and ","%":" percent ","#":" number ","@":" at ","_":" ","/":" "}
WORDS_TO_REMOVE={'la', 'y', 'le', 'se', 'une', 'd', 'sa', 'ton', 'm', 'un', 'ta', 'son', 'en', 'mon', 'leurs', 'dont', 'du', 't', 'les', 'des', 'l', 'ma'}

VISU_JSON_DATA_STRUCT= """const dataset = { \n\tnodes: [\n\t\t#NODES_LIST#],\n\tlinks: [\n\t\t#LINKS_LIST#] };"""
VISU_JSON_DATA_STRUCT_NODES_TAG= "#NODES_LIST#"
VISU_JSON_DATA_STRUCT_LINKS_TAG= "#LINKS_LIST#"
VISU_OBJECTS_GROUP_NAME= "Classes"
VISU_DATATYPES_GROUP_NAME= "Datatype Properties"

