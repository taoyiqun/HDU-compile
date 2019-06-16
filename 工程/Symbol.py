import Util as ut
from abc import ABCMeta, abstractmethod


class Token(object, metaclass=ABCMeta):
    def __init__(self, filename=None):
        if filename is None:
            self.__tokens = []
        else:
            try:
                self.__tokens = ut.FileReadUtil.readsymbols(filename)
            except FileNotFoundError as e:
                print(filename + "not be found")
            except IOError as e:
                print(filename + "IO error")

    def _gettokens(self):
        return self.__tokens

    @staticmethod
    @abstractmethod
    def getdetail():
        pass


class Separator(Token):
    Tag = 5

    def __init__(self, filename):
        super(Separator, self).__init__( filename)

    @staticmethod
    def getdetail():
        return "分隔符"

    def getseparator(self):
        return super(Separator,self)._gettokens()


class UnsignedNumber(Token):
    Tag = 3

    def __init__(self):
        super(UnsignedNumber, self).__init__(self)

    @staticmethod
    def getdetail():
        return "无符号数字"


class Operator(Token):
    Tag = 4

    def __init__(self, filename):
        super(Operator, self).__init__(filename)

    @staticmethod
    def getdetail():
        return "运算符"

    def getoperators(self):
        return  super(Operator,self)._gettokens()


class KeyWord(Token):
    Tag = 1

    def __init__(self, filename):
        super(KeyWord, self).__init__( filename)

    def getkeywords(self):
        return   super(KeyWord,self)._gettokens()


    @staticmethod
    def getdetail():
        return "关键字"


class ID(Token):
    Tag = 2

    def __init__(self):
        super(ID, self).__init__(self)

    @staticmethod
    def getdatail():
        return "标识符"
