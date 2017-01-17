import sys
def decode(string, coding = 'utf-8'):
    if(sys.version_info[0] == 2):
        return string.decode('utf-8')
    return string

def encode(string, coding = 'utf-8'):
    if(sys.version_info[0] == 2):
        return string.encode(coding)
    return string

def cInput():
    if(sys.version_info[0] == 2):
        return raw_input().strip()
    else:
        return input().strip()