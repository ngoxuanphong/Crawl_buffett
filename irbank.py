from src.savePDF import GetPpfIrbank

if __name__ == "__main__":
    irbank = GetPpfIrbank()
    irbank.getAllCom()
    # irbank.savePDF(1606)