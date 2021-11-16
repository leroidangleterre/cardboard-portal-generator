import bpy
import random
import math
from mathutils import Euler

scene = bpy.context.scene

placementStartFrame = 160
placementMiddleFrame = 200
placementEndFrame = 260
maxTimeShift = 30


openingStartFrame = 350
openingEndFrame = 400

# Dimensions of the portal, in number of columns and row apart from the center ones.
portalWidth = 12
portalHeight = 7


nbPostits = (2*portalWidth + 1)*(2*portalHeight + 1)


savedKeyframes = []


def saveAllKeyframesEmtpyPortal():
    savedKeyFrames = []
    curves = emptyPortal.animation_data.action.fcurves
    
    for c in curves:
        # print("c: " + str(c) + ", data_path: " + str(c.data_path))
        keyframeList = c.keyframe_points
        # print("        keyframe_points: " + str(keyframeList))
        # print("        index: " + str(c.array_index))
        
        for point in keyframeList:
            # print("             frame: " + str(point.co[0]))
            # print("             value: " + str(point.co[1]))
            # print("                 type : " + str(point.type))
            # print("                 id_data: " + str(point.id_data.name_full))
            
            data_path = c.data_path # i.e. "location"
            index = c.array_index   # i.e. "0" to "2" for location[0] to location [2] (x to z)
            frame = point.co[0]     # frame in the timeline
            value = point.co[1]     # value of the parameter at that frame
            
            
            print("saving at Frame " + str(frame) + ", " + str(data_path) + "[" + str(index) + "] = " + str(value) + ";")
            
            keyframeToBeSaved = [frame, data_path, index, value]
            savedKeyframes.append(keyframeToBeSaved)

def loadAllKeyframes():
    if savedKeyframes is not None:
        for savedKeyframe in savedKeyframes:
            print("Loading frame: " + str(savedKeyframe[0]) + ", data_path: " + str(savedKeyframe[1]) + ", index: " + str(savedKeyframe[2]) + ", value: " + str(savedKeyframe[3]))

            frame = savedKeyframe[0]
            data_path = savedKeyframe[1]
            index = savedKeyframe[2]
            value = savedKeyframe[3]

            if data_path == "location":
                emptyPortal.location[index] = value
                print("value: " + str(value))
                emptyPortal.keyframe_insert(data_path="location", frame=savedKeyframe[0], index = index) #, value = savedKeyframe[3])
                print("Setting keyframe location at frame " + str(savedKeyframe[0]))
            elif data_path == "rotation_euler":
                emptyPortal.rotation_euler[index] = value
                emptyPortal.keyframe_insert(data_path=str(savedKeyframe[1]), frame=savedKeyframe[0], index = index) #, value = savedKeyframe[3])





# Remove keyframes for Empty.Portal and set its rotation to (0, 0, 0)
# Delete portal animation and keep a backup.
emptyPortal = scene.objects["Empty.Portal"]
saveAllKeyframesEmtpyPortal()
emptyPortal.animation_data_clear()
emptyPortal.rotation_euler = Euler((0, 0, 0), 'XYZ')
emptyPortal.location = (0, 0, 0)



# Delete older clones
bpy.data.scenes["Scene"].frame_current = placementEndFrame
emptyPortalChildren = []
for ob in bpy.data.objects:
    if ob.parent == emptyPortal:
        emptyPortalChildren.append(ob)
        print(str(ob) + " added.")
for object in emptyPortalChildren: #scene.objects:
    if object.name.startswith("clone"):
        
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        
        # Delete that object.
        bpy.data.objects[object.name].select_set(True)
        bpy.ops.object.delete()



# Return true when the tile is at the border of the ellipse, i.e. when at least one of its neighbors is outside.
def is_border(line, column):
    if not(is_in_ellipse(line, column)):
        return false
    # Find at least one neighbor outside:
    for i in range(-1, 2):
        for j in range(-1, 2):
            if not(is_in_ellipse(line+i, column+j)):
                return True
    return False


# Return true when the tile is in the ellipse, including on its border.
def is_in_ellipse(line, column):
    xFinal = column*postitSize
    yFinal = line*postitSize
    xTest = xFinal/(2*portalWidth+1)
    yTest = yFinal/(2*portalHeight+1)
    return xTest*xTest + yTest*yTest <= 1


def getAllInitPlanes():
    planes = []
    for obj in bpy.data.objects:
        if obj.name.startswith("Plane."):
            planes.append(obj)
    return planes

postitIndex = 0
disappearingTiles = []
plane000 = scene.objects["Plane.000"]
plane000.animation_data_clear()

# Create new postits
for line in range(-portalHeight, portalHeight+1):
    print("line: " + str(line))
    for column in range(-portalWidth, portalWidth+1):
        
        postitSize = plane000.dimensions[0]
        
        # Create only tiles that are inside the ellipse
        if is_in_ellipse(line, column):
            xFinal = column*postitSize
            yFinal = line*postitSize
            zFinal = 0.0
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = plane000
            plane000.select_set(True)
            
            # Duplicate the tile
            bpy.ops.object.duplicate()
            activeTile = bpy.context.view_layer.objects.active
            
            # Set tile name
            activeTile.name = "clone"
            
            # Set tile origin
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
            
            # Movement, first keyframe
            z = 2 * postitIndex / nbPostits
            bpy.ops.transform.transform(mode='TRANSLATION', value=(0.0, 0.0, z, 0.0))
            activeTile.keyframe_insert(data_path="location", frame=placementStartFrame)
            activeTile.keyframe_insert(data_path="rotation_euler", frame=placementStartFrame)
            
            # Movement, middle keyframe
            z = 5
            bpy.ops.transform.transform(mode='TRANSLATION', value=(0.0, 0.0, z, 0.0))
            activeTile.keyframe_insert(data_path="location", frame=placementMiddleFrame)

            # Movement, last keyframe; the last key is randomly shifted in time.
            # Location
            radius = 5
            timeshift = random.randint(-maxTimeShift, maxTimeShift)
            activeTile.location = (xFinal, yFinal, zFinal)
            activeTile.keyframe_insert(data_path="location", frame=placementEndFrame+timeshift )
            
            # Rotation of random quarter turns around Z-axis
            rotation_angle_z = random.randint(0, 3) * math.pi/2
            bpy.ops.transform.rotate(value=rotation_angle_z, orient_axis='Z')
            activeTile.keyframe_insert(data_path="rotation_euler", frame=placementEndFrame+timeshift)
            
            # Visibility and renderability
            activeTile.hide_render = True
            activeTile.hide_viewport = True
            activeTile.keyframe_insert(data_path="hide_render", frame=placementStartFrame-1)
            activeTile.keyframe_insert(data_path="hide_viewport", frame=placementStartFrame-1)
            activeTile.hide_render = False
            activeTile.hide_viewport = False
            activeTile.keyframe_insert(data_path="hide_render", frame=placementStartFrame)
            activeTile.keyframe_insert(data_path="hide_viewport", frame=placementStartFrame)
            postitIndex = postitIndex + 1
            if not(is_border(line, column)):
                disappearingTiles.append(bpy.context.active_object) 


for obj in bpy.data.objects:
    
    if obj.name.startswith("Plane."):
        disappearingTiles.append(obj)

for obj in disappearingTiles:
    # Make the tile disappear when the portal opens
    obj.scale = (1, 1, 1)
    obj.keyframe_insert(data_path="scale", frame=openingStartFrame)
    obj.scale = (0, 0, 0)
    obj.keyframe_insert(data_path="scale", frame=openingEndFrame)


loadAllKeyframes()