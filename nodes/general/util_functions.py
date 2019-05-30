import bpy

def joinObjects(col,joinTo,toJoin):
    joinTo.select_set(state=True)
    toJoin.select_set(state=True)
    ctx = bpy.context.copy()
    ctx['active_object'] = joinTo
    ctx['selected_objects'] = [joinTo,toJoin]
    bpy.ops.object.join(ctx)
    return
