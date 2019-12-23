# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Projectile",
    "author": "Nathan Craddock",
    "version": (1, 0),
    "blender": (2, 81, 0),
    "location": "3D View Sidebar > Physics tab",
    "description": "Set initial velocities for rigid body physics",
    "tracker_url": "",
    "category": "Physics"
}

from . import ui
from . import ops
from . import utils

def register():
    ui.register()
    ops.register()
    utils.register()

def unregister():
    ui.register()
    ops.register()
    utils.register()
