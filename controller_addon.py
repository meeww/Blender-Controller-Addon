

bl_info = {
        "name": "Controller Support",
        "author": "Meeww",
        "version": (0, 0, 1),
        "blender": (3, 3, 0),
        "location": "View3D > UI > CONTROLLER",
        "description": " Press N to open up the properties panel and scroll down to controller to activate the addon. To view the controller parameters simply open up the object properties panel of the object named '##Controller'",
        "warning": "",
        "doc_url": "",
        "category": "3D View",
    }


import bpy

import ctypes
from bpy.types import Panel, PropertyGroup, Scene, WindowManager
from bpy.props import (
    IntProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
)
class Globals():
    string= ""
class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]
xinput = ctypes.windll.xinput1_1  

XInputSetState = xinput.XInputSetState
XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
XInputSetState.restype = ctypes.c_uint       

def set_vibration(controller, left_motor, right_motor):
    vibration = XINPUT_VIBRATION(int(left_motor * 65535), int(right_motor * 65535))
    XInputSetState(controller, ctypes.byref(vibration))
    
def install(context):
    import subprocess
    import sys
    import os
     
    python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
    target = os.path.join(sys.prefix, 'lib', 'site-packages')
     
    subprocess.call([python_exe, '-m', 'ensurepip'])
    subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'])
     
    subprocess.call([python_exe, '-m', 'pip', 'install', '--upgrade', 'XInput-Python', '-t', target])
     
    print('FINISHED')
    import XInput
    
    
class Controller_Panel(Panel):
    bl_idname = "SCENE_PT_controller"
    bl_label = "Controller Support"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Controller"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        
        # Install Scripts
        layout.label(text="Run as Administrator to install:")
        row = layout.row()
        row.scale_y = 1.0
        row.operator("object.install_xinput")


        #run
        row = layout.row()
        row.scale_y = 1.0
        row.operator("wm.controller_operator")
        layout.label(text=str(Globals.string))
        
class InstallController(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.install_xinput"
    bl_label = "Install Controller Scripts"

    def execute(self, context):
        install(context)
        return {'FINISHED'}
           


class ModalTimerOperator(bpy.types.Operator):

    """Operator which runs itself from a timer"""
    bl_idname = "wm.controller_operator"
    bl_label = "Start Controller"

    _timer = None


    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            print("stopping")
            c = bpy.data.objects["##Controller"]
            c["Running"] = 0
            
            reload(c)
            self.cancel(context)
           
            return {'CANCELLED'}

        #Controller Code
        
        import XInput
            
        state=XInput.get_state(0)
        buttons = XInput.get_button_values(state);
        triggers = XInput.get_trigger_values(state);
        sticks = XInput.get_thumb_values(state);
        c = bpy.data.objects["##Controller"]

        c["Running"] = 1
   
        c["A"] = buttons["A"]
        c["B"] = buttons["B"]
        c["X"] = buttons["X"]
        c["Y"] = buttons["Y"]
        
        c["RT"] = triggers[1]
        c["LT"] = triggers[0]
        
        
        c["LS Horizontal"] = sticks[0][0]
        c["LS Vertical"] = sticks[0][1]
        c["LS Click"] = buttons["LEFT_THUMB"]
        
        c["RS Horizontal"] = sticks[1][0]
        c["RS Vertical"] = sticks[1][1]
        c["RS Click"] = buttons["RIGHT_THUMB"]
        
        c["DPAD_UP"] = buttons["DPAD_UP"]
        c["DPAD_LEFT"] = buttons["DPAD_LEFT"]
        c["DPAD_RIGHT"] = buttons["DPAD_RIGHT"]
        c["DPAD_DOWN"] = buttons["DPAD_DOWN"]
        
        c["LB"] = buttons["LEFT_SHOULDER"];
        c["RB"] = buttons["RIGHT_SHOULDER"];
        
        c["START"] = buttons["START"];
        c["SELECT"] = buttons["BACK"];
        set_vibration(0, c["Rumble_L"], c["Rumble_R"])
        reload(c)

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        found = False
        for obj in bpy.data.objects:
            if obj.name == "##Controller":
                found = True;
                controller = obj;

        if found == False:
            controller = bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            bpy.data.objects["Plane"].name = "##Controller"

        bpy.data.objects["##Controller"]["Rumble_L"] = 0.0;
        bpy.data.objects["##Controller"]["Rumble_R"] = 0.0;
        Globals.string = "Currently Running."

        
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        Globals.string = "Not Currently Running."
        wm.event_timer_remove(self._timer)
        
        
            


        


    

def register():
    #the usual registration...

    
    
    from bpy.utils import register_class
    bpy.utils.register_class(Controller_Panel)
    bpy.utils.register_class(InstallController)
    bpy.utils.register_class(ModalTimerOperator)

def unregister():
    #the usual unregistration in reverse order ...

    
    
    from bpy.utils import unregister_class
    bpy.utils.unregister_class(Controller_Panel)
    bpy.utils.unregister_class(InstallController)
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()
    
def reload(c):
    c.location[0] = 0.00;
    
    
