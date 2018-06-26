ENCODE_TABLE = [0x32, 0x31, 0x30, 0x36, 0x46, 0x34, 0x35, 0x33, 0x45, 0x38, 0x37, 0x39, 0x43, 0x41, 0x42, 0x44,\
                0x49, 0x48, 0x47, 0x4D, 0x56, 0x4B, 0x4C, 0x4A, 0x55, 0x4F, 0x4E, 0x50, 0x53, 0x51, 0x52, 0x54,\
                0x59, 0x58, 0x57, 0x63, 0x6C, 0x61, 0x62, 0x5A, 0x6B, 0x65, 0x64, 0x66, 0x69, 0x67, 0x68, 0x6A,\
                0x6F, 0x6E, 0x6D, 0x73, 0x28, 0x71, 0x72, 0x70, 0x27, 0x75, 0x74, 0x76, 0x79, 0x77, 0x78, 0x7A]


DECODE_TABLE = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, 56, 52, -1, -1, -1, -1, -1, -1, -1,\
                2, 1, 0, 7, 5, 6, 3, 10, 9, 11, -1, -1, -1, -1, -1, -1,\
                -1, 13, 14, 12, 15, 8, 4, 18, 17, 16, 23, 21, 22, 19, 26, 25,\
                27, 29, 30, 28, 31, 24, 20, 34, 33, 32, 39, -1, -1, -1, -1, -1,\
                -1, 37, 38, 35, 42, 41, 43, 45, 46, 44, 47, 40, 36, 50, 49, 48,\
                55, 53, 54, 51, 58, 57, 59, 61, 62, 60, 63, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,\
                -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]


def encrypt(ori,key):
    keycb=len(key)
    oricb=len(ori)
    blend_len=2*oricb
    src_len=0
    symbol_add=0
    page=0
    dstlen=0

    if ori is None or oricb<=0 or key is None or keycb<=8 :
        return -1

    blend=[]

    for i in range(oricb):
        first_ch=(ori[i] & 0xAA)|(key[i % keycb] & 0x55)
        second_ch = (ori[i] & 0x55)|(key[i % keycb] & 0xAA)
        blend.insert(2*i,first_ch)
        blend.insert(2*i+1,second_ch)

    if 0==blend_len%3:
        src_len=blend_len
    else:
        symbol_add=3-(blend_len%3)
        src_len=blend_len+symbol_add

    page=src_len//3

    src_buffer =[]

    src_buffer=blend
    if(src_len-blend_len==1):
        src_buffer.append(0)
    if(src_len-blend_len==2):
        src_buffer.append(0)
        src_buffer.append(0)

    dstlen=page*4
    des_buffer=[]

    if des_buffer is None:
        return -1

    for i in range(page):
        src_tmp=[]
        des_tmp=[]
        src_tmp=src_buffer[i*3:(i+1)*3]

        des_tmp.append(src_tmp[0] >> 2)
        des_tmp.append(((src_tmp[0] & 0x03) << 4) | (src_tmp[1] >> 4))
        des_tmp.append(((src_tmp[1] & 0x0f) << 2) | (src_tmp[2] >> 6))
        des_tmp.append(src_tmp[2] & 0x3f)

        for j in range(4):
            des_tmp[j]=ENCODE_TABLE[des_tmp[j]]

        des_buffer[i*4:(i+1)*4]=des_tmp[0:4]

    for i in range(1,symbol_add+1):
        des_buffer[dstlen-i]=0x7E

    output_buffer=[]

    if output_buffer is None:
        return -1

    output_buffer=des_buffer
    out=output_buffer
    outcb=dstlen

    return out,outcb


def decrypt(crypt,key):
    oricb=len(crypt)
    keycb=len(key)
    page=oricb//4
    dstlen=page*3
    output_cb=0
    t=0
    if crypt is None or oricb==0 or oricb%4!=0 or key is None or keycb<8:
        return -1

    des_buffer=[]

    if des_buffer is None:
        return -1

    for i in range(page):
        src=[]
        src=crypt[i*4:(i+1)*4]

        for j in range(4):
            if (src[j] >= len( DECODE_TABLE)) or src[j] < 0:
                return -1

            if src[j]!=0x7E:
                src[j]=DECODE_TABLE[src[j]]
                if(-1==src[j]):
                    return -1


        des=[]
        des.append((src[0] << 2) | ((src[1] & 0x30) >> 4))
        des.append((src[1] & 0x0f) << 4)
        if 0x7E != src[2]:
            des[1] |= (src[2] & 0x3C) >> 2
            if src[2] << 6>0xff:
                des.append(src[2] << 6)
                while (des[2]>0xff):
                    des[2]=des[2] -0xff-1
            else:
                des.append(src[2] << 6)
        else:
            dstlen=dstlen-1

        if 0x7E != src[3]:
            des[2] |= src[3]
        else:
            dstlen=dstlen-1

        des_buffer[t*3:(t+1)*3]=des
        t=t+1

    if 0!=dstlen%2:
        return -1

    output_cb=dstlen//2
    output_buffer=[]

    for output_count in range(output_cb):
        out_ctr = (des_buffer[output_count * 2] & 0xAA) | (des_buffer[output_count * 2 + 1] & 0x55)
        key_ctr = (des_buffer[output_count * 2] & 0x55) | (des_buffer[output_count * 2 + 1] & 0xAA)
        if key_ctr!=key[output_count % keycb]:
            return -1

        output_buffer.append(out_ctr)

    out = output_buffer
    outcb = output_cb

    return out,outcb