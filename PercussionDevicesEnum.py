#coding=utf-8

__author__ = 'Luca'


class PercussionDevices(object):
    def __init__(self):
        self.PercussionDevicesDict = {33: "MetronomeClick",
                                34: "MetronomeBell",
                                35: "AcousticBassDrum",
                                36: "BassDrum1",
                                37: "SideStick",
                                38: "AcousticSnare",
                                39: "HandClap",
                                40: "ElectricSnare",
                                41: "LowFloorTom",
                                42: "ClosedHiHat",
                                43: "HighFloorTom",
                                44: "PedalHiHat",
                                45: "LowTom",
                                46: "OpenHiHat",
                                47: "LowMidTom",
                                48: "HiMidTom",
                                49: "CrashCymbal1",
                                50: "HighTom",
                                51: "RideCymbal1",
                                52: "ChineseCymbal",
                                53: "RideBell",
                                54: "Tambourine",
                                55: "SplashCymbal",
                                56: "Cowbell",
                                57: "CrashCymbal2",
                                58: "Vibraslap",
                                59: "RideCymbal2",
                                60: "HiBongo",
                                61: "LowBongo",
                                62: "MuteHiConga",
                                63: "OpenHiConga",
                                64: "LowConga",
                                65: "HighTimbale",
                                66: "LowTimbale",
                                67: "HighAgogo",
                                68: "LowAgogo",
                                69: "Cabasa",
                                70: "Maracas",
                                71: "ShortWhistle",
                                72: "LongWhistle",
                                73: "ShortGuiro",
                                74: "LongGuiro",
                                75: "Claves",
                                76: "HiWoodBlock",
                                77: "LowWoodBlock",
                                78: "MuteCuica",
                                79: "OpenCuica",
                                80: "MuteTriangle",
                                81: "OpenTriangle"}

    def get_timber_group(self, inst_list):

        HighTimberInstruments = {}
        MediumTimberInstruments = {}
        LowTimberInstruments = {}

        if inst_list in HighTimberInstruments:
            return "high"
        elif inst_list in MediumTimberInstruments:
            return "medium"
        elif inst_list in LowTimberInstruments:
            return "low"
        else:
            return "none"



    #lines = []
    #file = open('/home/panic/Desktop/instruments', 'r')
    #
    #for i, line in enumerate(file):
    #    #print i
    #    linha = line.split(" = ")[::-1]
    #
    #    #lines.append()
    #
    #    print([s.strip() for s in linha][0] + " : \"" + [s.strip() for s in linha][1] + "\", ")
    #