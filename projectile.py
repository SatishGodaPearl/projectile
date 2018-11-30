"""
Projectile
Copyright (C) 2018 Nathan Craddock

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

bl_info = {
    "name": "Projectile",
    "author": "Nathan Craddock",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "",
    "description": "Set initial velocities for rigid body physics",
    "tracker_url": "",
    "category": "Object"
}

import bpy
from bpy.types import Header, Menu, Panel
import gpu
from gpu_extras.batch import batch_for_shader
import mathutils

import math

# Kinematic Equation to find displacement over time
def kinematic_displacement(initial, velocity, time):
    frame_rate = bpy.context.scene.render.fps
    gravity = bpy.context.scene.gravity
    
    dt = (time * 1.0) / frame_rate
    ds = mathutils.Vector((0.0, 0.0, 0.0))
        
    ds.x = initial.x + (velocity.x * dt) + (0.5 * gravity.x * math.pow(dt, 2))
    ds.y = initial.y + (velocity.y * dt) + (0.5 * gravity.y * math.pow(dt, 2))
    ds.z = initial.z + (velocity.z * dt) + (0.5 * gravity.z * math.pow(dt, 2))
    
    return ds

# Functions for draw handlers
def draw_trajectory():
    object = bpy.context.object
    draw = object.projectile_draw_trajectories
    
    coordinates = []
    
    # Generate coordinates
    v = kinematic_displacement(object.projectile_props.s, object.projectile_props.v, 0)
    coord = (v.x, v.y, v.z)
    coordinates.append(coord)
    
    for frame in range(1, bpy.context.scene.frame_end):
        v = kinematic_displacement(object.projectile_props.s, object.projectile_props.v, frame)
        coord = (v.x, v.y, v.z)
        coordinates.append(coord)
        coordinates.append(coord)
        
    v = kinematic_displacement(object.projectile_props.s, object.projectile_props.v, bpy.context.scene.frame_end)
    coord = (v.x, v.y, v.z)
    coordinates.append(coord)
    
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos" : coordinates})
    
    shader.bind()
    shader.uniform_float("color", (1, 1, 1, 1))
    
    # Only draw if 
    if draw and object.select_get() and object.projectile:
        batch.draw(shader)


class PHYSICS_OT_projectile_add(bpy.types.Operator):
    bl_idname = "rigidbody.projectile_add_object"
    bl_label = "Add Object"
    bl_description = "Set selected object as a projectile"
    
    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.type == 'MESH'
        
    def execute(self, context):
        # Make sure it is a rigid body
        if context.object.rigid_body is None:
            bpy.ops.rigidbody.objects_add()
            
        # Set as a projectile
        context.object.projectile = True
        
        # Now initialize the location
        context.active_object.projectile_props.s = context.active_object.location
        
        return {'FINISHED'}


class PHYSICS_OT_projectile_remove(bpy.types.Operator):
    bl_idname = "rigidbody.projectile_remove_object"
    bl_label = "Remove Object"
    bl_description = "Remove object from as a projectile"
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return context.object.projectile
        
    def execute(self, context):
        # Remove animation data
        context.active_object.animation_data_clear()
        
        bpy.ops.rigidbody.objects_remove()
        
        context.object.projectile = False
        
        # HACKY! :D
        # Move frame forward, then back to update
        bpy.context.scene.frame_current += 1
        bpy.context.scene.frame_current -= 1
        
        return {'FINISHED'}
    

# TODO: Rename
class PHYSICS_PT_projectile_launch(bpy.types.Operator):
    bl_idname = "rigidbody.projectile_launch"
    bl_label = "Launch!"
    bl_description = "Launch the selected object!"
    
    @classmethod
    def poll(cls, context):
        if context.object:
            return context.object.type == 'MESH'
        
    def execute(self, context):
        object = context.object
        properties = object.projectile_props
        
        object.animation_data_clear()
        
        # Set start frame
        if bpy.context.scene.frame_start > properties.start_frame:
            properties.start_frame = bpy.context.scene.frame_start
            
        displacement = kinematic_displacement(properties.s, properties.v, 2)
        
        bpy.context.scene.frame_current = properties.start_frame
        # Set start keyframe
        object.location = properties.s
        object.keyframe_insert('location')
        
        bpy.context.scene.frame_current += 2
        
        # Set end keyframe
        object.location = displacement
        object.keyframe_insert('location')
        
        # Set animated checkbox
        object.rigid_body.kinematic = True
        object.keyframe_insert('rigid_body.kinematic')
        
        bpy.context.scene.frame_current += 1
        
        # Set unanimated checkbox
        object.rigid_body.kinematic = False
        object.keyframe_insert('rigid_body.kinematic')
        
        bpy.context.scene.frame_current = 0
        
        return {'FINISHED'}
        

# TODO: Decide where to best place these settings (maybe two panels?) Quick settings in sidebar
# And detailed settings in physics tab
class PHYSICS_PT_projectile(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"
    bl_label = "Projectile"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        view = context.space_data
        
        ob = context.object
        if (ob and ob.projectile):
            row = layout.row()
            row.operator('rigidbody.projectile_remove_object')
            
            row = layout.row()
            row.prop(ob.projectile_props, 'v')
            
            row = layout.row()
            row.operator('rigidbody.projectile_launch')
            
            row=layout.row()
            row.prop(context.object, 'projectile_draw_trajectories')
        else:
            row = layout.row()
            row.operator('rigidbody.projectile_add_object')
            
        
        
class ProjectileObjectProperties(bpy.types.PropertyGroup):
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[("initv", "Initial Velocity", "Set initial velocity"),
               ("goal",  "Goal",             "Set the goal")],
        default='initv')
        
    start_frame: bpy.props.IntProperty(
        name="Start Frame",
        description="Frame to start velocity initialization on",
        default=1)
        
    s: bpy.props.FloatVectorProperty(
        name="Location",
        description="Initial position for the object",
        subtype='TRANSLATION')
        
    v: bpy.props.FloatVectorProperty(
        name="Velocity",
        description="Set the velocity of the object",
        subtype='VELOCITY')

classes = (
    ProjectileObjectProperties,
    PHYSICS_PT_projectile,
    PHYSICS_OT_projectile_add,
    PHYSICS_OT_projectile_remove,
    PHYSICS_PT_projectile_launch,
)

def register():    
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        
    bpy.types.Object.projectile_props = bpy.props.PointerProperty(type=ProjectileObjectProperties)
    bpy.types.Object.projectile = bpy.props.BoolProperty(name="Projectile")
    bpy.types.Object.projectile_draw_trajectories = bpy.props.BoolProperty(name="Draw Trajectories", default=True)
    
    bpy.types.SpaceView3D.draw_handler_add(draw_trajectory, (), 'WINDOW', 'POST_VIEW')

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
        
    del bpy.types.Object.projectile_props
    del bpy.types.Object.projectile
    
    bpy.types.SpaceView3D.draw_handler_remove(draw_trajectory, (), 'WINDOW', 'POST_VIEW')

    
if __name__ == "__main__":
    register()
