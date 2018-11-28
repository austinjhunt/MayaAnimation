# Austin Hunt
# Project started on November 21, 2018
# Computing in the Arts 120: Animation and Virtual Worlds

"""
This is an action-filled animation of a classic Nicolas Cage-esque
car-helicopter chase in the middle of a city on a stormy night.

My objective with this project is to do as MUCH as I can
(or that I have time to do) with Python code:
object movements/rotations, camera aiming and dollying, physics simulations,
texture mapping, keyframing, and more. I don't want to use the Maya UI at all, since it
consistently crashes when the UI is used with crowded scenes.

This code, together with its home folder of images and object files,
is portable, functional, and self-contained. Its development
took between 30 and 40 hours (lots of trial and error modifications of
variables like accelerations, velocities, positions, rotations, etc.)
It can be run on both Mac OS and Windows. It requires no additional interface interactions within the Maya
application aside from pasting and executing the code.

"""

import pymel.core as pm  # use for poly modeling
import random  # use for random positioning, random velocities
import maya.cmds as cm
import platform  # use to determine current os, filepath structure is dependent on this


class FinalAnimation:
    def __init__(self, filePathToCitaFinal, os):
        self.filepath_to_citaFinal = filePathToCitaFinal
        self.os = os

    # NOTE: HELICOPTER MODEL AND AUDI MODEL FOUND AT TURBOSQUID.COM
    # I ONLY ASSIGNED NEW MATERIALS TO THEIR FACES
    # define a method to import your scaled .obj files!
    def getObjFiles(self):

        if self.os == "Mac":
            objFilePath = self.filepath_to_citaFinal + "/objFiles/"
        elif self.os == "Windows":
            objFilePath = self.filepath_to_citaFinal + "\\objFiles\\"

        fileType = "obj"

        files = cm.getFileList(folder=objFilePath, filespec='*.%s' % fileType)
        if len(files) == 0:
            cm.warning("No files found")
        else:
            for f in files:
                cm.file(objFilePath + f, i=True)

        if self.os == "Mac":
            mbFilePath = self.filepath_to_citaFinal + "/mbFiles/"  # want the mb for audi,heli,ramp
        elif self.os == "Windows":
            mbFilePath = self.filepath_to_citaFinal + "\\mbFiles\\"  # want the mb for audi,heli,ramp

        fileType = "mb"
        files = cm.getFileList(folder=mbFilePath, filespec='*.%s' % fileType)
        if len(files) == 0:
            cm.warning("No files found")
        else:
            for f in files:
                cm.file(mbFilePath + f, i=True)

    def centerAllPivots(self):

        allObjs = ['heli', 'raindrop', 'car', 'streetlight']
        for name in allObjs:
            pm.select(name)
            cm.xform(cp=True)
            # cm.makeIdentity(name,t=True,a=True)
            pm.move(name, 0, 0, 0, a=True)

    # define method to initialize all object positions (except for raindrops, that's handled by rainSimulation())
    def initialize_objects(self):
        # generateBuildings()
        pm.select('car')
        pm.move(0, 0, -1900, a=True)

        pm.select('heli')
        pm.move(0, 0, 0, a=True)
        pm.move(0, 400, -1950, a=True)

        # generate rows of streetlights along each side of road
        # road goes from -25 -> +25
        # so set street lightrows at -28, +28
        roadSides = [-28, 28]
        i = 1
        # first select streetlight and center it at origin
        pm.select('streetlight')
        pm.move(0, 0, 0, a=True)

        # create shader of type blinn because blinn extends class lambert
        lampmaterialName = "lampmaterial"  #
        lampMaterial = pm.nodetypes.Blinn(n=lampmaterialName)  # will be black metal
        # lamppost is metal -> reflective
        lampMaterial.setReflectivity(.8)
        # store each unique value of triple as r,g,b, set material color using them
        r, g, b = 0, 0, 0
        color = pm.datatypes.Color(r, g, b)
        lampMaterial.setColor(color)
        for side in roadSides:
            for z in range(-2000, 2000, 100):
                pm.instance('streetlight', n='light' + str(i))
                pm.select('light' + str(i))
                cm.hyperShade(assign=lampmaterialName)
                pm.move(side, 0, z)
                i += 1
        # after doing this delete the initial streetlight (imported to the origin)
        pm.select('streetlight')
        pm.delete()

        # set up ramp model i built
        pm.select('ramp')
        pm.move(0, 0, 1500)

    def animateCarAndHeli(self):
        heli = Helicopter()
        heli.animate()

        car = Car()
        car.animate()

    # method to create a simulation of (numRaindrops) falling raindrops
    def rainSimulation(self, numRaindrops):

        # first assign blue water-esque material to raindrop

        # create shader of type blinn because blinn extends class lambert
        materialName = "raindropmaterial"  # name each concrete material
        raindropmaterial = pm.nodetypes.Blinn(n=materialName)
        # concrete not reflective
        raindropmaterial.setReflectivity(.6)  # water is a bit reflective

        # store each unique value of triple as r,g,b, set material color using them
        r, g, b = 111, 185, 218
        color = pm.datatypes.Color(r, g, b)
        raindropmaterial.setColor(color)

        pm.select('raindrop')
        cm.hyperShade(assign=materialName)

        # init lists of x y z positions and  x, y, z velocities
        # each index position across all lists reps 1 particle
        # list to store ith object's x y z position
        xpos_list = []
        ypos_list = []
        zpos_list = []
        # lists to store ith object's x y z velocity (don't want just a vertical path )
        xvel_list = []
        yvel_list = []
        zvel_list = []
        # list to store object names raindrop1...raindropi...raindrop(numRaindrops)
        raindrop_list = []
        # frames per second constant
        FPS = 24
        # initialize the lists such that indices 0-(numRaindrops-1) represent n df particles
        for i in range(numRaindrops):
            # only care about area between the two rows of buildings (X)
            # want the drops to start at / around the height of the tallest buildings (500),
            # seen above in the generateBuildings method (Y)
            # only care about area along the road (Z)
            xpos, ypos, zpos = random.randint(-100, 100), random.randint(300, 600), random.randint(-1500, 4000)
            xvel, yvel, zvel = 0, 0, 0  # initially all velocities 0

            # uniquely name each instance so setKeyframe can be used with obj name, add the name to the raindrop_list
            objname = 'raindrop' + str(i + 1)
            raindrop_list.append(objname)

            # add x y z positions to respective lists
            xpos_list.append(xpos)
            ypos_list.append(ypos)
            zpos_list.append(zpos)

            # add x y z velocities to respective lists
            xvel_list.append(xvel)
            yvel_list.append(yvel)
            zvel_list.append(zvel)

            # create an instance of the raindrop I already modeled
            # pm.instance automatically creates 'raindrop1','raindrop2',etc. which is
            # why i used str(i+1) above to refer to these respective objects
            pm.instance('raindrop')

            # move that instance to its initial x y z position by indexing the lists for x y z position
            # where index i refers to the current object
            pm.move(xpos_list[i], ypos_list[i], zpos_list[i])

        # acceleration will be a constant, so define these outside of for loop
        # use x y and z so it looks like wind blowing
        xaccel, yaccel, zaccel = random.randint(-2, 2), -9.8, random.randint(-2, 2)

        # loop through object names, use enumerate to keep track of index position
        # (index position i is the identifier of unique object i across all lists)
        for i, objname in enumerate(raindrop_list):
            # start with framenumber 1 for each object
            frameNum = 1

            # keep updating x, y, z position AND velocity of current object and subsequently setting keyframe
            # until that object hits the ground!

            while ypos_list[i] > 0:
                # keyframe translate x
                cm.setKeyframe(objname, time=frameNum, attribute="translateX", value=xpos_list[i])
                xvel_list[i] = xvel_list[i] + xaccel * 1.0 / FPS
                xpos_list[i] = xpos_list[i] + xvel_list[i] * 1.0 / FPS

                # keyframe translate y
                cm.setKeyframe(objname, time=frameNum, attribute="translateY", value=ypos_list[i])
                yvel_list[i] = yvel_list[i] + yaccel * 1.0 / FPS
                ypos_list[i] = ypos_list[i] + yvel_list[i] * 1.0 / FPS

                # keyframe translate z
                cm.setKeyframe(objname, time=frameNum, attribute="translateZ", value=zpos_list[i])
                zvel_list[i] = zvel_list[i] + zaccel * 1.0 / FPS
                zpos_list[i] = zpos_list[i] + zvel_list[i] * 1.0 / FPS

                # go to next frame
                frameNum += 1
            # now delete original raindrop located at origin
        pm.select('raindrop')
        pm.delete()


