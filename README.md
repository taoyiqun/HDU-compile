# HDU-compile
词法分析器和语法分析器
[TOC]

# 编译原理实验报告

<font face="楷体" size=4 ><center>17042127   陶逸群</center></font>

## 说明

这次实验完成了词法分析器，递归下降分析子程序，LL（1）语法分析器，有限自动机的确定化，LL(1)文法判定。同时将词法分析器，递归下降分析子程序，LL（1）语法分析器，LL(1)文法判定进行整合实现了词法分析到语法分析的过程，使用PyQt5写了界面。

程序框图、设计过程、主要数据结构等以及程序源代码均在代码说明部分给出，同时将LL（1）语法分析器，LL(1)文法判定整合在一起为LL(1)语法分析部分说明。

该文档为其他四份文档的总和，只看该文档即可。

## 词法分析程序设计

### 实验描述

设计、编制并调试一个简单语言*CP*(Compiler Principle)的词法分析程序，加深对词法分析原理的理解。

CP语言的词法如下：

- 关键词： begin  end  if   then  else   for  while  do  and  or  not ，注意：所有关键词都是小写的。
- 标识符ID，与标准C语言一致，即：以下划线或字母开头的字母数字下划线组成的符号串。
- 无符号整数NUM：数字串
- 运算符和分界符： +、-、*、/、>、\<、=、:=、>=、<=、<>、++、--、(、)、; 、 # 。注意：:=表示赋值运算符、#表示注释开始的部分，;表示语句结束，<>表示不等关系
- 空白符包括空格、制表符和换行符，用于分割ID、NUM、运算符、分界符和关键词，词法分析阶段要忽略空白符。

### 代码说明

#### Symbol模块

##### 介绍

是各个词法的抽象。

- Token父类：所有词法的父类

- Separator类：分隔符类
- UnsignedNumber类：无符号数字类
- Operator类：运算符类
- KeyWord类：关键字类
- ID类：标识符类

##### 代码

```python
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
```

#### LexResult模块

##### 介绍

主要用来储存词法分析结果。

- getsymbol，gettag，getdetail，getnumber函数分别用来获取识别到的字符，字符所对应的标号，字符分类，在识别到的词法中的排位。

- \__str\__函数用来把识别到的单个LexResult转成字符，listtostr函数将词法表转换成字符(使用reduce),这两个函数在后续LL(1)文法识别时使用。

##### 代码

```python
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
```

#### Util模块

##### 介绍

在词法分析器中主要构建了FileReadUtil类和LaxterUtil类。

