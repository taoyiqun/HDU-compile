class   LexResult:
    def __init__(self,symbol=None,tag=None,detail=None,number=None):
        self.__symbol=symbol
        self.__tag=tag
        self.__detail=detail
        self.__number=number

    def getsymbol(self):
        return self.__symbol
    def gettag(self):
        return self.__tag
    def getdetail(self):
        return self.__detail
    def getnumber(self):
        return self.__number
    def __str__(self):
        return self.getsymbol()
    @staticmethod
    def listtostr(mystr,lex):
        return str(mystr)+str(lex)