# class for the road (texture mapping, plane creation)
class Road:
    def __init__(self, filePathToCitaFinal, width, length, os):
        self.filepath_to_citaFinal = filePathToCitaFinal
        self.width = width
        self.length = length
        self.os = os

    def generate(self):

        # Create a mesh (plane) with above dims
        pm.polyPlane(name='road', w=self.width, h=self.length)
        pm.move(0, .3, 0)

        # apply texture map using roadTexture image
        # create a shader
        shader = cm.shadingNode("blinn", asShader=True, n='roadTextureColor')
        # a file texture node
        file_node = cm.shadingNode("file", asTexture=True, n='roadTextureFile')  # "file" is node type
        # a shading group

        if self.os == "Mac":
            file = self.filepath_to_citaFinal + "/images/roadTexture.jpg"
        elif self.os == "Windows":
            file = self.filepath_to_citaFinal + "\\images\\roadTexture.jpg"

        shading_group = cm.sets(renderable=True, noSurfaceShader=True, empty=True)
        # connect shader to sg surface shader
        cm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
        # connect file texture node to shader's color
        cm.connectAttr('%s.outColor' % file_node, '%s.color' % shader)
        cm.setAttr('roadTextureFile.fileTextureName', file, type='string')
        cm.select('road')
        cm.hyperShade(a='roadTextureColor')


# class for the ground plane (texture mapping, plane creation)
class Ground:
    def __init__(self, filePathToCitaFinal, width, length, os):
        self.filepath_to_citaFinal = filePathToCitaFinal
        self.width = width
        self.length = length
        self.os = os

    def generate(self):
        # Create a mesh (plane) with above dims
        pm.polyPlane(name='ground', w=self.width, h=self.length)
        pm.move(0, -0.3, 0)
        pm.rotate('0deg', '0deg', '0deg')

        # apply texture map using ground image
        # create a shader
        shader = cm.shadingNode("blinn", asShader=True, n='groundTextureColor')
        # a file texture node
        file_node = cm.shadingNode("file", asTexture=True, n='groundTextureFile')  # "file" is node type
        # a shading group

        if self.os == "Mac":
            file = self.filepath_to_citaFinal + "/images/cityGround.jpg"
        elif self.os == "Windows":
            file = self.filepath_to_citaFinal + "\\images\\cityGround.jpg"

        shading_group = cm.sets(renderable=True, noSurfaceShader=True, empty=True)
        # connect shader to sg surface shader
        cm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
        # connect file texture node to shader's color
        cm.connectAttr('%s.outColor' % file_node, '%s.color' % shader)
        cm.setAttr('groundTextureFile.fileTextureName', file, type='string')
        cm.select('ground')
        cm.hyperShade(a='groundTextureColor')


