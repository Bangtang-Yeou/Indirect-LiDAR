def Outputmode2value(mode):
    
    if mode == 'A-B':
        return 0
    
    if mode == 'A+B':
        return 1
    
    if mode == 'A':
        return 2
    
    if mode == 'B':
        return 3

def Value2outputmode(value):
    
    if value == 0:
        return 'A-B'
    
    if value == 1:
        return 'A+B'
    
    if value == 2:
        return 'A'
    
    if value == 3:
        return 'B'
    
def Operatingmode2value(mode):
    
    if mode == 'Raw phases':
        return 0x00C0
    
    if mode == 'Distance Amplitude':
        return 0x0000
    
    if mode == 'Distance confidence':
        return 0x00D0
    
def Value2operatingmode(value):
    
    if value == 0x00C0:
        return 'Raw phases'
    
    if value == 0x0000:
        return 'Distance Amplitude'
    
    if value == 0x00D0:
        return 'Distance confidence'