import logging
import re
import pandas
import os
import json
import sys

from uuid import uuid5, NAMESPACE_DNS
from dateutil.parser import parse as date_parse
from collections import Counter
from unicodedata import normalize as unicodedata_normalize
from copy import deepcopy as copy_deepcopy
from . perfect_poc_consts import *

logger=logging.getLogger('LOG')
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
# logger.setLevel("INFO")


def Most_Common(lst:list):
    try:
        data = Counter(lst)
        return data.most_common(1)[0][0]
    except:
        return None

def first_char_upper(string:str):
    """
    Premiere lettre en majuscule, different de .capitalize() qui rabaisse les formes MusicType en Musictype
    """
    if len(string)>1:
        return string[0].upper()+string[1:]
    else:
        return string.upper()

def raise_error(error_msg:str,running_mode:int):
    logger.error(error_msg)
    if running_mode==RUNNING_MODE_DEBUG:
        # Donne l'erreur python détaillée puis quitte
        raise NameError(error_msg)
    elif running_mode==RUNNING_MODE_NORMAL:
        # Quitte en se limitant aux messages du logging
        sys.exit()
    else:
        # Continue l'exécution
        return

def uuid_generator(id_str1,id_str2):
    return uuid5(NAMESPACE_DNS,str(id_str1)+str(id_str2))

def default_labels(target_name:str):
    return {'en': DEFAULT_ENGLISH_LABEL + target_name, 'fr': DEFAULT_FRENCH_LABEL + target_name}

def regex_predicate_and_class_names(name):
    #Désaccentue
    name = unicodedata_normalize('NFKC', str(name))
    #Ne conserve que l'alphanumérique
    name=name.replace(' ','_')
    name = re.sub("[^A-Za-z0-9_:]", "", name)
    return name

def class_name_factory(name):
    if ':' not in name:
        name=first_char_upper(name)
    name=regex_predicate_and_class_names(name)
    return name

def predicate_name_factory(name):
    name=name.replace(':','_')
    name=regex_predicate_and_class_names(name)
    name= PREDICATE_PREFIX+name[0].lower()+name[1:]
    return name

def read_date(string_to_test: str, cast_to_short_date=False):
    """
    Evalue la possibilité de faire d'une chaîne, une date.
    Retourne une date ou None
    """
    string_length = string_to_test.__str__().__len__()
    if string_length > 30 or string_length < 6:
        return (None, None)
    else:
        if (string_length <= 10) or cast_to_short_date:
            try:
                # Retourne le format accepté par la norme
                value = date_parse(string_to_test, ).date().isoformat()
                range = XSD_CONF_DATE_TYPE
            except:
                return (None, None)
        else:
            try:
                # Retourne le format accepté par la norme
                value = date_parse(string_to_test, ).isoformat()
                range = XSD_CONF_DATETIME_TYPE
            except:
                return (None, None)
        return (value,range)

def correct_uri(uri:str(),ending_char:str()=None):
    """
    Définit le caractère de fin (ending_char) à trouver sur une uri
    ending_char = None ou un caractère de le set chars_to_filter
    Si ending_char == None alors retire le dernier caractère s'il fait partie de le set chars_to_filter
    """
    chars_to_filter={'#','/'}
    if ending_char is None:
        # Retire les caractères à filtrer
        while uri[-1] in chars_to_filter:
            uri=uri[:-1]
    else:
        #Retire tous les derniers caractères pour finalement rajouter le bon
        #Efficace sur les fins bizarres de type #/ ou /#
        while uri[-1] in chars_to_filter:
            uri = uri[:-1]
        #Rajoute le bon
        uri=uri+ending_char
    return uri