# create this class to use its createFileTexture method within other classes
class Place2DTexture:

    def __init__(self, fileTextureName, p2dName):
        self.fileTextureName = fileTextureName
        self.p2dName = p2dName

    def createFileTexture(self, i, j):
        tex = pm.shadingNode('file', name=self.fileTextureName, asTexture=True, isColorManaged=True)
        if not pm.objExists(self.p2dName):
            pm.shadingNode('place2dTexture', name=self.p2dName, asUtility=True)
        p2d = pm.PyNode(self.p2dName)
        tex.filterType.set(0)
        pm.connectAttr(p2d.outUV, tex.uvCoord)
        pm.connectAttr(p2d.outUvFilterSize, tex.uvFilterSize)
        pm.connectAttr(p2d.vertexCameraOne, tex.vertexCameraOne)
        pm.connectAttr(p2d.vertexUvOne, tex.vertexUvOne)
        pm.connectAttr(p2d.vertexUvThree, tex.vertexUvThree)
        pm.connectAttr(p2d.vertexUvTwo, tex.vertexUvTwo)
        pm.connectAttr(p2d.coverage, tex.coverage)
        pm.connectAttr(p2d.mirrorU, tex.mirrorU)
        pm.connectAttr(p2d.mirrorV, tex.mirrorV)
        pm.connectAttr(p2d.noiseUV, tex.noiseUV)
        pm.connectAttr(p2d.offset, tex.offset)
        pm.connectAttr(p2d.repeatUV, tex.repeatUV)
        # need to set place2dtexture's repeatUV to higher value than 1
        # to prevent texture stretching
        pm.setAttr(p2d.repeatUV, (i, j))  # THIS WORKED!!! WOW I GUESSED HAHAHA
        pm.connectAttr(p2d.rotateFrame, tex.rotateFrame)
        pm.connectAttr(p2d.rotateUV, tex.rotateUV)
        pm.connectAttr(p2d.stagger, tex.stagger)
        pm.connectAttr(p2d.translateFrame, tex.translateFrame)
        pm.connectAttr(p2d.wrapU, tex.wrapU)
        pm.connectAttr(p2d.wrapV, tex.wrapV)
        return tex


# background class (texture mapping, plane creation)
class Background:
    def __init__(self, filePathToCitaFinal, width, height, os):
        self.filepath_to_citaFinal = filePathToCitaFinal
        self.width = width
        self.height = height
        self.os = os

    def generate(self):
        # create mesh (plane) with above dims
        pm.polyPlane(name='background', w=self.width, h=self.height)
        pm.move(-20, 280, -2050)
        pm.rotate('0deg', '90deg', '0deg')
        # apply texture map using lightning  image
        # create a shader
        shader = cm.shadingNode("blinn", asShader=True, n='backgroundTextureColor')
        cm.setAttr('{0}.specularColor'.format(shader), 0, 0, 0, type='double3')
        # a file texture node
        file_node = cm.shadingNode("file", asTexture=True, n='backgroundTextureFile')  # "file" is node type
        # a shading group
        if self.os == "Mac":
            file = self.filepath_to_citaFinal + "/images/lightningstormbackground.jpg"
        elif self.os == "Windows":
            file = self.filepath_to_citaFinal + "\\images\\lightningstormbackground.jpg"

        shading_group = cm.sets(renderable=True, noSurfaceShader=True, empty=True)
        # connect shader to sg surface shader
        cm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)
        # connect file texture node to shader's color
        cm.connectAttr('%s.outColor' % file_node, '%s.color' % shader)
        cm.setAttr('backgroundTextureFile.fileTextureName', file, type='string')
        cm.select('background')
        cm.hyperShade(a='backgroundTextureColor')


# world class, encapsulate the entire scene inside of a sphere
# make the inside material of the sphere a dark sky material

class World:

    def __init__(self, filePathToCitaFinal, os):
        self.filepath_to_citaFinal = filePathToCitaFinal
        self.os = os

    # I want to put the entire scene on the inside of a sphere to make the sky material continuous

    def generate(self):
        worldSphere = pm.polySphere(n='world', r=4000)
        pm.move(0, 0, 0)

        # since by default the inside of the object will be black due to single side lighting,
        # turn 2 sided lighting on
        pm.displaySurface(['world'], two=True)

        # now want to assign texture AND set repeat UV to prevent image stretching
        materialName = "world_material"
        worldMaterial = pm.nodetypes.Blinn(n=materialName)
        # use a brick material texture file
        # create p2d object of class defined above
        p2d = Place2DTexture("worldTextureFile", "worldp2d")
        file_node = p2d.createFileTexture(1, 3)
        # a shading group

        # get file name
        if self.os == "Mac":
            file = self.filepath_to_citaFinal + "/images/lightningstormbackgroundCrop.jpg"
        elif self.os == "Windows":
            file = self.filepath_to_citaFinal + "\\images\\lightningstormbackgroundCrop.jpg"

        # connect file texture node to shader's color
        pm.connectAttr('%s.outColor' % file_node, '%s.color' % worldMaterial)
        pm.setAttr('worldTextureFile.fileTextureName', file, type='string')
        specularColor = pm.datatypes.Color(0, 0, 0)
        worldMaterial.setSpecularColor(specularColor)  # don't want it to be shiny
        worldMaterial.setReflectivity(0)
        ambientColor = pm.datatypes.Color(0.57,0.57,0.57) # want it somewhat bright, try to blend with the 
        # already-positioned background plane
        worldMaterial.setAmbientColor(ambientColor)

        # assign to world
        pm.select('world')
        cm.hyperShade(assign=materialName)


