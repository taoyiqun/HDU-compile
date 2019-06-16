from copy import deepcopy
from functools import reduce

import Symbol
import sys
import LexResult as lexR
class   FileReadUtil():
    @staticmethod
    def readsymbols(filename):
        symbols=[]
        with open(filename,'r') as f:
            for line in f.readlines():
                symbols.append(line.replace('\n',''))
        return symbols
    @staticmethod
    def getcode(filename):
        codeline = 1
        codeview = ''
        codefilename = 'code.txt'
        filename = 'yuan.txt'
        with open(filename, 'r')  as f:
            codes = f.read()
            i = 0
            while i < len(codes):
                if  codes[i] == '#':
                    while i<len(codes) and codes[i] != '\n':
                        codes = codes[:i] + codes[i + 1:]
                    i=i+1
                elif i + 2 <= len(codes) - 1 and (codes[i:i + 3] == "'''" or codes[i:i + 3] == '"""'):
                    codes = codes[:i] + codes[i + 3:]
                    while True:
                        if i + 2 <= len(codes) - 1 and (codes[i:i + 3] == "'''" or codes[i:i + 3] == '"""'):
                            codes = codes[:i] + codes[i + 3:]
                            break
                        elif i + 2 > len(codes) - 1:
                            print("注释错误，未匹配'''")
                            sys.exit()
                        else:
                            codes = codes[:i] + codes[i + 1:]

                else:
                    i = i + 1
        with    open(codefilename, 'w') as f:
            f.write(codes)

        with open(codefilename, 'r') as f:
            for line in f.readlines():
                codeview = codeview + str(codeline) + '|' + line
                codeline = codeline + 1
        return codeview


class   LexerUtil:
    @staticmethod
    def lexer():
        keywords = Symbol.KeyWord('keywords.txt')
        operators = Symbol.Operator('operators.txt')
        separators = Symbol.Separator('separators.txt')
        unsignednumber = Symbol.UnsignedNumber
        id = Symbol.ID
        with open('code.txt', 'r') as f:
            code = f.read()
        lexresults=[]
        i=0
        symbol=''
        code = code.replace('\t', '')
        code = code.replace('\v', '')
        code = code.replace('\r', '')
        code = code.replace('\n', '')
        code.lstrip()
        codelen=len(code)
        while(i<codelen):
            if code[i]==' ':
                i=i+1
                continue
            elif code[i].isalpha():
                symbol = code[i]
                i = i + 1
                while i<codelen and (code[i].isalpha() or code[i].isdigit() or code[i]=='_'):
                    symbol = symbol + code[i]
                    i = i + 1
                if symbol in keywords.getkeywords():
                    lexresults.append(lexR.LexResult( symbol, keywords.Tag, keywords.getdetail(),len(lexresults)+1))
                    continue
                else:
                    lexresults.append(lexR.LexResult( symbol, id.Tag, id.getdatail(),len(lexresults)+1))
                    continue
            elif code[i].isdigit():
                symbol = code[i]
                i = i + 1
                while i < codelen and code[i].isdigit():
                    symbol = symbol + code[i]
                    i = i + 1
                lexresults.append(lexR.LexResult( symbol, unsignednumber.Tag, unsignednumber.getdetail(),len(lexresults)+1))
            elif LexerUtil.findfirst(code[i],separators.getseparator()+operators.getoperators()):
                symbol = code[i]
                i=i+1
                if i<codelen:
                    if str(symbol+code[i]) in separators.getseparator():
                        lexresults.append(lexR.LexResult( symbol+code[i], separators.Tag, separators.getdetail(),len(lexresults)+1))
                        i=i+1
                    elif str(symbol+code[i]) in operators.getoperators():
                        lexresults.append(lexR.LexResult( symbol+code[i], operators.Tag, operators.getdetail(),len(lexresults)+1))
                        i=i+1
                    elif str(symbol) in separators.getseparator():
                        lexresults.append(lexR.LexResult( symbol, separators.Tag, separators.getdetail(),len(lexresults)+1))
                    else:
                        lexresults.append(lexR.LexResult( symbol , operators.Tag, operators.getdetail(),len(lexresults)+1))
                elif str(symbol) in separators.getseparator():
                        lexresults.append(lexR.LexResult(symbol, separators.Tag, separators.getdetail(),len(lexresults)+1))
                elif str(symbol) in operators.getoperators():
                    lexresults.append(lexR.LexResult( symbol, operators.Tag, operators.getdetail(),len(lexresults)+1))
                else:continue
            else:
               lexresults.append(lexR.LexResult(code[i],0,'失败字符',len(lexresults)+1))
               i=i+1
        return lexresults

    @staticmethod
    def findfirst(u,l):
        for z in range(0,len(l)):
            l[z]=l[z][0]
        if  u in l:
            return True
        else:
            return False