def filter_root_filename_string(value):
    """
    Retire les caractères non admis dans le nom racine d'un fichier
    """
    value = unicodedata_normalize('NFKC', str(value))
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def read_source_file(source_file:str,csv_separator:str=None, json_rows_key:str=None,json_table_name_key:str=None):
    """
    Lit un fichier de données et retourne un DataFrame Pandas
    """
    if not os.path.isfile(source_file):
        logger.error("\"{}\" source file does not exist! Source file ignored.".format(source_file))
        dataframes = None
        table_name = None
    else:
        _, file_extension = map(lambda x: x.upper(), os.path.splitext(source_file))
        # Par défaut la table porte le nom de base du fichier source
        table_name = os.path.basename(source_file)[:-len(file_extension)]
        # tables_dict.setdefault(source_file, dict())
        # init_data_options_params(source_file=source_file)

        if file_extension in CSV_EXTENSIONS_LIST:
            try:
                dataframes = pandas.read_csv(source_file, sep=csv_separator,
                                             encoding=DEFAULT_ENCODING, chunksize=PANDAS_CHUNKSIZE)
            except Exception as error:
                error_msg = 'File \"{}\" was found but the following error occurred while trying to parse data (check separator option).'.format(
                    source_file)
                logger.error(error_msg)
                logger.error(error)
                dataframes = None

        elif file_extension in JSON_EXTENSIONS_LIST:
            # json_rows_key = configuration_dict.setdefault(JSON_ROWS_KEY, JSON_DEFAULT_ROWS_KEY)
            # json_table_name_key = configuration_dict.setdefault(JSON_TABLE_NAME_KEY, JSON_DEFAULT_TABLE_NAME_KEY)
            with open(source_file, "r", encoding=DEFAULT_ENCODING) as jsonfile:
                try:
                    json_buffer = json.load(jsonfile)
                except Exception as error:
                    error_msg = 'File \"{}\" was found but the following error occurred while trying to parse json format (step 1).'.format(
                        source_file)
                    logger.error(error_msg)
                    logger.error(error)
                    dataframes = None
            # ATTRIBUTION DU NOM DE LA TABLE
            if json_table_name_key not in json_buffer:
                logger.warning(
                    "\"{}\" key with name of the table was not found in the json file: filename name will be used as table name.".format(
                        json_table_name_key))
            else:
                table_name = json_buffer[json_table_name_key]

            if (json_rows_key != "") and (json_rows_key not in json_buffer):
                logger.error(
                    "\"{}\" key with data rows was not found in the json file ! Source file ignored.".format(
                        json_rows_key))
                dataframes = None
            else:
                # Les Data sont dans un bloc du json (ex:'rows') => décale le buffer à lire
                if (json_rows_key in json_buffer):
                    # => décale le buffer à lire
                    json_buffer = json_buffer[json_rows_key]
                    try:
                        dataframes = [pandas.read_json(path_or_buf=json.dumps(json_buffer), orient='records')]
                    except Exception as error:
                        error_msg = 'File \"{}\" was found but the following error occurred while trying to parse json data (step 2).'.format(
                            source_file)
                        logger.error(error_msg)
                        logger.error(error)
                        dataframes = None
        else:
            logger.error(
                "\"{}\" is an unknown extension for source file ! Source file ignored.".format(file_extension))
            dataframes = None

    return dataframes, table_name

def value_factory(value,xsd_type,conversions_pipe:list()=None,column_name:str=None):

    # if conversions_pipe is not None:
    #     for conversion in conversions_pipe:
    #         if conversion == CONVERSION_STR_TO_FLOAT:
    #             futur_value = convert_to_float(futur_value)
    #         elif conversion == CONVERSION_STR_TO_INT:
    #             futur_value = convert_to_int(futur_value)
    #         elif conversion == CONVERSION_EXTRACT_INTEGER_FROM_STR:
    #             futur_value = extract_integer_from_str(futur_value)
    #         else:
    #             raise_error("PIPE ERROR - Unknwon \"{}\" operation in pipe, ignored. ".format(conversion))
    #     value = futur_value

    value = apply_conversion_pipe(value, conversions_pipe,column_name)

    value_type=type(value)
    futur_value = value
    if value_type is int and xsd_type is XSD_CONF_FLOAT_TYPE:
        futur_value= float(value)
    elif value_type is float and xsd_type is XSD_CONF_INT_TYPE:
        futur_value= int(value)
    elif xsd_type in {XSD_CONF_DATE_TYPE, XSD_CONF_DATETIME_TYPE} and value_type is str:
        if xsd_type is XSD_CONF_DATE_TYPE:
            (futur_value, _) = read_date(value, cast_to_short_date=True)
        else:
            (futur_value, _) = read_date(value)
    elif (xsd_type == XSD_CONF_FLOAT_TYPE) and (value_type == str):
        try:
            futur_value = float(value)
        except:
            logger.warning("Conversion str to float impossible for {}".format(value))
            futur_value = None
    elif (xsd_type == XSD_CONF_INT_TYPE) and (value_type == str):
        try:
            futur_value = int(float(value))
        except:
            logger.warning("Conversion str to int impossible for {}".format(value))
            futur_value = None
    elif xsd_type is XSD_CONF_BOOLEAN_TYPE and value_type is not bool:
        futur_value = False if str(value).upper() in BOOLEAN_FALSE_LIST else True

    return futur_value