# class to store all the buildings, building materials & whatnot
class City:

    def __init__(self, filePathToCitaFinal, os):
        self.filepath_to_citaFinal = filePathToCitaFinal
        self.os = os

    # method found at https://forums.autodesk.com/t5/maya-programming/how-to-create-a-file-node-place2dtexture-in-maya-sdk/td-p/6717342
    # trying to set repeat UV to 20 to keep brick texture from vertically stretching
    # need a place2dtexture node to do this

    # method to generate the building materials, output a list of them
    def generate_building_materials(self):
        building_materials_list = []  # init to empty

        # most buildings are concrete, brick or glass
        for el in ['concrete', 'brick', 'glass']:
            if el == 'concrete':

                # use off-white or grey
                # 3 varieties
                # 255-250-240 #floral white
                # 205-192-176 # antique white
                # 139-131-120 # darker-greyish-brown
                # store the above triples, create a concrete material for each
                concrete_triples = [[1, 0.98, .941], [.804, 0.753, .690], [.545, 0.514, .471]]
                for i, triple in enumerate(concrete_triples):
                    # create shader of type blinn because blinn extends class lambert
                    materialName = "building_material_concrete_" + str(i)  # name each concrete material
                    buildingMaterial = pm.nodetypes.Blinn(n=materialName)
                    # concrete not reflective
                    buildingMaterial.setReflectivity(0)

                    # store each unique value of triple as r,g,b, set material color using them
                    r, g, b = triple[0], triple[1], triple[2]
                    color = pm.datatypes.Color(r, g, b)
                    buildingMaterial.setColor(color)
                    building_materials_list.append(materialName)

            elif el == 'brick':
                # just need one blinn material
                # create shader of type blinn because blinn extends class lambert
                materialName = "building_material_brick"  # name each concrete material
                buildingMaterial = pm.nodetypes.Blinn(n=materialName)
                # use a brick material texture file
                p2d = Place2DTexture("brickTextureFile", "brickp2d")  # create p2d object of class defined above
                file_node = p2d.createFileTexture(20, 20)
                # a shading group

                if self.os == "Mac":
                    file = self.filepath_to_citaFinal + "/images/brickTexture.jpg"
                elif self.os == "Windows":
                    file = self.filepath_to_citaFinal + "\\images\\brickTexture.jpg"

                # connect file texture node to shader's color
                pm.connectAttr('%s.outColor' % file_node, '%s.color' % buildingMaterial)
                pm.setAttr('brickTextureFile.fileTextureName', file, type='string')
                specularColor = pm.datatypes.Color(0, 0, 0)
                buildingMaterial.setSpecularColor(specularColor)
                buildingMaterial.setReflectivity(0)

                building_materials_list.append(materialName)
                building_materials_list.append(materialName)  # double chances of brick,
            # nicer than plane white all over

            else:
                # glass
                # set color to black with white specular to mimic reflectiveness, little bit of transparency
                materialName = "building_material_glass"  # name each concrete material
                buildingMaterial = pm.nodetypes.Blinn(n=materialName)
                buildingMaterial.setTransparency(0.4)
                color = pm.datatypes.Color(0, 0, 0)
                buildingMaterial.setColor(color)
                specularColor = pm.datatypes.Color(1, 1, 1)
                buildingMaterial.setSpecularColor(specularColor)
                buildingMaterial.setReflectivity(.8)
                building_materials_list.append(materialName)
                building_materials_list.append(materialName)
                building_materials_list.append(materialName)

        # return list of materials
        # this will only be called once, we don't need many copies of same materials
        return building_materials_list

    # since the road width is 50 and depth is 2000 and it is centered at the origin, then start at
    # -1000z,-40x, go to 1000z, -40x (do the same for +40x) and make buildings that are at most 15 units wide

    def generateBuildings(self):
        # row of randomly sized buildings on left side and right side of 2000 long road
        building_materials_list = self.generate_building_materials()
        building_materials_list_length = len(building_materials_list)
        roadSides = [-600, -500, -400, -300, -200, -100, 100, 200, 300, 400, 500,
                     600]  # instead of just a row of buildings on each side,
        # have a grid of buildings on each side
        i = 0
        for x in roadSides:
            for z in range(-2000, 4000, 100):
                # 25 away from left side of road, let buildingx be max of 22
                depth, height, width = random.randint(50, 100), random.randint(100, 500), random.randint(50, 100)
                pm.polyCube(name="building" + str(i), depth=depth, height=height, width=width)
                pm.move(x, height / 2, z)

                # assign random color (materials) to each building
                # (just by choosing random index from list of random building materials )
                random_material_name = building_materials_list[random.randint(0, building_materials_list_length - 1)]
                cm.select('building' + str(i))
                cm.hyperShade(assign=random_material_name)
                i += 1