class ParserUtil :

    def __init__(self,lexresult):
        self.lexresult=lexresult
        self.len=len(lexresult)
        self.current=-1
        self.res=[]
        self.flag=True

    def parser(self):
        self.processE()
        if self.current<self.len:
            self.flag=False



    def processE(self):
        self.res.append('E-->TE\'')
        self.processT()
        self.processEChild()

    def processT(self):
        self.res.append('T-->FT\'')
        self.processF()
        self.processTChild()

    def processF(self):
        self.current=self.current+1
        if self.current>=self.len:
            self.res.append('F 产生式不完全')
            self.flag=False
            return
        mystr = self.lexresult[self.current]
        if mystr.getsymbol()=='(':
            self.res.append('F-->(E)')
            self.processE()
            self.current = self.current + 1
            if self.current >= self.len:
                self.res.pop()
                self.res.append('F-->( 产生式不完全')
                self.flag=False
                return
            mystr = self.lexresult[self.current]
            if mystr.getsymbol()==')':
                return
            else:
                self.res.pop()
                self.res.append('F-->(E)中\')\'识别错误 识别到第%s个符号%s'% (mystr.getnumber(),mystr.getsymbol()))
                self.flag=False
                return

        elif mystr.gettag()==2:
            self.res.append('F--> %s' % mystr.getsymbol())
            return
        else:
            self.res.append('F-->id中\'id\'识别错误 识别到第%s个符号%s' % (mystr.getnumber(), mystr.getsymbol()))
            self.flag = False
            return

    def processEChild(self):
        self.current = self.current + 1
        if self.current >= self.len:
            self.res.append('E\'-->ε')
            return
        mystr=self.lexresult[self.current]
        if mystr.getsymbol()=='+' or mystr.getsymbol()=='-':
            self.current = self.current - 1
            self.res.append('E\'-->ATE\'')
            self.processA()
            self.processT()
            self.processEChild()
        else:
            self.current=self.current-1
            self.res.append('E\'-->ε')


    def processTChild(self):
        self.current = self.current + 1
        if self.current >= self.len:
            self.res.append('T\'-->ε')
            return
        mystr = self.lexresult[self.current]
        if mystr.getsymbol() == '*' or mystr.getsymbol() == '/':
            self.current = self.current - 1
            self.res.append('T\'-->MFT\'')
            self.processM()
            self.processF()
            self.processTChild()
        else:
            self.current = self.current - 1
            self.res.append('T\'-->ε')



    def processA(self):
        self.current = self.current + 1
        if self.current >= self.len:
            self.res.append('A--> 产生式不完全')
            self.flag = False
            return
        mystr = self.lexresult[self.current]
        if mystr.getsymbol()=='+' or mystr.getsymbol()=='-':
            self.res.append('A--> %s' % mystr.getsymbol())
            return
        else:
            self.res.append('A-->+|-中\'+|-\'识别错误 识别到第%s个符号%s' % (mystr.getnumber(), mystr.getsymbol()))
            self.flag = False
            return

    def processM(self):
        self.current = self.current + 1
        if self.current >= self.len:
            self.res.append('M--> 产生式不完全')
            self.flag=False
            return
        mystr = self.lexresult[self.current]
        if mystr.getsymbol()=='*' or mystr.getsymbol()=='/':
            self.res.append('M-->%s' % mystr.getsymbol())
            return
        else:
            self.res.append('M-->*|/中\'*|/\'识别错误 识别到第%s个符号%s' % (mystr.getnumber(), mystr.getsymbol()))
            self.flag = False
            return