- FileReadUtil类封装了读取词法配置文件的函数readsymbols和函数getcode。getcode函数主要实现了读取源程序文件后将其去除注释(\#之后到换行部分，‘’’     ‘’‘之间部分）写入到过滤代码文件，并在过滤代码每行前加上行号的功能，返回的是加了行号的过滤代码文件。

- LaxterUtil类实现了对过滤后源码的词法分析。流程如下:

  ```flow
  st=>start: 开始
  e=>end: 返回词法分析结果列表
  op1=>operation: 读取词法文件
  op2=>operation: 读取过滤注释后代码文件
  op3=>operation: 进一步过滤(\t,\v,\r,\n和开头的空格)
  cond=>condition: 分析未结束
  cond1=>condition: 当前字符是否为空格
  op4=>operation: 下一个字符,countion跳过循环
  cond2=>condition: 当前字符是否为字母
  op5=>operation: 一直读到当前字符不是_,数字和字母
  cond3=>condition: 是否关键字
  op6=>operation: 分析关键字
  op7=>operation: 分析标识符
  cond4=>condition: 当前字符是否是数字
  op8=>operation: 一直读到当前字符不是数字
  op9=>operation: 识别到无符号数字
  cond5=>condition: 是否能识别到分隔符或运算符
  op10=>operation: 向前看一位试探识别分隔符和运算符
  op11=>operation: 识别到失败词法
  st->op1->op2->op3->cond
  cond(true)->cond1
  cond1(yes)->op4
  cond1(no)->cond2
  cond2(yes)->op5->cond3
  cond3(yes)->op6
  cond3(no)->op7
  cond2(no)->cond4
  cond4(yes)->op8->op9
  cond4(no)->op10->cond5
  cond5(no)->op11
  cond(false)->e
  
  ```

  其中调用findfirst函数进行运算符和分割符的试探。

##### 代码

```python
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
```

```python
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
```

### 运行结果

![1559667435199](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559667435199.png)

![1559667553503](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559667553503.png)

![1559667649797](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559667649797.png)

## 递归下降分析子程序

### 实验描述

掌握最基本的自顶向下分析方法，即递归下降子程序方法，理解其特点和适用范围（回溯，左递归等现象），锻炼递归调用程序的构造方法。

给定CP语言中简单算术表达式文法G[E]: 

- E→TE’
- E’→ATE’|ε
- T→FT’
- T’→MFT’ |ε
- F→(E) | i
- A → + | -
- M → * | /

根据该文法，编写递归下降分析子程序。

### 代码描述

完成该实验在Util模块中添加了ParserUtil类。

#### PerserUtil类

##### 介绍

该类接受词法分析得到的LexResult列表。

主要是parser函数调用分析开始函数processE接着根据下一个识别到的词法调用对应的子程序直到分析结束。最后得到的分析结果以字符串列表的形式存在self.res中。self.flag代表是否分析成功。

- processE函数：分析E
- processT函数：分析T
- processF函数：分析F
- processEChild函数：分析E’
- processTChild函数：分析T‘
- processA函数：分析A
- processM函数：分析M

##### 代码

```python
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
```

### 运行结果

正确输入

![1559669104150](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559669104150.png)

![1559669781414](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559669781414.png)

![1559669815450](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559669815450.png)

错误输入:

![1559669169725](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559669169725.png)

![1559669247805](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1559669247805.png)

## LL(1)语法分析

### 实验描述

了解 LL(1)语法分析是如何根据语法规则逐一分析词法分析所得到的单词，检查语法错误，即掌握语法分析过程。

掌握LL(1)语法分析器的设计与调试。

理解LL(1)文法的判定方法，进一步掌握文法的改造原理（左递归消去、左公共因子提取），FIRST集、FOLLOW集的构造方法，预测分析表的的构造算法。

针对任意的文法，编写相应的左递归消除、左公共因子提取程序，求解相应的FIRST、FOLLOW集，构造预测分析表，并结合专题3的LL(1)语法分析程序，并给出测试句子的分析过程。

判断LL(1)文法部分：

1. 输入：文法
2. 处理：左递归消除、左公共因子提取，FIRST、FOLLOW等集合构造，判断LL(1)
3. 输出：是LL(1)的情况输出预测分析表，否则判断不是LL(1)
4. 编写LL(1)语法分析程序，并给出测试句子的分析过程。

### 代码描述

完成该实验在Util模块中添加了LLOneAnalyzer类。

#### LLOneAnalyzer类

首先说明在该类中产生式以以下结构储存：

```python
<class 'dict'>: {'E': ['TBB', 'TBM', 'FU', 'FA'], 'B': ['ATB', 'ε'], 'T': ['FU'], 'U': ['MFU', 'ε'], 'F': ['(E)', 'i'], 'A': ['+', '-'], 'M': ['*', '/']}
```

**first**集、**follow**集以下结构储存:

```python
<class 'dict'>: {'E': {'i', '('}, 'B': {'-', 'ε', '+'}, 'T': {'i', '('}, 'U': {'ε', '*', '/'}, 'F': {'i', '('}, 'A': {'-', '+'}, 'M': {'*', '/'}, 'J': {'ε', '/', '-', '*', '+'}, 'j': {'-', 'ε', '+', '*', '/'}, 'I': {'-', 'ε', '*', '+', '/'}}
```

**select**集以一下结构储存:

```python
<class 'dict'>: {'E': {'TJ': {'(', 'i'}, 'Fj': {'(', 'i'}}, 'B': {'ATB': {'+', '-'}, 'ε': {'+', '-', ')', '/', '#', '*'}}, 'T': {'FU': {'(', 'i'}}, 'U': {'MFU': {'/', '*'}, 'ε': {'+', '-', ')', '/', '#', '*'}}}
```

简单的说就是两重dict，后面的一个set为对应产生式的select集。

**LL（1）分析表**以一下结构储存:

```python
<class 'dict'>: {'B': {'(': [set(), []], ')': [{'B-->ε'}, []], '+': [{'B-->ATB'}, ['B', 'T', 'A']], '-': [{'B-->ATB'}, ['B', 'T', 'A']], '*': [set(), []], '/': [set(), []], 'i': [set(), []], '#': [{'B-->ε'}, []]}}

```

dict套一个dict再套一个list，首先查找非终结符，然后查找当前字符得到的list中，第一项是当前的分析规则，第二项为分析规则右部转置，方便后续分析时压栈。

类中所有数据开列如下：

- ***self.symbols***：字母池，在消除文法左递归和提取左公共因子时用以产生新的产生式
- ***self.start***：开始符号
- ***self.overs***：终结符号
- ***self.production***：产生式(经过提取左公共因子和消除左递归可能被修改)
- ***self,nontermainals***：非终结符(经过提取左公共因子和消除左递归可能被修改)
- ***self.first***：first集
- ***self.follow***：follow集
- ***self.select***：select集
- ***self.analyse_table***：分析表

##### 介绍

初始化该类，首先会调用***left_factor***函数来提取左公共因子。就是扫描产生式字典将形如**A → δβ1 | δβ2 | δβ3 | …… |δβn | δ**的产生式转化成**A → δA'           A' → β1 | β2 | β3 | …… | βn | ε**

。直到产生式不再变化。

接着会调用***eliminate_res***函数消除左递归，就如同书上所给的算法一样，首先按照以下步骤消除间接左递归。

```java
for i ＝ 1 to n do
　　　　{for j ＝ 1 to i - l do
　　　　　{ 用产生式Ａi→a1b｜a2b｜……｜akb代替每个开如Ai→Ajb的产生式，其中，Aj→a1｜a2｜……｜ak是所有的当前Aj产生式；}
　　　　消除关于Ai产生式中的直接左递归性}
　　　}

```

而消除直接左递归方法如下:

```java
　1、把所有产生式写成候选式形式。如A→Aa1｜Aa2……｜Aan｜b1｜b2……｜bm。其中每个a都不等于ε，而第个b都不以A开头。
　2、变换候选式成如下形式：
　　A→b1A’｜b2A’……｜bmA’
　　A’ →a1A’｜a2A’……｜anA’｜ε

```

接着开始求优化过的产生式的***first***集。这个过程由***get_first***和***find_first***实现。***find_first***函数根据传入的非终结符，遍历当前产生式，返回改非终结符的first集。而***get_first***调用***find_first***函数，不断查找first集，直到first集不再变化。

然后求***follow***集合

1. 对S，将 # 加入 FOLLOW(S)，然后再按后面的处理
2. 若B → αAβ是G的产生式，则将FIRST(β) - ε 加入FOLLOW(A)
3. 若B → αA是G的产生式，或B → αAβ是G的产生式（β 多次推导后得到ε ），则将FOLLOW(B) 加入到FOLLOW(A) 
4. 反复使用2-3，直到FOLLOW集合不再变化为止

接下来，根据求得的***follow***和***first***集合求***select***集，用***get_select***和***find_longfirst***实现，***find_longfirst***用来求后续产生式的***first***集合，***get_select***调用***find_longfirst***根据不同情况来合并follow集和first集。

之后调用***panbie***判断是否是LL文法，修改**self.flag**,主要是求得的select集之间没有交集。

若该文法为LL文法则调用***get_analyse_table***来获得分析表。类初始化完毕。

后续对句子分析调用***analyse***函数，提供lexresults参数为词法分析得到的列表。该函数返回tupe，第一项为分析是否成功，第二项为分析栈的情况列表，第三项为当前输入字符串情况，第四项为执行的操作。

##### 代码

```python
class LLOneAnalyzer:
    start = 'E'
    overs = ['(', ')', '+', '-', '*', '/', 'i',
             #   'a','b','c'   #测试左递归
             ]
    productions = {
        #  'E': ['TBB', 'TBM','FU','FA'],      #测试左公共因子
        #'R':['Sa','a'],'Q': ['Rb', 'b'],'S': ['Qc', 'c'],    #测试左递归
        'E': ['TB', ],
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

```

### 运行结果

- 左递归和左公共因子消除![1560671878804](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1560671878804.png)

- 分析表

  ![1560671670536](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1560671670536.png)

- 分析过程![1560671590380](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1560671590380.png)

## 有限自动机的确定和最小化

### 实验描述

​	1. 理解有限自动机的作用，进一步理解有限自动机理论

​	2. 设计有限自动机的表示方式，采用合理的数据结构表示自动机的五个组成部分

​	3.掌握ε闭包的求法和子集构造算法，以程序实现NFA到DFA的转换，并且最小化DFA，提高算法的理解和实现能力

利用状态表和有限自动机的运行原理编写和设计程序，判断输入的自动机是DFA还是NFA，如果是NFA，利用子集法将其确定化，然后利用求同法或求异法将所得的DFA最小化。

### 代码说明

该实验为代码中的**DFA**模块，未与前述实验整合。采用集合储存状态和符号，状态对应符号的转换关系用二维dict储存，例如*table\['1'][\'b']=set('2','3')*表示1状态输入符号b到达2和3状态。

运行该模块，首先调用***panbieDFA***判断是否为最小化的自动机。该函数主要是：

```python
if len(table[state]['ε'])!=0:
    return False

```

判断是否存在空转换。

```python
if len(table[state][symbol])>1:
    return False

```

判断是否存在相同输入多个转换的情况。

如果不是最小化自动机，则首先进行NFA到DFA的转换。这里实现***trans***函数为ε闭包。***move***为状态集转换。模仿书上做法，在主函数中调用这两个函数进行NFA到DFA的转换。

```python
for i in r:
    for symbol in dfasymbols:
        res_state=trans(table,move(newtable[i][1],symbol,table))        #转换后闭包
        if res_state not in statelist:
            statelist.append(res_state)
            newtable[i][0].update({symbol:(len(statelist)-1)})    #原状态转换
            if len(end)+len(res_state)>len(res_state.union(end)):   #和终结状态有交集则为终结状态
                myset[1].add(len(statelist)-1)
            else:
                myset[0].add(len(statelist)-1)
            newtable.append([{mm:-1 for mm in dfasymbols} ,res_state])    #新的状态
            r.append(len(statelist)-1)    #状态变多了
        else:
            newtable[i][0].update({symbol:statelist.index(res_state)})    #原状态转换

```

而对DFA的最小化，则采用求同法，不断试探加入状态集，得到最终的最小化DFA。

```python
for symbol in dfasymbols:#每一个输入
    mynewset=deepcopy(myset)
    for aset in mynewset:  # 原划分中每一个集合
        transset = [set()]
        newdivide = [set(), ]
        newset = []
        for aitem in aset:  # 每个状态

            flag = False
            for i in range(len(transset)):
                k = deepcopy(transset[i])
                k.add(newtable[aitem][0][symbol])  # 每个状态对应输入的转换加入到transset中
                if panduan(k, myset):  # 加入后的集合是划分中某一集合的子集，可加入
                    transset[i].add(newtable[aitem][0][symbol])  # 加入
                    newdivide[i].add(aitem)  # 对应的状态在一个集合中
                    flag = True
                    break
            if not flag:
                transset.append({newtable[aitem][0][symbol], })
                newdivide.append({aitem, })
        newset = newset + newdivide  # 第一个符号第一个集合再次划分完毕
        myset.remove(aset)
        myset =  myset+deepcopy(newset)

```

完整代码，如下。

```python
from copy import deepcopy


def panbieDFA(table,states,symbols):
    for state in states:
        if len(table[state]['ε'])!=0:
            return False
    for state in states:
        for symbol in symbols:
            if len(table[state][symbol])>1:
                return False
    return True

def trans(table,states):
    stack=list(states)
    res=set()
    while(len(stack)!=0):
        item=stack.pop()
        for nextstate in table[item]['ε']:
            if nextstate  not  in res:
                res.add(nextstate)
                stack.append(nextstate)
        res.add(item)
    return res

def move(states,symbol,table):
    res=set()
    for state in states:
        resres=trans(table,table[state][symbol])
        res=res.union(resres)
    return res



def panduan(transset,myset):
    for aset in myset:
        if transset.issubset(aset):
            return True
    return False








#symbols = set(input('请输入转换字符表，不要输入ε 以空格分隔'))
#states =set(input('请输入状态 以空格分隔'))
symbols=set('a''b')
states=set('X''1''2''3''4''5''6''Y')
start=set('X')
end=set('Y')
symbols.add('ε')
#symbols.add(' ')
#states.add(' ')
#symbols.remove(' ')
#states.remove(' ')
table ={state: {symbol:set() for symbol in symbols}for state in states}
'''
for state in states:
    for symbol in symbols:
        nextstates=set(input('请输入状态%s经过%s可到达状态集以空格分隔'%(state,symbol)))
        nextstates.add(' ')
        nextstates.remove(' ')
        table[state][symbol]=nextstates
'''

table['X']['ε']=set('1')
table['1']['a']=set('1')
table['1']['b']=set('1')
table['1']['ε']=set('2')
table['2']['a']=set('3')
table['2']['b']=set('4')
table['3']['a']=set('5')
table['4']['b']=set('5')
table['5']['ε']=set('6')
table['6']['a']=set('6')
table['6']['b']=set('6')
table['6']['ε']=set('Y')





dfasymbols=deepcopy(symbols)
dfasymbols.remove('ε')


flag=panbieDFA(table,states,symbols)
if flag==True:
    print('已是最小化DFA')
else:
    statelist=[]
    newtable=[]
    newstate=trans(table,start)#闭包
    statelist.append(newstate)
    newtable.append([{symbol: -1 for symbol in dfasymbols},newstate])
    r=[0]
    myset=[{0},set()]        #中介状态非终结状态
    for i in r:
        for symbol in dfasymbols:
            res_state=trans(table,move(newtable[i][1],symbol,table))        #转换后闭包
            if res_state not in statelist:
                statelist.append(res_state)
                newtable[i][0].update({symbol:(len(statelist)-1)})    #原状态转换
                if len(end)+len(res_state)>len(res_state.union(end)):   #和终结状态有交集则为终结状态
                    myset[1].add(len(statelist)-1)
                else:
                    myset[0].add(len(statelist)-1)
                newtable.append([{mm:-1 for mm in dfasymbols} ,res_state])    #新的状态
                r.append(len(statelist)-1)    #状态变多了
            else:
                newtable[i][0].update({symbol:statelist.index(res_state)})    #原状态转换
    for symbol in dfasymbols:#每一个输入
        mynewset=deepcopy(myset)
        for aset in mynewset:  # 原划分中每一个集合
            transset = [set()]
            newdivide = [set(), ]
            newset = []
            for aitem in aset:  # 每个状态

                flag = False
                for i in range(len(transset)):
                    k = deepcopy(transset[i])
                    k.add(newtable[aitem][0][symbol])  # 每个状态对应输入的转换加入到transset中
                    if panduan(k, myset):  # 加入后的集合是划分中某一集合的子集，可加入
                        transset[i].add(newtable[aitem][0][symbol])  # 加入
                        newdivide[i].add(aitem)  # 对应的状态在一个集合中
                        flag = True
                        break
                if not flag:
                    transset.append({newtable[aitem][0][symbol], })
                    newdivide.append({aitem, })
            newset = newset + newdivide  # 第一个符号第一个集合再次划分完毕
            myset.remove(aset)
            myset =  myset+deepcopy(newset)
   #格式化输出
    newdict=[-1]*len(statelist)
    for i in range(len(myset)):
        for aitem in myset[i]:
            newdict[aitem]=i

    mindfa=[]
    for i in range(len(myset)):
        mindfa.append([{symbol: -1 for symbol in dfasymbols}, ])
        for symbol in dfasymbols:
            a=deepcopy(myset[i]).pop()
            mindfa[i][0].update({symbol:newdict[newtable[a][0][symbol]]})
    for symbol in dfasymbols:
        print('        %s'%symbol,end='')
    print('\n',end='')

    for i in range(len(mindfa)):
        print('状态%s'%i,end='')
        for symbol in dfasymbols:
            print('     %s'%mindfa[i][0][symbol],end='')
        print('\n',end='')
    print('sucess')

```

### 实验结果

![1560674007834](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1560674007834.png)

## 界面整合

这里编写***UI***模块，采用PyQτ5进行界面描绘。

![1560675162292](C:\Users\hdutyq\AppData\Roaming\Typora\typora-user-images\1560675162292.png)

在源码部分，输入要分析的代码，程序会将此代码储存到yuan.txt文件中，源码上面展示去除注释后代码样子，处理后的代码储存在code.txt文件中。源码右边是Qtable，主要展示语法分析过程和LL文法的分析表。

## 总结

通过这学期的实验，我掌握了编译过程中从词法分析到语法分析的过程，同时在实验中学习了Python语言的使用，训练了自己的算法实现能力。

由于是初学Python在代码编写上有许多不规范的地方，比如函数，变量的命名等部分。

在我看来，我的实验优点有

- 采用模块化编写
- 整合了从词法分析到语法分析的过程
- 界面
- 词法分析过程中的关键字采用文件形式储存方便修改

不足和值得改进的地方：

- 语法分析中的产生式没有采取文件读入的方式后续测试需要修改代码文件
- 代码的命名不是很规范
