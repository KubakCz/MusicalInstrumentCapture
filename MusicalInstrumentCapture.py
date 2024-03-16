import bpy
from .ImportHands import MESH_OT_ImportHands


class VIEW3D_PT_MusicalInstrumentCapture(bpy.types.Panel):
    bl_label = "Musical Instrument Capture"
    bl_idname = "VIEW3D_PT_MusicalInstrumentCapture"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Musical Instrument Capture"

    def draw(self, context):
        layout = self.layout
        layout.operator(MESH_OT_ImportHands.bl_idname, text="Import Hands")