def xsd_type_factory(value,test_date:True,test_float:True,test_int:True):
    value_type=type(value)
    if value_type is int:
        return XSD_CONF_INT_TYPE
    elif value_type is float:
        return XSD_CONF_FLOAT_TYPE
    elif value_type is bool:
        return XSD_CONF_BOOLEAN_TYPE
    elif value_type is not str:
        return None

    if test_date:
        (date_value, xsd_date_type)=read_date(value)
        if xsd_date_type is not None:
            return xsd_date_type
    if test_float:
        try:
            if str(float(value)) == value:
                return XSD_CONF_FLOAT_TYPE
        except:
            pass
    if test_int:
        try:
            if str(int(float(value))) == value:
                return XSD_CONF_INT_TYPE
        except:
            pass

    if value_type is str:
        return XSD_CONF_STRING_TYPE
    else:
        return None


def dict_label(dict_name:dict,parent_key_name:str=None):
    label=''
    for key,value in dict_name.items():
        if type(value)==dict:
            value_str= dict_label(dict_name=value,parent_key_name=key)
            if parent_key_name is not None:
                value_str="{}_{}".format(parent_key_name,value_str)
        elif type(value)==list:
                value_str_items=[]

                for item in value:
                    if type(item)==dict:
                        local_label = dict_label(dict_name=item,parent_key_name=key)
                        local_label = 'Empty' if local_label == '' else local_label
                    else:
                        local_label = 'Empty' if str(item)=='' else "\'{}\'".format(str(item))

                    value_str_items.append('{}_{}'.format(key, local_label))
                if parent_key_name is None:
                    value_str = ", ".join(value_str_items)
                else:
                    value_str=", ".join(['{}_{}'.format(key, item_value) for item_value in value_str_items])

                value_str= "[{}]".format(value_str)
        else:
            local_label = 'Empty' if str(value) == '' else "\'{}\'".format(str(value))
            if parent_key_name is None:
                value_str='{}_{}'.format(key, local_label)
            else:
                value_str="{}_{}_{}".format(parent_key_name,key, local_label)

        label = value_str if label=='' else "{}, {}".format(label,value_str)

    if parent_key_name is None:
        #Post traitement
        if label.count('\', ')==0:
            #Si une seule clé/valeur alors la valeur sert de label
            try:
                #Prend la valeur sans les ''
                new_label= label.split('_\'')[1][:-1]
            except:
                #N'insiste pas
                new_label=label
        else:
            new_label=first_char_upper(label)
            new_label=new_label.replace('_\'',' : ')
            new_label=new_label.replace('\'','')
            new_label=new_label.replace('_',' ')
        return new_label
    else:
        return label

def extract_predicate_from_uri(subject):
    try:
        predicate = subject.split('#')[1]
    except:
        predicate = None
    return predicate

def apply_conversion_pipe(value: str,conversion_pipe:list(),column_name):

    futur_value = value
    for conversion in conversion_pipe:
        if conversion == CONVERSION_STR_TO_FLOAT:
            futur_value=convert_to_float(futur_value,column_name)
        elif conversion == CONVERSION_CAPITALIZE_SENTENCE_STR:
            futur_value=convert_capitalize_sentence_str(futur_value,column_name)
        elif conversion == CONVERSION_CAPITALIZE_WORDS_STR:
            futur_value=convert_capitalize_words_str(futur_value,column_name)
        elif conversion == CONVERSION_LOWER_STR:
            futur_value=convert_lower_str(futur_value,column_name)
        elif conversion == CONVERSION_UPPER_STR:
            futur_value=convert_upper_str(futur_value,column_name)
        elif conversion == CONVERSION_REMOVE_PUNCT_STR:
            futur_value=convert_remove_punctuation_str(futur_value,column_name)
        elif conversion == CONVERSION_REMOVE_UNDERSCORE_STR:
            futur_value=convert_remove_underscore_str(futur_value,column_name)
        elif conversion == CONVERSION_STR_TO_INT:
            futur_value=convert_to_int(futur_value,column_name)
        elif conversion == CONVERSION_EXTRACT_INTEGER_FROM_STR:
            futur_value=extract_integer_from_str(futur_value,column_name)
        else:
            raise_error("PIPE ERROR in column {} - Unknwon \"{}\" operation in pipe, ignored. ".format(column_name,conversion))
    return futur_value

