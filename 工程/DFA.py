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