# class for the helicopter, storing positions/accels/vels as vars
# also contains method for animating it
class Helicopter:
    def __init__(self):

        # select all the heli elements
        # move them in z dir
        # keep moving in y z dir until y reaches height of 25
        self.heliposy = 400  # thats where it starts
        self.heliposz = -1950

        # we want the drop to be slower than the forward motion, so make z magnitude higher than y magnitude
        self.heliaccz = 8  # init accel z
        self.heliaccy = -7  # init accel y
        self.helively = -1.5  # init vel y
        self.helivelz = 410  # init vel z

        # init rotate of heli
        self.helirotatex = 20
        self.helirotatey = 0
        self.helirotatez = 0
        self.heliposx = 0  

    # method to animate heli, to be called in animate_chase()
    def animate(self):

        do_rotate = False  # when you reach height 200, set this to true to start rotation
        frameNum = 1  # init framenumber to 1
        FPS = 24  # frames per sec constant
        # while heliposy > 110:
        while self.heliposy > 110 and frameNum < 241:  # now that i know exactly when animation should end
            if self.heliposy <= 200:
                do_rotate = True
                if self.helirotatey <= -180:  # stop rotating after complete 180
                    do_rotate = False
            cm.setKeyframe('heli', time=frameNum, attribute="rotateX", value=self.helirotatex)
            cm.setKeyframe('heli', time=frameNum, attribute="rotateY", value=self.helirotatey)
            if do_rotate:
                self.helirotatey = self.helirotatey + (-112) * 1.0 / FPS
            # keyframe translate y
            cm.setKeyframe('heli', time=frameNum, attribute="translateY", value=self.heliposy)
            self.helively = self.helively + self.heliaccy * 1.0 / FPS
            self.heliposy = self.heliposy + self.helively * 1.0 / FPS
            # keyframe translate z
            cm.setKeyframe('heli', time=frameNum, attribute="translateZ", value=self.heliposz)
            self.helivelz = self.helivelz + self.heliaccz * 1.0 / FPS
            self.heliposz = self.heliposz + self.helivelz * 1.0 / FPS
            # go to next frame
            frameNum += 1

        # dont want to just immediately stop in the air, want to simulate a hovering effect (up,down,up,down)
        if self.heliposy <= 110:
            currentlymoving = 'down'  # initially going down
            # hover until car collides, approx 80 frames?
            for i in range(18):  # down up 30 times
                # move down
                if currentlymoving == 'down':
                    print('moving down')
                    self.heliaccy = 200  # push up on move down
                else:
                    self.heliaccy = -1  # push down on move up
                # keyframe translate y
                print('frameNum = ', frameNum, 'heliposy =', self.heliposy, 'heliaccely =', self.heliaccy, 'helively=',
                      self.helively)
                cm.setKeyframe('heli', time=frameNum, attribute="translateY", value=self.heliposy)
                self.helively = self.helively + self.heliaccy * 1.0 / FPS
                self.heliposy = self.heliposy + self.helively * 1.0 / FPS
                if self.helively > 0:
                    currentlymoving = 'up'
                elif self.helively <= 0:
                    currentlymoving = 'down'
                frameNum += 1

        # dodge to right!
        keep_dodging = True  # keep the dodge sequence going while true
        level_out = False  # use this to determine when to level out the heli
        start_dodge_framenum = frameNum  # what is the current framenum
        
        while keep_dodging:

            # set keyframe on each var that should change in dodge sequence
            cm.setKeyframe('heli', time=frameNum, attribute="rotateZ", value=self.helirotatez)
            cm.setKeyframe('heli', time=frameNum, attribute="rotateX", value=self.helirotatex)
            cm.setKeyframe('heli', time=frameNum, attribute="translateZ", value=self.heliposz)
            cm.setKeyframe('heli', time=frameNum, attribute="translateY", value=self.heliposy)
            cm.setKeyframe('heli', time=frameNum, attribute="translateX", value=self.heliposx)
            if not level_out:
                print('inside not level out!')
                # rotate along z axis to right
                self.helirotatez = self.helirotatez + (-100) * 1.0 / FPS  # 200 picked through t&e
                # tilt back
                self.helirotatex = self.helirotatex + (-100) * 1.0 / FPS  # 200 picked through t&e

                # move up a bit (use a constant to rep velocity, no need for acceleration here)
                self.heliposy = self.heliposy + (60) * 1.0 / FPS

                # move back, use same values already stored
                self.helivelz = self.helivelz + self.heliaccz * 1.0 / FPS
                self.heliposz = self.heliposz + self.helivelz * 1.0 / FPS

                # move right
                self.heliposx = self.heliposx + (60) * 1.0 / FPS

                if self.heliposz >= 2045 and self.heliposx >= 25:
                    level_out = True


            else:  # level out now true, so level back out (i.e. only rotations)
                while self.helirotatez < 0:  # leveled, stop dodging
                    cm.setKeyframe('heli', time=frameNum, attribute="rotateZ", value=self.helirotatez)
                    cm.setKeyframe('heli', time=frameNum, attribute="rotateX", value=self.helirotatex)
                    # rotate along z axis to left (negative)
                    self.helirotatez = self.helirotatez + (40) * 1.0 / FPS  # 90 picked through t&e
                    # tilt back (negative x)
                    self.helirotatex = self.helirotatex + (40) * 1.0 / FPS  # 90 picked through t&e

                    print("STOP DODGING")
                    frameNum += 1
                keep_dodging = False  # done

            frameNum += 1


# class for the car, storing positions/accels/vels as vars
# also contains method for animating it
class Car:
    def __init__(self):

        # init positions, velocities, accels
        self.carposx, self.carposy, self.carposz = 0, 0, -1900
        self.carvelx, self.carvely, self.carvelz = 0, 150, 360  # use 360 to keep car behind heli along z axis
        self.caraccelx, self.gravityaccel, self.caraccelz = 0, -9.8, 5  # want car to accel but not faster than heli
        # use y accel/vel when car is getting that airtime #skillz

        self.car_rotatex = 0  # init, not rotated

    # method to animate car, to be called in animate_chase()
    def animate(self):
        # re-init frame number to 1
        frameNum = 1
        FPS = 24  # frames per sec constant

        # car drives along road in straight line under heli as heli moves forward and descends (approaching car)
        do_rotate_backward = False  # use this to determine rotation along ramp
        do_rotate_forward = False  # use this to determine nosedive rotation after ramp

        # while carposz < 1965: # just before collision with heli
        while self.carposz < 4000:
            # keyframe translate z
            if self.carposz > 1470 and self.carposz < 1480:
                do_rotate_backward = True
            else:
                do_rotate_backward = False
            cm.setKeyframe('car', time=frameNum, attribute="rotateX", value=self.car_rotatex)
            if do_rotate_backward:
                self.car_rotatex = self.car_rotatex + (-410) * 1.0 / FPS  # rotate backward, -410 found thru T&E
            # move up along ramp
            if self.carposz > 1470 and self.carposz < 1480:
                cm.setKeyframe('car', time=frameNum, attribute="translateY", value=self.carposy)
                self.carvely = self.carvely + self.gravityaccel * 1.0 / FPS
                self.carposy = self.carposy + self.carvely * 1.0 / FPS
            # left ramp,
            # amplify acceleration after leaving ramp to make car fall faster, also begin partial nosedive
            if self.carposz >= 1480 and self.carposy >= 0:
                cm.setKeyframe('car', time=frameNum, attribute="translateY", value=self.carposy)
                self.carvely = self.carvely + (
                            self.gravityaccel * 10 * .9) * 1.0 / FPS  # amplify downward acceleration due to gravity (not strong enough otherwise)
                self.carposy = self.carposy + self.carvely * 1.0 / FPS
                do_rotate_forward = True  # nosedive,level out
                if (
                        self.carposy > 0 and self.carposy < 5):  # dont wanna just hover due to a vertical offset in kinematic equations
                    # if it has reached this height then just set it to ground level
                    self.carposy = 0

            if do_rotate_forward:
                self.car_rotatex = self.car_rotatex + (8) * 1.0 / FPS

            # always moving forward
            cm.setKeyframe('car', time=frameNum, attribute="translateZ", value=self.carposz)
            self.carvelz = self.carvelz + self.caraccelz * 1.0 / FPS
            self.carposz = self.carposz + self.carvelz * 1.0 / FPS
            if self.carposz > 2725 and self.carposz < 2745:  # reached the ground
                do_rotate_forward = False
                self.car_rotatex = 0
            # increment frame number
            frameNum += 1


