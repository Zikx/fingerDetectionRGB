import webcolors

def rgb_to_hex(red, green, blue):
    rgbList = [red, green, blue]
    returnList = []
    for idx in rgbList:
        returnList.append(hex(idx)[2:].upper())
    return '#'+"".join(returnList)
print(rgb_to_hex(255,0,0))

# valu = rgb_to_hex(255, 0, 0)
# valu = '#FF00'
# print(webcolors.hex_to_name(valu, spec='css3'))
# print(webcolors.hex_to_name())


