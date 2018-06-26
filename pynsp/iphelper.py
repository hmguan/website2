LE = 0
BE = 1

def ip2str(ipuint, endian = LE)->str:
    if LE == endian:
        return '{}.{}.{}.{}'.format((ipuint & 0xFF), ((ipuint >> 8) & 0xFF), ((ipuint >> 16) & 0xFF), ((ipuint >> 24) & 0xFF))
    else:
        return '{3}.{2}.{1}.{0}'.format((ipuint & 0xFF), ((ipuint >> 8) & 0xFF), ((ipuint >> 16) & 0xFF), ((ipuint >> 24) & 0xFF))

def str2ip(ipstr, endian = LE)->int:
    ipuint = 0
    bits_move_le = (24, 16, 8, 0)
    bits_move_be = (0, 8, 16, 24)
    seg = ipstr.split('.')
    if 4 != len(seg):
        return 0
    i = 0
    for n in seg:
        if False == n.isdigit():
            raise TypeError()
            return 0
        if LE == endian:
            ipuint |= int(n) <<  bits_move_le[i]
        else:
            ipuint |= int(n) <<  bits_move_be[i]
        i += 1
    return ipuint