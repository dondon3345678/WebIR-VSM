# coding=utf-8
""" split mixed string into chinese and english """
def splitchen(mixstr):
    splitlist = []
    ch = ""
    en = ""
    ch_status = False

    for c in mixstr:
        if not ch_status and isch(c):
            ch_status = True
            if en != "":
                splitlist.append([1,en])
                en = ""
        elif not isch(c) and ch_status:
            ch_status = False
            if ch != "" :
                splitlist.append([2,ch])
        if ch_status:
            ch += c
        else:
            en += c
            ch = ""
    if en != "":
        splitlist.append([1,en])
    elif ch != "":
        splitlist.append([2,ch])
    
    ret = []
    for elem in splitlist:
        if elem[0] == 2:
            for i in range(len(elem[1])):
                ret.append(elem[1][i])
        else:
            ret.append(elem[1])
    return ret
    
def isch(c):
    x = ord(c)

    if x >= 0x2e80 and x <= 0x33ff:
        return True
    elif x >= 0xff00 and x <= 0xffef:
        return True
    elif x >= 0x4e00 and x <= 0x9fbb:
        return True
    elif x >= 0xf900 and x <= 0xfad9:
        return True
    elif x >= 0x20000 and x <= 0x2a6d6:
        return True
    elif x >= 0x2f800 and x <= 0x2fa1d:
        return True
    else:
        return False
"""
if __name__ == "__main__":
    o = splitChEn()
    str = u'今天天氣很good'
    l = o.splitchen(str)
    for elem in l:
        if elem[0] == 2:
            #chinese
            for i in range(len(elem[1])):
                print type(elem[1][i])
        else:
            print elem[1]
    
"""
