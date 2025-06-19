from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Vec3  # 用于方向移动
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay, CollisionSphere
from panda3d.core import Point3, BitMask32
from direct.task import Task

import sys


class World(ShowBase):

    def genLabelText(self, text, i):
        return OnscreenText(text=text, pos=(0.06, -.06 * (i + 0.5)), fg=(1, 1, 1, 1),
                            parent=base.a2dTopLeft, align=TextNode.ALeft, scale=.05)

    def __init__(self):
        super().__init__()  
        self.setBackgroundColor(0, 0, 0)
        base.disableMouse()
        self.camSpeed = 2  # 摄像机移动速度
        self.camRotSpeed = 2  # 摄像头旋转速度
        self.camZoomSpeed = 5  # 鼠标滚轮缩放速度
        camera.setPos(0, 0, 85)
        camera.setHpr(0, -90, 0)

        self.yearscale = 60
        self.dayscale = self.yearscale / 365.0 * 5
        self.orbitscale = 10
        self.sizescale = 0.6
        self.planet_speed_factor = 1.0



        self.loadPlanets()
        # self.rotatePlanets()

        self.title = OnscreenText(
            text="Panda3D: Solar System Simulation",
            parent=base.a2dBottomRight, align=TextNode.A_right,
            style=1, fg=(1, 1, 1, 1), pos=(-0.1, 0.1), scale=.07)

        self.mouse1EventText = self.genLabelText(
            "Mouse Button 1: Toggle entire Solar System [RUNNING]", 1)
        self.skeyEventText = self.genLabelText("[S]: Toggle Sun [RUNNING]", 2)
        self.ykeyEventText = self.genLabelText("[Y]: Toggle Mercury [RUNNING]", 3)
        self.vkeyEventText = self.genLabelText("[V]: Toggle Venus [RUNNING]", 4)
        self.ekeyEventText = self.genLabelText("[E]: Toggle Earth [RUNNING]", 5)
        self.mkeyEventText = self.genLabelText("[M]: Toggle Mars [RUNNING]", 6)
        self.jkeyEventText = self.genLabelText("[J]: Toggle Jupiter [RUNNING]", 7)
        self.xkeyEventText = self.genLabelText("[X]: Toggle Saturn [RUNNING]", 8)
        self.ukeyEventText = self.genLabelText("[U]: Toggle Uranus [RUNNING]", 9)
        self.nkeyEventText = self.genLabelText("[N]: Toggle Neptune [RUNNING]", 10)
        self.yearCounterText = self.genLabelText("0 Earth years completed", 11)

        self.yearCounter = 0
        self.simRunning = True

        self.accept("escape", sys.exit)
        self.accept("mouse1", self.handleMouseClick)
        # self.accept("e", self.handleEarth)
        # self.accept("s", self.togglePlanet, ["Sun", self.day_period_sun, None, self.skeyEventText])
        # self.accept("y", self.togglePlanet, ["Mercury", self.day_period_mercury, self.orbit_period_mercury, self.ykeyEventText])
        # self.accept("v", self.togglePlanet, ["Venus", self.day_period_venus, self.orbit_period_venus, self.vkeyEventText])
        # self.accept("m", self.togglePlanet, ["Mars", self.day_period_mars, self.orbit_period_mars, self.mkeyEventText])
        # self.accept("j", self.togglePlanet, ["Jupiter", self.day_period_jupiter, self.orbit_period_jupiter, self.jkeyEventText])
        # self.accept("x", self.togglePlanet, ["Saturn", self.day_period_saturn, self.orbit_period_saturn, self.xkeyEventText])
        # self.accept("u", self.togglePlanet, ["Uranus", self.day_period_uranus, self.orbit_period_uranus, self.ukeyEventText])
        # self.accept("n", self.togglePlanet, ["Neptune", self.day_period_saturn, self.orbit_period_saturn, self.nkeyEventText])
        self.accept("newYear", self.incYear)

        self.accept("arrow_up", self.moveCamera, [Vec3(0, self.camSpeed, 0)])
        self.accept("arrow_down", self.moveCamera, [Vec3(0, -self.camSpeed, 0)])
        self.accept("arrow_left", self.moveCamera, [Vec3(-self.camSpeed, 0, 0)])
        self.accept("arrow_right", self.moveCamera, [Vec3(self.camSpeed, 0, 0)])
        self.accept("page_up", self.moveCamera, [Vec3(0, 0, self.camSpeed)])
        self.accept("page_down", self.moveCamera, [Vec3(0, 0, -self.camSpeed)])
        
        # 控制旋转的变量
        self.pitchUp = False
        self.pitchDown = False
        self.yawLeft = False
        self.yawRight = False

        # 绑定旋转控制
        self.accept("a", self.setYawLeft, [True])
        self.accept("a-up", self.setYawLeft, [False])
        self.accept("d", self.setYawRight, [True])
        self.accept("d-up", self.setYawRight, [False])
        self.accept("arrow_up", self.setPitchUp, [True])
        self.accept("arrow_up-up", self.setPitchUp, [False])
        self.accept("arrow_down", self.setPitchDown, [True])
        self.accept("arrow_down-up", self.setPitchDown, [False])

        # 添加任务更新摄像头方向
        self.taskMgr.add(self.updateCameraRotation, "updateCameraRotation")

        # 添加键盘控制摄像头旋转
        self.accept("t", self.setPitchUp, [True])
        self.accept("t-up", self.setPitchUp, [False])
        self.accept("g", self.setPitchDown, [True])
        self.accept("g-up", self.setPitchDown, [False])
        self.accept("f", self.setYawLeft, [True])
        self.accept("f-up", self.setYawLeft, [False])
        self.accept("h", self.setYawRight, [True])
        self.accept("h-up", self.setYawRight, [False])

        
        self.accept("i", self.moveCamera, [Vec3(0, self.camSpeed, 0)])
        self.accept("k", self.moveCamera, [Vec3(0, -self.camSpeed, 0)])
        self.accept("j", self.moveCamera, [Vec3(-self.camSpeed, 0, 0)])
        self.accept("l", self.moveCamera, [Vec3(self.camSpeed, 0, 0)])
        self.accept("u", self.moveCamera, [Vec3(0, 0, self.camSpeed)])  # 向上移动
        self.accept("o", self.moveCamera, [Vec3(0, 0, -self.camSpeed)])  # 向下移动
        # self.accept('[', self.decreasePlanetSpeed)
        # self.accept(']', self.increasePlanetSpeed)

        

        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)

        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)

        self.camNode = self.cam.node()  # 方便你后面用 self.camNode

        # 添加鼠标滚轮控制缩放
        self.accept("mouse3", self.handleMouseWheel)

        self.planetInfoText = OnscreenText(
            text="Click a planet!",
            parent=base.a2dBottomLeft,
            pos=(0.1, 0.3),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft
        )

         # 角度记录
        self.planet_angles = {
            "sun_spin": 0.0,
            "mercury_spin": 0.0,
            "mercury_orbit": 0.0,
            "venus_spin": 0.0,
            "venus_orbit": 0.0,
            "mars_spin": 0.0,
            "mars_orbit": 0.0,
            "earth_spin": 0.0,
            "earth_orbit": 0.0,
            "jupiter_spin": 0.0,
            "jupiter_orbit": 0.0,
            "saturn_spin": 0.0,
            "saturn_orbit": 0.0,
            "uranus_spin": 0.0,
            "uranus_orbit": 0.0,
            "neptune_spin": 0.0,
            "neptune_orbit": 0.0,
        }

        # 添加更新任务
        self.taskMgr.add(self.updatePlanets, "UpdatePlanetTask")

        # 键盘控制
        self.accept("arrow_up", self.increasePlanetSpeed)
        self.accept("arrow_down", self.decreasePlanetSpeed)
        print("↑ 增加速度，↓ 减小速度")


    def handleMouseWheel(self):
        # 获取鼠标滚轮的方向
        wheel = base.mouseWatcherNode.getWheel()
        if wheel > 0:  # 鼠标滚轮向上
            camera.setPos(camera.getPos() + Vec3(0, 0, -self.camZoomSpeed))  # 向前移动
        elif wheel < 0:  # 鼠标滚轮向下
            camera.setPos(camera.getPos() + Vec3(0, 0, self.camZoomSpeed))  # 向后移动

    def moveCamera(self, offset):
        camera.setPos(camera.getPos() + offset)

    def setYawLeft(self, value):
        self.yawLeft = value

    def setYawRight(self, value):
        self.yawRight = value

    def setPitchUp(self, value):
        self.pitchUp = value

    def setPitchDown(self, value):
        self.pitchDown = value

    def updateCameraRotation(self, task):
        h, p, r = camera.getHpr()

        if self.yawLeft:
            h += self.camRotSpeed
        if self.yawRight:
            h -= self.camRotSpeed
        if self.pitchUp:
            p += self.camRotSpeed
        if self.pitchDown:
            p -= self.camRotSpeed

        camera.setHpr(h, p, r)
        return task.cont

    def handleMouseClick(self):
    # Detect which object was clicked
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            self.picker.traverse(self.render)
            print(mpos)
            print(self.pq.getNumEntries())
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()

                # Traverse up to find the model with the correct tag
                pickedPlanet = pickedObj.findNetTag('planet')
                if not pickedPlanet.isEmpty():
                    planetName = pickedPlanet.getTag('planet')
                    self.showPlanetInfo(planetName)
            else:
                print("Clicked on empty space.")

    def showPlanetInfo(self, planetName):
        # Example basic info dictionary
        planetInfo = {
            "Sun": {
                "Name": "Sun",
                "Type": "Star",
                "Diameter": "1,392,700 km",
                "Day Length": "About 25 Earth days",
                "Orbit Period": "N/A"
            },
            "Mercury": {
                "Name": "Mercury",
                "Type": "Planet",
                "Diameter": "4,879 km",
                "Day Length": "58.6 Earth days",
                "Orbit Period": "88 Earth days"
            },
            "Venus": {
                "Name": "Venus",
                "Type": "Planet",
                "Diameter": "12,104 km",
                "Day Length": "243 Earth days",
                "Orbit Period": "225 Earth days"
            },
            "Earth": {
                "Name": "Earth",
                "Type": "Planet",
                "Diameter": "12,742 km",
                "Day Length": "24 hours",
                "Orbit Period": "365 days"
            },
            "Moon": {
                "Name": "Moon",
                "Type": "Satellite",
                "Diameter": "3,474 km",
                "Day Length": "27.3 Earth days",
                "Orbit Period": "27.3 Earth days"
            },
            "Mars": {
                "Name": "Mars",
                "Type": "Planet",
                "Diameter": "6,779 km",
                "Day Length": "24.6 hours",
                "Orbit Period": "687 Earth days"
            },
            "Jupiter":{
                "Name": "Jupiter",
                "Type": "Planet",
                "Diameter": "139,820 km",
                "Day Length": "9.9 hours",
                "Orbit Period": "4,333 Earth days"
            },
            "Saturn":{
                "Name": "Saturn",
                "Type": "Planet",
                "Diameter": "120,500 km",
                "Day Length": "10.7 hours",
                "Orbit Period": "10,756 Earth days"
            },
            "Uranus":{
                "Name": "Uranus",
                "Type": "Planet",
                "Diameter": "50,724 km",
                "Day Length": "17.14 hours",
                "Orbit Period": "84 Earth years"
            },
            "Neptune":{
                "Name": "Neptune",
                "Type": "Planet",
                "Diameter": "49,528 km",
                "Day Length": "16.6 hours",
                "Orbit Period": "165 Earth years"
            }
        }

        if planetName in planetInfo:
            info = planetInfo[planetName]
            print(f"--- {info['Name']} ---")
            print(f"Type: {info['Type']}")
            print(f"Diameter: {info['Diameter']}")
            print(f"Day Length: {info['Day Length']}")
            print(f"Orbit Period: {info['Orbit Period']}")
            
            # Optionally, you can update a GUI text node instead of printing
            self.planetInfoText.setText(
                f"{info['Name']}\n"
                f"Type: {info['Type']}\n"
                f"Diameter: {info['Diameter']}\n"
                f"Day Length: {info['Day Length']}\n"
                f"Orbit Period: {info['Orbit Period']}"
            )
        else:
            print(f"No data available for {planetName}.")


    def togglePlanet(self, planet, day, orbit=None, text=None):
        if day.isPlaying():
            print("Pausing " + planet)
            state = " [PAUSED]"
        else:
            print("Resuming " + planet)
            state = " [RUNNING]"
        if text:
            old = text.getText()
            text.setText(old[0:old.rfind(' ')] + state)
        self.toggleInterval(day)
        if orbit:
            self.toggleInterval(orbit)

    def toggleInterval(self, interval):
        if interval.isPlaying():
            interval.pause()
        else:
            interval.resume()

    def handleEarth(self):
        self.togglePlanet("Earth", self.day_period_earth, self.orbit_period_earth, self.ekeyEventText)
        self.togglePlanet("Moon", self.day_period_moon, self.orbit_period_moon)

    def incYear(self):
        self.yearCounter += 1
        self.yearCounterText.setText(str(self.yearCounter) + " Earth years completed")

    def loadPlanets(self):
        self.orbit_root_mercury = render.attachNewNode('orbit_root_mercury')
        self.orbit_root_venus = render.attachNewNode('orbit_root_venus')
        self.orbit_root_mars = render.attachNewNode('orbit_root_mars')
        self.orbit_root_earth = render.attachNewNode('orbit_root_earth')
        self.orbit_root_jupiter = render.attachNewNode('orbit_root_jupiter')
        self.orbit_root_saturn = render.attachNewNode('orbit_root_saturn')
        self.orbit_root_uranus = render.attachNewNode('orbit_root_uranus')
        self.orbit_root_neptune = render.attachNewNode('orbit_root_neptune')
        self.orbit_root_moon = self.orbit_root_earth.attachNewNode('orbit_root_moon')
        

        self.sky = loader.loadModel("models/solar_sky_sphere")
        self.sky_tex = loader.loadTexture("models/stars_1k_tex.jpg")
        self.sky.setTexture(self.sky_tex, 1)
        self.sky.reparentTo(render)
        self.sky.setScale(50)

        self.sun = loader.loadModel("models/planet_sphere")
        self.sun_tex = loader.loadTexture("models/sun_1k_tex.jpg")
        self.sun.setTexture(self.sun_tex, 1)
        self.sun.reparentTo(render)
        self.sun.setScale(2 * self.sizescale)
        self.sun.setTag('planet', 'Sun')

        # Add collision solid to the planet
        cNode = CollisionNode('planet_collision')
        cNode.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNode.setFromCollideMask(BitMask32.allOff())
        cNode.setIntoCollideMask(BitMask32.bit(1))
        cNodePath = self.sun.attachNewNode(cNode)

        # Setup collision system
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = self.camera.attachNewNode(self.pickerNode)
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerNode.setIntoCollideMask(BitMask32.allOff())

        self.picker.addCollider(self.pickerNP, self.pq)

        # Accept mouse click
        self.accept('mouse1', self.on_mouse_click)

        self.mercury = loader.loadModel("models/planet_sphere")
        self.mercury_tex = loader.loadTexture("models/mercury_1k_tex.jpg")
        self.mercury.setTexture(self.mercury_tex, 1)
        self.mercury.reparentTo(self.orbit_root_mercury)
        self.mercury.setPos(0.188 * self.orbitscale, 0, 0)
        self.mercury.setScale(0.385 * self.sizescale)
        self.mercury.setTag('planet', 'Mercury')

        # Add collision solid to the planet
        cNodeMercury = CollisionNode('planet_collision')
        cNodeMercury.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeMercury.setFromCollideMask(BitMask32.allOff())
        cNodeMercury.setIntoCollideMask(BitMask32.bit(1))
        cNodeMercuryPath = self.mercury.attachNewNode(cNodeMercury)

        self.venus = loader.loadModel("models/planet_sphere")
        self.venus_tex = loader.loadTexture("models/venus_1k_tex.jpg")
        self.venus.setTexture(self.venus_tex, 1)
        self.venus.reparentTo(self.orbit_root_venus)
        self.venus.setPos(0.432 * self.orbitscale, 0, 0)
        self.venus.setScale(0.923 * self.sizescale)
        self.venus.setTag('planet', 'Venus')

        # Add collision solid to the planet
        cNodeVenus = CollisionNode('planet_collision')
        cNodeVenus.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeVenus.setFromCollideMask(BitMask32.allOff())
        cNodeVenus.setIntoCollideMask(BitMask32.bit(1))
        cNodeVenusPath = self.venus.attachNewNode(cNodeVenus)

        self.mars = loader.loadModel("models/planet_sphere")
        self.mars_tex = loader.loadTexture("models/mars_1k_tex.jpg")
        self.mars.setTexture(self.mars_tex, 1)
        self.mars.reparentTo(self.orbit_root_mars)
        self.mars.setPos(0.996 * self.orbitscale, 0, 0)
        self.mars.setScale(0.515 * self.sizescale)
        self.mars.setTag('planet', 'Mars')

        # Add collision solid to the planet
        cNodeMars = CollisionNode('planet_collision')
        cNodeMars.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeMars.setFromCollideMask(BitMask32.allOff())
        cNodeMars.setIntoCollideMask(BitMask32.bit(1))
        cNodeMarsPath = self.mars.attachNewNode(cNodeMars)

        self.earth = loader.loadModel("models/planet_sphere")
        self.earth_tex = loader.loadTexture("models/earth_1k_tex.jpg")
        self.earth.setTexture(self.earth_tex, 1)
        self.earth.reparentTo(self.orbit_root_earth)
        self.earth.setPos(0.679 * self.orbitscale, 0, 0)
        self.earth.setScale(self.sizescale)
        self.earth.setTag('planet', 'Earth')

        # Add collision solid to the planet
        cNodeEarth = CollisionNode('planet_collision')
        cNodeEarth.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeEarth.setFromCollideMask(BitMask32.allOff())
        cNodeEarth.setIntoCollideMask(BitMask32.bit(1))
        cNodeEarthPath = self.earth.attachNewNode(cNodeEarth)

        self.orbit_root_moon = self.earth.attachNewNode("moon_orbit_root")
        self.orbit_root_moon.setPos(0, 0, 0)  # 相对地球中心
        self.moon = loader.loadModel("models/planet_sphere")
        self.moon_tex = loader.loadTexture("models/moon_1k_tex.jpg")
        self.moon.setTexture(self.moon_tex, 1)
        self.moon.reparentTo(self.orbit_root_moon)
        self.moon.setPos(0.15 * self.orbitscale, 0, 0)
        self.moon.setScale(0.27 * self.sizescale)
        self.moon.setTag('planet', 'Moon')

        # Add collision solid to the planet
        cNodeMoon = CollisionNode('planet_collision')
        cNodeMoon.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeMoon.setFromCollideMask(BitMask32.allOff())
        cNodeMoon.setIntoCollideMask(BitMask32.bit(1))
        cNodeMoonPath = self.moon.attachNewNode(cNodeMoon)

        self.jupiter = loader.loadModel("models/planet_sphere")
        self.jupiter_tex = loader.loadTexture("jupi.jpeg")
        self.jupiter.setTexture(self.jupiter_tex, 1)
        self.jupiter.reparentTo(self.orbit_root_jupiter)
        self.jupiter.setPos(1.150 * self.orbitscale, 0, 0)
        self.jupiter.setScale(self.sizescale)
        self.jupiter.setTag('planet', 'Jupiter')

        # Add collision solid to the planet
        cNodeJupiter = CollisionNode('planet_collision')
        cNodeJupiter.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeJupiter.setFromCollideMask(BitMask32.allOff())
        cNodeJupiter.setIntoCollideMask(BitMask32.bit(1))
        cNodeJupiterPath = self.jupiter.attachNewNode(cNodeJupiter)

        self.saturn = loader.loadModel("models/planet_sphere")
        self.saturn_tex = loader.loadTexture("saturn.jpeg")
        self.saturn.setTexture(self.saturn_tex, 1)
        self.saturn.reparentTo(self.orbit_root_saturn)
        self.saturn.setPos(1.426 * self.orbitscale, 0, 0)
        self.saturn.setScale(self.sizescale)
        self.saturn.setTag('planet', 'Saturn')

        # Add collision solid to the planet
        cNodeSaturn = CollisionNode('planet_collision')
        cNodeSaturn.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeSaturn.setFromCollideMask(BitMask32.allOff())
        cNodeSaturn.setIntoCollideMask(BitMask32.bit(1))
        cNodeSaturnPath = self.saturn.attachNewNode(cNodeSaturn)

        self.uranus = loader.loadModel("models/planet_sphere")
        self.uranus_tex = loader.loadTexture("uranus.jpg")
        self.uranus.setTexture(self.uranus_tex, 1)
        self.uranus.reparentTo(self.orbit_root_uranus)
        self.uranus.setPos(2.871 * self.orbitscale, 0, 0)
        self.uranus.setScale(self.sizescale)
        self.uranus.setTag('planet', 'Uranus')

        # Add collision solid to the planet
        cNodeUranus = CollisionNode('planet_collision')
        cNodeUranus.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeUranus.setFromCollideMask(BitMask32.allOff())
        cNodeUranus.setIntoCollideMask(BitMask32.bit(1))
        cNodeUranusPath = self.uranus.attachNewNode(cNodeUranus)

        self.neptune = loader.loadModel("models/planet_sphere")
        self.neptune_tex = loader.loadTexture("nep.jpeg")
        self.neptune.setTexture(self.neptune_tex, 1)
        self.neptune.reparentTo(self.orbit_root_neptune)
        self.neptune.setPos(4.509 * self.orbitscale, 0, 0)
        self.neptune.setScale(self.sizescale)
        self.neptune.setTag('planet', 'Neptune')

        # Add collision solid to the planet
        cNodeNeptune = CollisionNode('planet_collision')
        cNodeNeptune.addSolid(CollisionSphere(0, 0, 0, 1.5))  # Radius should match planet size
        cNodeNeptune.setFromCollideMask(BitMask32.allOff())
        cNodeNeptune.setIntoCollideMask(BitMask32.bit(1))
        cNodeNeptunePath = self.neptune.attachNewNode(cNodeNeptune)

    def rotatePlanets(self, speed_factor=1.0):
    # 太阳自转（无公转）
        self.day_period_sun = self.sun.hprInterval(10.0 * self.dayscale, (360, 0, 0))
        self.day_period_sun.loop()  # 使用 loop() 让动画持续运行

        # 水星（Mercury）公转和自转
        self.orbit_period_mercury = self.orbit_root_mercury.hprInterval(87.9 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_mercury = self.mercury.hprInterval(58.6 * self.dayscale, (360, 0, 0))
        self.orbit_period_mercury.loop()  # 公转
        self.day_period_mercury.loop()    # 自转

        # 金星（Venus）公转和自转
        self.orbit_period_venus = self.orbit_root_venus.hprInterval(225.0 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_venus = self.venus.hprInterval(243.0 * self.dayscale, (360, 0, 0))
        self.orbit_period_venus.loop()  # 公转
        self.day_period_venus.loop()    # 自转

        # 地球（Earth）公转和自转
        self.orbit_period_earth = self.orbit_root_earth.hprInterval(365.25 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_earth = self.earth.hprInterval(1.0 * self.dayscale, (360, 0, 0))
        self.orbit_period_earth.loop()  # 公转
        self.day_period_earth.loop()    # 自转

        # 火星（Mars）公转和自转
        self.orbit_period_mars = self.orbit_root_mars.hprInterval(1.88 * 365.25 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_mars = self.mars.hprInterval(1.03 * self.dayscale, (360, 0, 0))
        self.orbit_period_mars.loop()  # 公转
        self.day_period_mars.loop()    # 自转

        # 月球（Moon）公转和自转
        self.orbit_period_moon = self.orbit_root_moon.hprInterval(27.3 * self.yearscale, (360, 0, 0))
        self.day_period_moon = self.moon.hprInterval(1.14 * self.dayscale, (360, 0, 0))
        self.orbit_period_moon.loop()  # 公转
        self.day_period_moon.loop()    # 自转

        # jupiter
        self.orbit_period_jupiter = self.orbit_root_jupiter.hprInterval(12 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_jupiter = self.jupiter.hprInterval(0.42 * self.dayscale, (360, 0, 0))
        self.orbit_period_jupiter.loop()  # 公转
        self.day_period_jupiter.loop()    # 自转

        #Saturn
        self.orbit_period_saturn = self.orbit_root_saturn.hprInterval(29.4 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_saturn = self.saturn.hprInterval(0.44 * self.dayscale, (360, 0, 0))
        self.orbit_period_saturn.loop()  # 公转
        self.day_period_saturn.loop() 

        #Uranus
        self.orbit_period_uranus = self.orbit_root_uranus.hprInterval(84 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_uranus = self.uranus.hprInterval(30.687 * self.dayscale, (360, 0, 0))
        self.orbit_period_uranus.loop()  # 公转
        self.day_period_uranus.loop() 

        #neptune
        self.orbit_period_neptune = self.orbit_root_neptune.hprInterval(165 * self.yearscale / speed_factor, (360, 0, 0))
        self.day_period_neptune = self.neptune.hprInterval(0.67 * self.dayscale, (360, 0, 0))
        self.orbit_period_neptune.loop()  # 公转
        self.day_period_neptune.loop() 

    def increasePlanetSpeed(self):
        self.planet_speed_factor *= 1.5
        self.resetPlanetRotation()

    def decreasePlanetSpeed(self):
        self.planet_speed_factor /= 1.5
        self.resetPlanetRotation()


    def resetPlanetRotation(self):
        for interval in [
            self.day_period_mercury, self.orbit_period_mercury,
            self.day_period_venus, self.orbit_period_venus,
            self.day_period_earth, self.orbit_period_earth,
            self.day_period_mars, self.orbit_period_mars,
            self.day_period_jupiter, self.orbit_period_jupiter,
            self.day_period_saturn, self.orbit_period_saturn,
            self.day_period_uranus, self.orbit_period_uranus,
            self.day_period_neptune, self.orbit_period_neptune,
        ]:
            interval.pause()

        self.rotatePlanets(speed_factor=self.planet_speed_factor)



    def updatePlanets(self, task):
        dt = globalClock.getDt()
        speed = self.planet_speed_factor

        # Sun自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["sun_spin"] += spin_speed * dt * speed
        self.sun.setH(self.planet_angles["sun_spin"] % 360)

        # mercury自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["mercury_spin"] += spin_speed * dt * speed
        self.mercury.setH(self.planet_angles["mercury_spin"] % 360)

        # mercury公转
        orbit_speed = 360 / (87.9 * self.yearscale)
        self.planet_angles["mercury_orbit"] += orbit_speed * dt * speed
        self.orbit_root_mercury.setH(self.planet_angles["mercury_orbit"] % 360)

        # venus自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["venus_spin"] += spin_speed * dt * speed
        self.venus.setH(self.planet_angles["venus_spin"] % 360)

        # venus公转
        orbit_speed = 360 / (227 * self.yearscale)
        self.planet_angles["venus_orbit"] += orbit_speed * dt * speed
        self.orbit_root_venus.setH(self.planet_angles["venus_orbit"] % 360)


        # 地球自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["earth_spin"] += spin_speed * dt * speed
        self.earth.setH(self.planet_angles["earth_spin"] % 360)

        # 地球公转
        orbit_speed = 360 / (365.25 * self.yearscale)
        self.planet_angles["earth_orbit"] += orbit_speed * dt * speed
        self.orbit_root_earth.setH(self.planet_angles["earth_orbit"] % 360)

        # mars自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["mars_spin"] += spin_speed * dt * speed
        self.mars.setH(self.planet_angles["mars_spin"] % 360)

        # mars公转
        orbit_speed = 360 / (1.88 * 365.25 * self.yearscale)
        self.planet_angles["mars_orbit"] += orbit_speed * dt * speed
        self.orbit_root_mars.setH(self.planet_angles["mars_orbit"] % 360)

        # jupiter自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["jupiter_spin"] += spin_speed * dt * speed
        self.jupiter.setH(self.planet_angles["jupiter_spin"] % 360)

        # jupiter公转
        orbit_speed = 360 / (11.8 * 365.25 * self.yearscale)
        self.planet_angles["jupiter_orbit"] += orbit_speed * dt * speed
        self.orbit_root_jupiter.setH(self.planet_angles["jupiter_orbit"] % 360)

        # saturn自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["saturn_spin"] += spin_speed * dt * speed
        self.saturn.setH(self.planet_angles["saturn_spin"] % 360)

        # Saturn公转
        orbit_speed = 360 / (29.5 * 365.25 * self.yearscale)
        self.planet_angles["saturn_orbit"] += orbit_speed * dt * speed
        self.orbit_root_saturn.setH(self.planet_angles["saturn_orbit"] % 360)

        # uranus自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["uranus_spin"] += spin_speed * dt * speed
        self.uranus.setH(self.planet_angles["uranus_spin"] % 360)

        # uranus公转
        orbit_speed = 360 / (84 * 365.25 * self.yearscale)
        self.planet_angles["uranus_orbit"] += orbit_speed * dt * speed
        self.orbit_root_uranus.setH(self.planet_angles["uranus_orbit"] % 360)

        # neptune自转
        spin_speed = 360 / self.dayscale  # 度/秒
        self.planet_angles["neptune_spin"] += spin_speed * dt * speed
        self.neptune.setH(self.planet_angles["neptune_spin"] % 360)

        # neptune公转
        orbit_speed = 360 / (165 * 365.25 * self.yearscale)
        self.planet_angles["neptune_orbit"] += orbit_speed * dt * speed
        self.orbit_root_neptune.setH(self.planet_angles["neptune_orbit"] % 360)

    
        return Task.cont

    def increasePlanetSpeed(self):
        self.planet_speed_factor *= 3
        print(f"当前速度因子: {self.planet_speed_factor:.2f}")

    def decreasePlanetSpeed(self):
        self.planet_speed_factor /= 3
        print(f"当前速度因子: {self.planet_speed_factor:.2f}")

    def on_mouse_click(self):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())
            self.picker.traverse(self.render)

            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()
                planet_tag = pickedObj.findNetTag('planet')
                if not planet_tag.isEmpty():
                    print("Clicked on:", planet_tag.getTag('planet'))

app = World()
app.run()