import webcolors

def rgb_to_hex(red, green, blue):
    rgbList = [red, green, blue]
    returnList = []
    for idx in rgbList:
        if idx < 10:
            returnList.append('0' + hex(idx)[2:].upper())
        else:
            returnList.append(hex(idx)[2:].upper())
    return '#'+"".join(returnList)

abc = rgb_to_hex(255,0,0)
print(abc)

print(webcolors.hex_to_name(abc))