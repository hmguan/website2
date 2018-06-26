class nspdef(object):
    """
    package head = {'N', 's', 'p', 'd' #length }
    """
    def tcp_parser( data, cb, pkt_cb)->int:
        if data[0] != 0x4E or data[1] != 0x73 or data[2] != 0x70 or data[3] != 0x64:
            print('Nspd verify failed.')
            return -1

        # warning: (-0x7b | 0x100) == -0x7b. what the fuck?
        acquire_bytes = int(data[4]) & 0xFF
        acquire_bytes |= ((data[5] & 0xFF) << 8)
        acquire_bytes |= ((data[6] & 0xFF) << 16)
        acquire_bytes |= ((data[7] & 0xFF) << 24)

        if None != pkt_cb:
            pkt_cb.contents.value = acquire_bytes
        return 0

    def tcp_builder(data, cb)->int:
        if None == data or cb <= 0:
            return -1
        data[0] = 0x4E
        data[1] = 0x73 
        data[2] = 0x70 
        data[3] = 0x64
        data[4] = cb & 0xFF
        data[5] = ((cb >> 8) & 0xFF)
        data[6] = ((cb >> 16) & 0xFF)
        data[7] = ((cb >> 24) & 0xFF)
        return 0