# many cameras involved, create one class to create and animate
# each of the cams
class CameraTeam:

    def __init__(self, filePathToCitaFinal, os):
        self.filepath_to_citaFinal = filePathToCitaFinal
        self.os = os

    def addSavedMotionPathCamera(self):
        # saved a camera with motion path as an ma file
        if self.os == "Mac":
            maFilePath = self.filepath_to_citaFinal + "/maFiles/"
        elif self.os == "Windows":
            maFilePath = self.filepath_to_citaFinal + "\\maFiles\\"

        fileType = "ma"
        files = cm.getFileList(folder=maFilePath, filespec='*.%s' % fileType)
        if len(files) == 0:
            cm.warning("No files found")
        else:
            for f in files:
                cm.file(maFilePath + f, i=True)
        pm.group('curve1', 'camera1moveup', n='cam1group')  # group cam with its motion path
        pm.select('cam1group')
        cm.xform(cp=True)
        # cm.makeIdentity(name,t=True,a=True)
        pm.move('cam1group', 0, 0, 0, a=True)
        # includes upward motion, angling downward as it moves up
        pm.move(0, 5, -1700)

    def addCarCamLeft(self):
        # add another cam on car left
        car_cam_left = pm.nodetypes.Camera(n='car_cam_left')

        car_cam_left.setMotionBlurred(True)
        pm.select('car_cam_left1')
        pm.move(-8, 2, -1900, absolute=True)
        # pm.rotate('180deg','0deg','0deg')
        centerOfInterest = pm.datatypes.Point(-8, 2, 1500)

        car_cam_left.setCenterOfInterestPoint(centerOfInterest)

        # move left cam alongside the car (at same speed/acceleration of car)
        carcamleft_velz = 360  # car's init z vel is 360, so copy that for both mounted cams
        carcamleft_accelz = 5  # car init z accel is 5, so copy that for both mounted cams

        carcamleft_posz = -1900  # z position
        carcamleft_posy = 2  # y position

        carcamleft_vely = 150  # car's init z vel is 360, so copy that for both mounted cams
        gravityaccel = -9.8

        # copy the while loop used for car motion, change variables
        frameNum = 1
        FPS = 24

        # stop while car still moving
        while carcamleft_posz < 2950:
            # keyframe posz
            cm.setKeyframe('car_cam_left1', time=frameNum, attribute="translateZ", value=carcamleft_posz)

            # begin vertical movement along ramp
            if carcamleft_posz > 1470 and carcamleft_posz < 1480:
                cm.setKeyframe('car_cam_left1', time=frameNum, attribute="translateY", value=carcamleft_posy)
                carcamleft_vely = carcamleft_vely + gravityaccel * 1.0 / FPS
                carcamleft_posy = carcamleft_posy + carcamleft_vely * 1.0 / FPS

            # keyframe posz
            cm.setKeyframe('car_cam_left1', time=frameNum, attribute="translateZ", value=carcamleft_posz)

            # left ramp, amplify accel
            if carcamleft_posz >= 1480 and carcamleft_posy > 0:
                cm.setKeyframe('car_cam_left1', time=frameNum, attribute="translateY", value=carcamleft_posy)
                # amplify downward acceleration due to gravity (not strong enough otherwise)
                carcamleft_vely = (carcamleft_vely + (gravityaccel * 10) * 1.0 / FPS)
                carcamleft_posy = carcamleft_posy + carcamleft_vely * 1.0 / FPS

                # also slow down the cameras velz so that car overtakes them in the air
                carcamleft_velz = carcamleft_velz + (0.1 * carcamleft_accelz) * 1.0 / FPS

            else:  # dont slow down cams yet
                carcamleft_velz = carcamleft_velz + carcamleft_accelz * 1.0 / FPS

            carcamleft_posz = carcamleft_posz + carcamleft_velz * 1.0 / FPS
            frameNum += 1

    def addCarCamRight(self):
        # "mount" a camera to car's right side

        car_cam_right = pm.nodetypes.Camera(n='car_cam_right')

        car_cam_right.setMotionBlurred(True)
        pm.select('car_cam_right1')
        pm.move(8, 2, -1900, absolute=True)
        centerOfInterest = pm.datatypes.Point(8, 2, 1500)
        car_cam_right.setCenterOfInterestPoint(centerOfInterest)

        # move both of these cams alongside the car (at same speed/acceleration of car)
        carcamright_velz = 360  # car's init z vel is 360, so copy that for both mounted cams
        carcamright_accelz = 5  # car init z accel is 5, so copy that for both mounted cams

        carcamright_posz = -1900  # z position
        carcamright_posy = 2  # y position

        carcamright_vely = 150  # car's init z vel is 360, so copy that for both mounted cams
        gravityaccel = -9.8

        # copy the while loop used for car motion, change variables
        frameNum = 1
        FPS = 24

        # stop while car still moving
        while carcamright_posz < 2950:
            # keyframe posz
            cm.setKeyframe('car_cam_right1', time=frameNum, attribute="translateZ", value=carcamright_posz)

            # begin vertical movement along ramp
            if carcamright_posz > 1470 and carcamright_posz < 1480:
                cm.setKeyframe('car_cam_right1', time=frameNum, attribute="translateY", value=carcamright_posy)
                carcamright_vely = carcamright_vely + gravityaccel * 1.0 / FPS
                carcamright_posy = carcamright_posy + carcamright_vely * 1.0 / FPS

            # key frame posz
            cm.setKeyframe('car_cam_right1', time=frameNum, attribute="translateZ", value=carcamright_posz)

            # left ramp, amplify accel
            if carcamright_posz >= 1480 and carcamright_posy > 0:
                cm.setKeyframe('car_cam_right1', time=frameNum, attribute="translateY", value=carcamright_posy)
                # amplify downward acceleration due to gravity (not strong enough otherwise)
                carcamright_vely = (carcamright_vely + (gravityaccel * 10) * 1.0 / FPS)
                carcamright_posy = carcamright_posy + carcamright_vely * 1.0 / FPS

                # also slow down the cameras velz so that car overtakes them in the air
                carcamright_velz = carcamright_velz + (0.1 * carcamright_accelz) * 1.0 / FPS

            else:  # dont slow down cams yet
                carcamright_velz = carcamright_velz + carcamright_accelz * 1.0 / FPS

            carcamright_posz = carcamright_posz + carcamright_velz * 1.0 / FPS
            frameNum += 1

    # add cam inside heli looking out (front window)
    def addHeliInsideCam(self):

        # add a cam to side of heli AND inside heli (1 = inside, 2 = top)

        cam_heli1 = pm.nodetypes.Camera(n='cam_heli_inside')

        cam_heli1.setMotionBlurred(True)

        # cam inside heli
        # for some reason it appends a 1 even though it's the only one with this name
        pm.select('cam_heli_inside1')
        pm.move(0, 394, -1929)

        cam_heli1posy = 394  # thats where it starts
        cam_heli1posz = -1929
        # we want the drop to be slower than the forward motion, so make z magnitude higher than y magnitude
        cam_heli1accz = 8 # init accel z
        cam_heli1accy = -7  # init accel y
        cam_heli1vely = -1.5  # init vel y
        cam_heli1velz = 410  # init vel z

        # init rotate of cam1
        cam_heli1rotatex, cam_heli1rotatey, cam_heli1rotatez = -20, 180, 0

        do_rotate = False  # when you reach height 200, set this to true to start rotation
        frameNum = 1  # init framenumber to 1
        FPS = 24  # frames per sec constant

        # CAM 1 stuff
        while cam_heli1posy > 110:
            # start rotating when inside cam drops to 200
            if cam_heli1posy <= 200:
                do_rotate = True
                if cam_heli1rotatey <= -180:  # stop rotating after complete 180
                    do_rotate = False
                # set keyframe on cam1 rotations
            cm.setKeyframe('cam_heli_inside1', time=frameNum, attribute="rotateX", value=cam_heli1rotatex)
            cm.setKeyframe('cam_heli_inside1', time=frameNum, attribute="rotateY", value=cam_heli1rotatey)
            if do_rotate:
                cam_heli1rotatey = cam_heli1rotatey + (-112) * 1.0 / FPS

            # keyframe translate y cam1
            cm.setKeyframe('cam_heli_inside1', time=frameNum, attribute="translateY", value=cam_heli1posy)
            cam_heli1vely = cam_heli1vely + cam_heli1accy * 1.0 / FPS
            cam_heli1posy = cam_heli1posy + cam_heli1vely * 1.0 / FPS
            # keyframe translate z cam1
            cm.setKeyframe('cam_heli_inside1', time=frameNum, attribute="translateZ", value=cam_heli1posz)
            cam_heli1velz = cam_heli1velz + cam_heli1accz * 1.0 / FPS
            cam_heli1posz = cam_heli1posz + cam_heli1velz * 1.0 / FPS

            # go to next frame
            frameNum += 1

        # continue moving back, left, rotate right
        cam_heli1accx = -7
        cam_heli1velx = -300
        cam_heli1posx = 0

        # slow down z vel
        cam_heli1velz = 0.8 * cam_heli1velz
        print('just updated cam1 inside vel z to ', cam_heli1velz)
        for i in range(5):  # another < 1 seconds
            cm.setKeyframe('cam_heli_inside1', time=frameNum, attribute="translateZ", value=cam_heli1posz)
            cam_heli1velz = cam_heli1velz + cam_heli1accz * 1.0 / FPS
            cam_heli1posz = cam_heli1posz + (0.5 * cam_heli1velz) * 1.0 / FPS

            cm.setKeyframe('cam_heli_inside1', time=frameNum, attribute="translateX", value=cam_heli1posx)
            cam_heli1velx = cam_heli1velx + cam_heli1accx * 1.0 / FPS
            cam_heli1posx = cam_heli1posx + cam_heli1velx * 1.0 / FPS

            cm.setKeyframe('cam_heli_inside1', time=frameNum, attribute="rotateY", value=cam_heli1rotatey)
            cam_heli1rotatey = cam_heli1rotatey + (-160) * 1.0 / FPS

            frameNum += 1

    # add cam to side of heli

    def addHeliSideCam(self):

        # add a cam to side of heli AND inside heli (1 = inside, 2 = top)

        cam_heli2 = pm.nodetypes.Camera(n='cam_heli_side')

        cam_heli2.setMotionBlurred(True)

        # camera on side angled toward heli
        pm.select('cam_heli_side1')
        pm.move(23, 413, -1964)

        cam_heli2posy = 413  # thats where it starts
        cam_heli2posz = -1964
        # we want the drop to be slower than the forward motion, so make z magnitude higher than y magnitude
        cam_heli2accz = 8  # init accel z
        cam_heli2accy = -7  # init accel y
        cam_heli2vely = -1.5  # init vel y
        cam_heli2velz = 410  # init vel z

        # init rotate of cam2
        cam_heli2rotatex, cam_heli2rotatey, cam_heli2rotatez = -51, 166, -17

        do_rotate = False  # when you reach height 200, set this to true to start rotation
        frameNum = 1  # init framenumber to 1
        FPS = 24  # frames per sec constant

        cam2_pan_around = False  # when true, pan around heli
        cam2_pan_around_done = False  # self explanatory, when is it done
        cam2_begin_descent = False  # after it's done, set to true to begin drop to ground slowly

        # first stage: move forward, descend slightly
        while cam_heli2posz < -1500:
            # keep moving cam heli2 along road
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="translateZ", value=cam_heli2posz)
            cam_heli2velz = cam_heli2velz + cam_heli2accz * 1.0 / FPS
            cam_heli2posz = cam_heli2posz + cam_heli2velz * 1.0 / FPS

            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="translateY", value=cam_heli2posy)
            # if cam heli2 has not reached the ground, keep descending
            cam_heli2vely = cam_heli2vely + cam_heli2accy * 1.0 / FPS
            cam_heli2posy = cam_heli2posy + cam_heli2vely * 1.0 / FPS

            # not changing yet

            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="rotateX", value=cam_heli2rotatex)
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="rotateY", value=cam_heli2rotatey)

            frameNum += 1

        # now, second stage, speed in front of heli and #lookbackatit

        while cam_heli2rotatex > -30 or cam_heli2rotatey > 10:
            # print('setting keyframe at rotate x, y, frameNum:', cam_heli2rotatex,cam_heli2rotatey,frameNumCopy)
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="rotateX", value=cam_heli2rotatex)
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="rotateY", value=cam_heli2rotatey)
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="translateZ", value=cam_heli2posz)
            cam_heli2posz += 460 * 1.0 / FPS
            cam_heli2rotatey += (-100) * 1.0 / FPS
            cam_heli2rotatex += (-25) * 1.0 / FPS
            frameNum += 1

        # end 2nd stage

        # stage 3, keep moving along road, descend to ground

        while cam_heli2posy > 15:  # while it hasnt hit the ground
            # key frame those vals to change
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="translateY", value=cam_heli2posy)
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="translateZ", value=cam_heli2posz)
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="rotateX", value=cam_heli2rotatex)

            # change the vals
            # keep moving along road
            cam_heli2posz += cam_heli2velz * 1.0 / FPS
            # rotateslightly up
            cam_heli2rotatex += (12) * 1.0 / FPS
            # move down
            # current cam_heli2accy = -7
            # current cam_heli2vely = -1.5
            cam_heli2vely = cam_heli2vely + (-10) * 1.0 / FPS
            cam_heli2posy = cam_heli2posy + cam_heli2vely * 1.0 / FPS

            frameNum += 1

        # stage 4, move backward along road
        while cam_heli2posz < 3990:
            cm.setKeyframe('cam_heli_side1', time=frameNum, attribute="translateZ", value=cam_heli2posz)

            cam_heli2posz += 460 * 1.0 / FPS

            frameNum += 1 

        # we want to make this a cinematic experience, so let's bring in the cameras

    # NOTE: DISCOVERED THAT IF YOU ADD OBJECTS AFTER YOU ADD A CAMERA (EVEN IF YOU SPECIFICALLY POSITIONED
    # THAT CAMERA), THE CAMERA WILL AUTOLOCK ONTO LAST OBJECT ADDED)
    # SO, ADD CAMERAS AFTER EVERYTHING ELSE HAS BEEN ADDED!
    def addAllCameras(self):
        self.addSavedMotionPathCamera()
        self.addCarCamLeft()
        self.addCarCamRight()
        self.addHeliInsideCam()
        self.addHeliSideCam()




