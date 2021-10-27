from codigo.Isla.Herramientas.Herramienta import Herramienta
from codigo.Isla.Helper import Helper

class Pico(Herramienta):


    def __init__(self):
        # Es la herramienta principal para minar piedra
        Herramienta.__init__(self)
        self.image = Helper.PICO
        self.dañoPiedra = 5
        self.dañoArbol = 1
        self.dañoPersona = 4
        self.dañoAnimal = 4
        

    def restarUso(self):
        self.usos -= 1
        if self.usos == 0:
            self.rota = True
            self.image = Helper.PICO_ROTO