class LLOneAnalyzer:
    start = 'E'
    overs = ['(', ')', '+', '-', '*', '/', 'i',
               'a','b','c'   #测试左递归
             ]
    productions = {
          'E': ['TBB', 'TBM','FU','FA'],      #测试左公共因子
        'R':['Sa','a'],'Q': ['Rb', 'b'],'S': ['Qc', 'c'],    #测试左递归
        #'E': ['TB', ],
        'B': ['ATB', 'ε'],
        'T': ['FU', ],
        'U': ['MFU', 'ε'],
        'F': ['(E)', 'i'],
        'A': ['+', '-'],
        'M': ['*', '/'],

    }

    def __init__(self, start, overs, productions):
      #  self.used = [
            #  'S','Q','c','R','b','a'
       #     'E', 'T', 'B', 'A', 'ε', 'F', 'U', 'M', '(', ')', 'i', '+', '-''*', '/']
        self.flag=True
        self.symbols = ['C', 'D', 'd', 'e', 'f', 'G', 'g', 'H', 'h', 'I', 'j', 'J']
        self.start = start
        self.overs = overs
        self.productions = deepcopy(productions)
        self.left_factor()
        self.eliminate_res()
        self.nontermainals = self.productions.keys()
        self.first = {nontermainal: set() for nontermainal in self.nontermainals}
        self.follow = {nontermainal: set() for nontermainal in self.nontermainals}
        #产生式到终结符
        self.select={nontermainal: {aitem:set() for aitem in self.productions[nontermainal]} for nontermainal in self.nontermainals }
        self.get_first()
        self.get_follow()
        self.get_select()
        self.panbie()
        linovers=deepcopy(self.overs)
        linovers.append('#')
        #符号确定产生式
        self.analyse_table = {nontermainal: {over : [set(),[]] for over in linovers} for nontermainal in self.nontermainals}
        self.get_analyse_table()
    def left_factor(self):
        while True:
            new = deepcopy(self.productions)
            for nonterminal in list(self.productions.keys()):
                onepool = {}
                for right in self.productions[nonterminal]:
                    if right[0] not in onepool.keys():
                        onepool.update({right[0]: [right[1:]]})
                    else:
                        onepool[right[0]].append(right[1:])
                for (key, values) in onepool.items():
                    if len(values) > 1:

                        symbol = self.symbols.pop()
                        self.productions[nonterminal].append(key + symbol)
                        self.productions.update({symbol: []})
                        for value in values:
                            self.productions[nonterminal].remove(key + value)
                            if value !='':
                                self.productions[symbol].append(value)
                            else:
                                self.productions[symbol].append('ε')
            if new==self.productions:
                break
    def eliminate_res(self):
        for i in range(len(self.productions.keys())):
            non_res = []
            res = []
            kong=[]
            #第一个没有间接左递归
            for j in range(i):
                nonterminal1 = list(self.productions.keys())[i]
                right1 = self.productions[nonterminal1]
                nonterminal2 = list(self.productions.keys())[j]
                right2 = self.productions[nonterminal2]
                productions_res_new = []
                for k in range(len(right1)):
                    if right1[k][0] == nonterminal2 and right1[k][0] != 'ε':
                        for aright in right2:
                            if aright == 'ε':
                                if right1[k]==nonterminal2:
                                    productions_res_new.append('ε')
                                else:
                                    productions_res_new.append(right1[k][1:])
                            else:
                                productions_res_new.append(aright + right1[k][1:])
                    else:
                        productions_res_new.append(right1[k])
                self.productions[nonterminal1] = deepcopy(productions_res_new)
            nonterminal1 = list(self.productions.keys())[i]
            for straigtright in self.productions[nonterminal1]:
                if straigtright[0] == nonterminal1:
                    res.append(straigtright[1:])
                elif straigtright[0] == 'ε':
                    kong.append('ε')
                else:
                    non_res.append(straigtright)
            if len(res) == 0:
                pass
            else:
                symbol = self.symbols.pop()
                self.productions[nonterminal1].clear()
                self.productions.update({symbol: []})
                for one in non_res:
                    self.productions[nonterminal1].append(one + symbol)
                if 'ε' in kong:
                    self.productions[nonterminal1].append('ε')
                for one in res:
                    if one != 'ε':
                        self.productions[symbol].append(one + symbol)
                self.productions[symbol].append('ε')

    def get_first(self):
        for nontermainal in self.nontermainals:
            for right in self.productions[nontermainal]:
                if  right[0] in self.overs:
                    self.first[nontermainal].add(right[0])
        while True:
            old= deepcopy(self.first)
            for nontermainal in self.nontermainals:
                self.first[nontermainal]=self.first[nontermainal].union(self.find_first(nontermainal))
            if old == self.first:
                break

    def find_first(self,nontermainal):
        findedfirst = set()
        for right in self.productions[nontermainal]:
            if right == 'ε':
                findedfirst.add('ε')
            elif right[0] in self.overs:
                continue    #查找下一个产生式
            else:
                for sign in right:
                    if sign in self.nontermainals:
                        findedfirst=findedfirst.union(self.first[sign])
                        if('ε' not in self.first[sign]):
                            break
        return findedfirst
    def find_longfirst(self,str):
        findedlongfirst=set()
        for terminal in str:
            if terminal in self.overs:
                findedlongfirst.add(terminal)
                #终结符中不含ε
                return (findedlongfirst,True)
            else:
                findedlongfirst=findedlongfirst.union(self.first[terminal])
                if 'ε' not in self.first[terminal]:
                     return (findedlongfirst-set('ε'),True)
            return (findedlongfirst-set('ε'),False)
    def get_follow(self):
        self.follow[self.start].add('#')
        while True:
            old=deepcopy(self.follow)
            for nontermainal in self.nontermainals:
                for right in self.productions[nontermainal]:
                    for i, sign in enumerate(right):
                        if sign in self.overs or sign =='ε':    #注意ε影响
                            continue
                        if i == len(right) - 1:
                            self.follow[sign]=self.follow[sign].union(self.follow[nontermainal])
                        else:
                            res=self.find_longfirst(right[i+1:])
                            myset=res[0]
                            myflag=res[1]
                            if myflag==False:
                                myset=myset.union(self.follow[nontermainal])
                            self.follow[sign]=self.follow[sign].union(myset)
            if old==self.follow:
                break

    def get_select(self):
        for nontermainal in self.nontermainals:
            for right in self.productions[nontermainal]:
                if right =='ε':
                    self.select[nontermainal][right]=self.follow[nontermainal]
                else:
                    res = self.find_longfirst(right)
                    myset = res[0]
                    myflag = res[1]
                    if myflag == False:
                        self.select[nontermainal][right] = myset.union(self.follow[nontermainal])
                    else:
                        self.select[nontermainal][right] = myset
    def panbie(self):
        for nonterminal in self.nontermainals:
            mykeys=list(self.select[nonterminal].keys())
            for i in range(len(mykeys)):
                for j in range(len(mykeys)):
                    if len(self.select[nonterminal][mykeys[i]].union(self.select[nonterminal][mykeys[j]])) == len(self.select[nonterminal][mykeys[i]])+len(self.select[nonterminal][mykeys[j]]):
                        pass
                    elif i!=j:
                        self.flag=False
    def get_analyse_table(self):
        for nonterminal in self.select:
            for right in self.select[nonterminal]:
                for terminal in self.select[nonterminal][right]:
                    self.analyse_table[nonterminal][terminal][0].add(str(nonterminal+'-->'+right))
                    self.analyse_table[nonterminal][terminal][1]= list(right)
                    self.analyse_table[nonterminal][terminal][1].reverse()   #后续压栈要转置
                    if 'ε' in self.analyse_table[nonterminal][terminal][1]:
                        self.analyse_table[nonterminal][terminal][1].remove('ε') #注意ε要把它拿掉，不然后续会压入
    def analyse(self,lexresults):
        number=len(lexresults)
        lexresults.append(lexR.LexResult('#',999,'终止符',number))
        res_stack=[]
        res_string=[]
        res_action=[]
        self.stack=['#',self.start]
        flag =True
        while True:
            if len(lexresults)==1:
                res_string.append(lexresults[0].getsymbol())
            else:
                res_string.append(reduce(lexR.LexResult.listtostr, lexresults))
            res_stack.append(deepcopy(self.stack))
            x =self.stack.pop()
            y =lexresults[0]
            if x in self.overs:  #id 特殊处理
                if x == 'i':
                    if y.gettag()==2:
                        res_action.append('%s匹配'%y.getsymbol())
                        lexresults=lexresults[1:]
                    else:
                        res_action.append('%s匹配错误'%y.getsymbol())
                        flag=False
                        break
                else:
                    if x == y.getsymbol():
                        res_action.append('%s匹配' % y.getsymbol())
                        lexresults = lexresults[1:]
                    else:
                        res_action.append('%s匹配错误' % y.getsymbol())
                        flag=False
                        break
            elif x =='#':
                if x == y.getsymbol():
                    res_action.append('结束')
                    flag=True
                    break
                else:
                    res_action.append('产生式结束还有输入符')
                    flag=False
                    break
            elif x in self.nontermainals:
                if y.gettag()==2:
                    res_action.append(self.analyse_table[x]['i'][0])
                    self.stack = self.stack + self.analyse_table[x]['i'][1]
                else:
                    res_action.append(self.analyse_table[x][y.getsymbol()][0])
                    self.stack=self.stack+self.analyse_table[x][y.getsymbol()][1]
            else:
                flag=False


        return (flag,res_stack,res_string,res_action)
if __name__=='__main__':
    s=FileReadUtil.getcode('yuan.txt')
    l=LexerUtil.lexer()
    for i in l:
        print(i.getsymbol(),i.gettag(),i.getdetail()+'\n')
    k=ParserUtil(l)
    k.parser()
    for u in k.res:
        print(u+'\n')
    ll_analyzer = LLOneAnalyzer(start=LLOneAnalyzer.start, overs=LLOneAnalyzer.overs, productions=LLOneAnalyzer.productions)
    if ll_analyzer.flag==False:
        print('文法不是LL1')
    else:
        ll_analyzer.get_analyse_table()
        z=ll_analyzer.analyse(l)
        for i in range(len(z[1])):
            print('%s           %s              %s'%(z[1][i],z[2][i],z[3][i]))