# YOU DEFINE THE filepath_to_citaFinal
# it should be in format 'somedirectory/someotherdirectory/someparentdirectory/citaFinal'
# where someparentdirectory/ is the parent folder of citaFinal
def main():
    os = platform.system()  # get the os, filepaths are formatted differently for Mac OS and Windows
    # simplify
    if "Darwin" in os:
        os = "Mac"
        filepath_to_citaFinal = "Users/austinhunt/Desktop/citaFinal"
    elif "Windows" in os:
        os = "Windows"
        filepath_to_citaFinal = "C:\\Users\\huntaj\\Desktop\\citaFinal"  # copy your filepath here, this is an example

    # instantiate road
    road = Road(filepath_to_citaFinal, 50, 8000, os)
    road.generate()

    # instantiate ground
    ground = Ground(filepath_to_citaFinal, 1500, 8000, os)
    ground.generate()

    # instantiate background
    background = Background(filepath_to_citaFinal, 1200, 800, os)
    background.generate()

    #instantiate world
    world = World(filepath_to_citaFinal,os)
    world.generate()

    city = City(filepath_to_citaFinal,os)
    city.generateBuildings()

    animation = FinalAnimation(filepath_to_citaFinal,os)
    animation.getObjFiles()
    animation.centerAllPivots()
    animation.initialize_objects()
    animation.animateCarAndHeli()
    animation.rainSimulation(100)

    camTeam = CameraTeam(filepath_to_citaFinal, os)
    camTeam.addAllCameras() # do this last to prevent cams from autolocking on newly added objects

main()