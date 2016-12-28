import struct
import binascii
import codecs

class CBModel:
    DEC = 1000
    l_size = 0
    f_size = 0
    ll_weights = []
    fl_weights = []
    ave_ll_weights = []
    ave_fl_weights = []

    # def __init__(self, l, f):
    #     self.l_size = l
    #     self.f_size = f
    #     self.ll_weights = [0 for i in range(l * l)]
    #     self.fl_weights = [0 for i in range(f * l)]
    #     self.ave_ll_weights = [0.0 for i in range(l * l)]
    #     self.ave_fl_weights = [0.0 for i in range(f * l)]

    def reset_ave_weights(self):
        self.ave_ll_weights = [0.0 for i in range(l * l)]
        self.ave_fl_weights = [0.0 for i in range(f * l)]
    
    def update_ll_weights(self, i, j, delta, steps):
        ind = i * self.l_size + j
        self.ll_weights[ind] += delta
        self.ave_ll_weights[ind] += steps * delta

    def update_fl_weights(self, i, j, delta, steps):
        ind = i * self.l_size + j
        self.fl_weights[ind] += delta
        self.ave_fl_weights[ind] += steps * delta
    
    def average(self, step):
        for i in range(self.l_size * self.f_size):
            self.fl_weights[i] = int((float(self.fl_weights[i]) - self.ave_fl_weights[i] / float(step)) * self.DEC + 0.5)

        for i in range(self.l_size * self.l_size):
            self.ll_weights[i] = int((float(self.ll_weights[i]) - self.ave_ll_weights[i] / float(step)) * self.DEC + 0.5)
    
    def byteToInt(self, s):
        ans = ""+s[6]+s[7]+s[4]+s[5]+s[2]+s[3]+s[0]+s[1]
        ans = int(ans, 16)
        # print ans
        # ans = 0        
        # for i in range(7, -1, -2):
        #     ans = int(ans * 256) + int(s[i-1], 16) * 16 + int(s[i], 16)
        # print ans
        if(s[6] >= '8'):
            return -((1 << 32) - ans)
        return ans
    
    def __init__(self, filename):
        inputfile = open(filename, "rb")
        temp = inputfile.read(4)
        temp = codecs.decode(binascii.hexlify(temp))
        self.l_size = self.byteToInt(temp)
        temp = inputfile.read(4)
        temp = codecs.decode(binascii.hexlify(temp))
        self.f_size = self.byteToInt(temp)
        
        # self.ll_weights = [0 for i in range(self.l_size * self.l_size)]
        temp = inputfile.read(4 * self.l_size * self.l_size)
        # for i in range(len(self.ll_weights)):
        self.ll_weights = struct.unpack("<"+str(self.l_size * self.l_size)+"i", temp)
        self.ll_weights = tuple(self.ll_weights)

        # self.fl_weights = [0 for i in range(self.f_size * self.l_size)]
        temp = inputfile.read(4 * self.f_size * self.l_size)

        # for i in range(len(self.fl_weights)):
        self.fl_weights = struct.unpack("<"+str(self.f_size * self.l_size)+"i", temp)
        self.fl_weights = tuple(self.fl_weights)
        # print len(self.fl_weights)

        inputfile.close()

if __name__ == '__main__':
    mod = CBModel("cws_model.bin")
    print(len(mod.fl_weights))

