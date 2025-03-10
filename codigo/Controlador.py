import json
import os

import pygame
from codigo.Isla.Isla import Isla


class Controlador:

    def __init__(self, isla, camara, partida):
        self.isla = isla
        self.camara = camara
        self.mouse = camara.getMouse()
        self.aldea = self.isla.getAldea()
        self.ancho = self.isla.getAncho()
        self.altura = self.isla.getAltura()
        self.partida = partida
        self.running = False
        self.click = True
        self.camara.setControlador(self)

    def run(self):
        """ Se corre el jueguito con el personaje """
        # Controlar tiempo en el juego

        if not self.running:
            self.running = True

            clock = pygame.time.Clock()
            screenUpdate = 1
            # Tiempo para movibles
            pygame.time.set_timer(screenUpdate, 250)
            # Tiempo para arboles
            arbolesUpdate = 2
            pygame.time.set_timer(arbolesUpdate, 10000)

            ciclocDeVidaPersonas = 3
            pygame.time.set_timer(ciclocDeVidaPersonas, 20000)

            while self.running:
                # Checkea todos los eventos
                for event in pygame.event.get():
                    # Cerrar juego
                    if event.type == pygame.QUIT:
                        self.stopGame()

                    # Checkea si algun boton del mouse es presionado
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.mousePressed(pygame.mouse.get_pressed())
                        if event.button == 4:
                            # Baja el zoom
                            self.camara.getZoom().bajarZoom()

                        if event.button == 5:
                            # Aumenta el zoom
                            self.camara.getZoom().subirZoom()

                    if event.type == pygame.KEYDOWN:
                        self.keyEvent(event.key)

                    if event.type == screenUpdate:
                        self.moviblesUpdate()

                    if event.type == arbolesUpdate:
                        self.arbolesUpdate()

                    if event.type == ciclocDeVidaPersonas:
                        self.personasUpdate()

                self.camara.actualizarPantalla()
                self.camara.getUI().generarAldeaUI(self.aldea)
                self.camara.dibujarUI()
                pygame.display.update()

                clock.tick(60)
                # El reloj por el cual todos los eventos se actualizan

    def personasUpdate(self):
        """ Dentro de los arboles talados, se suma el tiempo para que vuelva a crecer """
        for persona in self.isla.getAldea().getPersonas():
            persona.cicloVida()

    def arbolesUpdate(self):
        """ Dentro de los arboles talados, se suma el tiempo para que vuelva a crecer """
        for arbol in self.isla.getArbolesTalados():
            arbol.avanzarTiempo()

    def moviblesUpdate(self):
        """ Cuando se actualiza la pantalla, se movera todas las personas y animales """
        self.click = True
        for persona in self.aldea.getPersonas():
            persona.makeMoves()

        for animal in self.camara.getIsla().getAnimales():
            animal.makeMoves()

    def stopGame(self):
        """ Termina el loop del juego y guarda la partida"""
        if not self.camara.getIsla() == self.isla:
            for persona in self.isla.getAldea().getPersonas():
                if persona.getIsla() == self.camara.getIsla():
                    self.camara.getIsla().enviarViajero(persona)
                    self.isla.agregarViajero(persona)
            self.camara.getIsla().toJsonPath(f'Islas/' + self.camara.getIsla().getNombre() + '.json')
        self.isla.toJson(self.partida)

        self.running = False

    def keyEvent(self, event):
        """ Detecta cuando una tecla del teclado clickeado """
        if event == pygame.K_RIGHT or event == pygame.K_d:
            self.camara.moveX(2)

        if event == pygame.K_LEFT or event == pygame.K_a:
            self.camara.moveX(-2)

        if event == pygame.K_UP or event == pygame.K_w:
            self.camara.moveY(-2)

        if event == pygame.K_DOWN or event == pygame.K_s:
            self.camara.moveY(2)

        if event == pygame.K_z:
            self.camara.getZoom().subirZoom()

        if event == pygame.K_x:
            self.camara.getZoom().bajarZoom()

        if event == pygame.K_SPACE:
            # Mueve la camara para volver a la aldea
            self.camara.setPosY(self.altura // 2)
            self.camara.setPosX(self.ancho // 2)

    def mousePressed(self, mouse):
        """ Detecta cuando el mouse es presionado """

        left, middle, right = mouse
        if left:

            # En el caso que sea el izquierdo se fija si hay UI´s
            if not self.camara.getUI().hayUIActivos():

                if not self.camara.getObjetoMouse() is None:
                    self.camara.colocarObjeto()

                elif not self.mouse.seleccionarMovible() is None:
                    self.camara.getUI().generarInfoObjeto(self.mouse.seleccionarMovible())

                elif not self.mouse.pedirInfoObjeto() is None:
                    self.camara.getUI().generarInfoObjeto(self.mouse.pedirInfoObjeto())

            else:
                if self.click:
                    self.mouse.clickearPorPoscicion(self.camara.getUI().getObjetosClickeables())

                self.click = False

        # En el caso que sea derecha checkea si esta seleccionado
        if right:

            # Si esta seleccionado y no es una persona, y trata de seleccionar una persona, la selecciona.
            if not self.mouse.seleccionarMovible() is None:

                if not self.camara.getSeleccionado() == self.mouse.seleccionarMovible():

                    if self.mouse.seleccionarMovible() in self.aldea.getPersonas():
                        self.camara.setSeleccionado(self.mouse.seleccionarMovible())

                else:
                    # Si tiene algo seleccionado y es una persona, la deselecciona
                    self.camara.setSeleccionado(None)

            if not self.camara.getSeleccionado() is None:
                if self.mouse.pedirInfoObjeto() is None:
                    # Si lo seleccionado es una persona, y selecciona al piso, lo mueve al lugar
                    self.camara.getSeleccionado().moveToPosition(self.mouse.getObjectMousePosition()[0],
                                                                 self.mouse.getObjectMousePosition()[1])


                else:
                    if self.mouse.seleccionarMovible() is None:
                        # Si selecciona un objeto se fija si no es movible, hacerle algo al objeto
                        self.camara.getSeleccionado().accionarObjeto(self.mouse.pedirInfoObjeto())

                    else:
                        # Si selecciona a un movible, desde una persona, se fija de poder hacerle algo al movile
                        if not self.mouse.seleccionarMovible() in self.aldea.getPersonas():
                            self.camara.getSeleccionado().accionarObjeto(self.mouse.seleccionarMovible())

    def cargarIslaPrincipal(self, explorador):
        self.camara.getIsla().enviarViajero(explorador)
        self.camara.getIsla().toJsonPath(f'Islas/' + self.camara.getIsla().getNombre() + '.json')
        self.camara.setIsla(self.isla)
        self.isla.agregarViajero(explorador)

    def cargarIslaSecundaria(self, isla, explorador):
        islaSecundaria = None
        archivos = os.listdir("Islas")
        for archivo in archivos:
            if archivo.split(".")[0] == isla:
                data = None
                with open(f'Islas/' + isla + '.json', 'r') as file:
                    data = json.load(file)

                islaSecundaria = Isla()
                islaSecundaria.cargarMapaConArchivo(data)
                self.camara.getIsla().enviarViajero(explorador)
                self.camara.setIsla(islaSecundaria)
                islaSecundaria.agregarViajero(explorador)
                return

        islaSecundaria = Isla()
        islaSecundaria.generarIslaDesconocida(400, 400)
        islaSecundaria.setNombre(isla)

        self.camara.getIsla().enviarViajero(explorador)
        if self.camara.getIsla().getNombre() != self.isla.getNombre():
            self.camara.getIsla().toJsonPath(f'Islas/' + self.camara.getIsla().getNombre() + '.json')
        self.camara.setIsla(islaSecundaria)
        islaSecundaria.agregarViajero(explorador)

    def getIsla(self):
        return self.isla

    def getCamara(self):
        return self.camara