def convert_to_float(value,column_name):
    """
    Convertit une valeur de type numérique ou chaîne de caractères en type float
    Fonction plus robuste qui traite les cas du type "3,230,000.00$" = 3230000.0
    """
    try:
        if isinstance(value, float):
            # Rien à faire
            return value
        elif isinstance(value, int):
            # Simple
            return float(value)
        else:
            # Force le type d'entrée
            futur_value = str(value)

        # Gère les expressions de types 4,570.64€ ou 4570,64€ pour en faire 4570.64
        if (futur_value.count(',') == 1 and futur_value.count('.') == 0):
            # Si la virgule est utilisée au lieu du point, remplacer
            futur_value = futur_value.replace(",", ".")
        # Ne conserver que les chiffres et le point
        futur_value = re.sub("[^0-9\.]", "", futur_value)
        return float(futur_value)
    except:
        raise_error("PIPE ERROR in column \"{}\" - Conversion of \"{}\" to float failure.".format(column_name,value))
        return value

def convert_to_int(value,column_name):
    """
    Convertit une valeur de type numérique ou chaîne de caractères en type integer
    """
    try:
        if isinstance(value, int):
            return value
        else:
            # procéder par int(float(f)) gère les cas "4.0"
            return int(convert_to_float(value))
    except:
        raise_error("PIPE ERROR in column \"{}\" - Conversion of \"{}\" to integer failure."
                         .format(column_name,value))
        return value

def extract_integer_from_str(value,column_name):
    """
    Convertit les expressions du type "4,560,000.00" en "4560000"
    """
    try:
        if isinstance(value, str):
            return str(convert_to_int(value))
        else:
            return str(int(float(value)))
    except:
        raise_error("PIPE ERROR in column \"{}\" - Integer extraction from \"{}\" failure."
                         .format(column_name,value))
        return value

def convert_capitalize_sentence_str(value,column_name):
    """
    Met en majuscule la première lettre de la phrase
    """
    if type(value)==str:
        #La builltin fonction .captalize() met les autres lettres à lower: "CNL" devient "Cnl"
        return first_char_upper(value)
    else:
        raise_error("PIPE ERROR in column \"{}\" - Capitalizing of \"{}\" failure, must be a string."
                         .format(column_name, value))
        return value

def convert_capitalize_words_str(value,column_name):
    """
    Met en majuscule la première lettre de whaque mot
    """
    if type(value)==str:
        #La builltin fonction .captalize() met les autres lettres à lower: "CNL" devient "Cnl"
        return " ".join([first_char_upper(word) for word in value.split()])
    else:
        raise_error("PIPE ERROR in column \"{}\" - Capitalizing of \"{}\" failure, must be a string."
                         .format(column_name, value))
        return value

def convert_lower_str(value,column_name):
    """
    Met en minuscules
    """
    if type(value)==str:
        return value.lower()
    else:
        raise_error("PIPE ERROR in column \"{}\" - Lowering of \"{}\" failure, must be a string."
                         .format(column_name, value))
        return value

def convert_upper_str(value,column_name):
    """
    Met en majuscules
    """
    if type(value)==str:
        return value.upper()
    else:
        raise_error("PIPE ERROR in column \"{}\" - Uppering of \"{}\" failure, must be a string."
                         .format(column_name, value))
        return value

def convert_remove_punctuation_str(value,column_name):
    """
    Remplace les '_' par des ' '
    """
    if type(value)==str:
        value= re.sub(r'[^\w\s]', '', value)
        while value.count('  ')>0:
            value=value.replace('  ',' ')
        return value.strip()
    else:
        raise_error("PIPE ERROR in column \"{}\" - Replacing _ in \"{}\" failure, must be a string."
                    .format(column_name, value))
        return value

def convert_remove_underscore_str(value,column_name):
    """
    Remplace les '_' par des ' '
    """
    if type(value)==str:
        return value.replace('_',' ')
    else:
        raise_error("PIPE ERROR in column \"{}\" - Replacing _ in \"{}\" failure, must be a string."
                    .format(column_name, value))
        return value
