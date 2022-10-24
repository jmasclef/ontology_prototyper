
TYPE_JSON_EDITOR_CONVERTER={ int:'integer', bool:'boolean', str:'string'}


class JSONEditorItemParams():
    def __int__(self, key_name,type, default_value):
        self.name = key_name
        self.description = 'Label for {}'.format(key_name)
        self.type = ''  # 'string' 'integer' 'object' 'array'
        self.format = None  # 'date' 'color' 'table' 'checkbox'
        self.enum = None  # ['male', 'female','other']
        self.default= default_value
        self.minLength= None #String min length
        self.minimum = None #minimum for integer
        self.maximum = None #maximum for integer
        self.infoText = None #i avec on hoover text


class JSONEditorObjectParams():
    type = 'object'
    def __int__(self, title,type, default_value):
        self.title = title
        self.required=[]
        self.properties=dict()


class JSONEditorArrayParams():
    type = 'array'
    def __int__(self, title:str, uniqueItems:bool):
        self.title = title
        self.format='table' #quelles autres options ?
        self.uniqueItems=uniqueItems
        self.items=dict() #Contient un object ou un item qui définit l'élement à répéter en tableau
        self.properties=dict()
