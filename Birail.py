import FreeCAD
import FreeCADGui
import math
from pivy import coin

class birail:
    def __init__(self, obj):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSub",  "Edge1",   "Base",   "Edge1")
        obj.addProperty("App::PropertyLinkSub",  "Edge2",   "Base",   "Edge2")
        obj.addProperty("App::PropertyBool",  "NormalizeTangent",   "Normalize",   "Normalize tangent" ).NormalizeTangent = False
        obj.addProperty("App::PropertyBool",  "NormalizeNormal",    "Normalize",   "Normalize normal"  ).NormalizeNormal = False
        obj.addProperty("App::PropertyBool",  "NormalizeBinormal",  "Normalize",   "Normalize binormal").NormalizeBinormal = False
        self.edge1 = None
        self.edge2 = None
        self.normTan = False
        self.normNor = False
        self.normBin = False

    def execute(self, obj):
        self.ruledSurface()
        obj.Shape = self.ruled

    def onChanged(self, fp, prop):
        FreeCAD.Console.PrintMessage('%s changed\n'%prop)
        if prop == "Edge1":
            self.edge1 = self.getEdge(fp.Edge1)
            self.ruledSurface()
        if prop == "Edge2":
            self.edge2 = self.getEdge(fp.Edge2)
            self.ruledSurface()
        if prop == "NormalizeTangent":
            self.normTan = fp.NormalizeTangent
        if prop == "NormalizeNormal":
            self.normNor = fp.NormalizeNormal
        if prop == "NormalizeBinormal":
            self.normBin = fp.NormalizeBinormal
            
    def getEdge(self, prop):
        o = prop[0]
        e = prop[1][0]
        n = eval(e.lstrip('Edge'))
        try:
            edge = o.Shape.Edges[n-1]
            return(edge)
        except:
            return(None)
        
    def ruledSurface(self):
        if isinstance(self.edge1,Part.Edge) and isinstance(self.edge2,Part.Edge):
            self.ruled = Part.makeRuledSurface(self.edge1, self.edge2)
            self.rail1 = self.ruled.Edges[0]
            self.rail2 = self.ruled.Edges[2]
            self.u0 = self.ruled.ParameterRange[0]
            self.u1 = self.ruled.ParameterRange[1]

    def tangentsAt(self, p):
        if self.normTan:
            return((self.rail1.tangentAt(p), self.rail2.tangentAt(p)))
        else:
            return((self.rail1.derivative1At(p), self.rail2.derivative1At(p)))
    def normalsAt(self, p):
        if self.normNor:
            return((self.ruled.normalAt(p,0).normalize(), self.ruled.normalAt(p,1).normalize()))
        else:
            return((self.ruled.normalAt(p,0), self.ruled.normalAt(p,1)))
    def binormalAt(self, p):
        # TODO check for 0-length vector
        v1 = self.rail1.valueAt(p)
        v2 = self.rail2.valueAt(p)
        v = v2.sub(v1)
        if self.normBin:
            return(v.normalize())
        else:
            return(v)
    def frame1At(self, p):
        t = self.tangentsAt(p)[0]
        b = self.binormalAt(p)
        return((b, t, self.ruled.normalAt(p,0)))
    def frame2At(self, p):
        t = self.tangentsAt(p)[1]
        b = self.binormalAt(p)
        return((b, t, self.ruled.normalAt(p,1)))
    def matrix1At(self, p):
        t = self.rail1.valueAt(p)
        u,v,w = self.frame1At(p)
        m=App.Matrix( u.x,v.x,w.x,t.x,
                      u.y,v.y,w.y,t.y,
                      u.z,v.z,w.z,t.z,
                      0.0,0.0,0.0,1.0)
        return(m)
    def matrix2At(self, p):
        t = self.rail2.valueAt(p)
        u,v,w = self.frame2At(p)
        m=App.Matrix( u.x,v.x,w.x,t.x,
                      u.y,v.y,w.y,t.y,
                      u.z,v.z,w.z,t.z,
                      0.0,0.0,0.0,1.0)
        return(m)
    

class birailVP:
    def __init__(self, obj):
        obj.Proxy = self
        
    #def getIcon(self):
        #return (path_curvesWB_icons+'/isocurve.svg')

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
  
    def setEdit(self,vobj,mode):
        return False
    
    def unsetEdit(self,vobj,mode):
        return

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None

    def claimChildren(self):
        return([self.Object.Edge1[0], self.Object.Edge2[0]])
        
    def onDelete(self, feature, subelements): # subelements is a tuple of strings
        try:
            self.Object.Edge1[0].ViewObject.show()
            self.Object.Edge2[0].ViewObject.show()
        except Exception as err:
            App.Console.PrintError("Error in onDelete: " + err.message)
        return True

def parseSel(selectionObject):
    res = []
    for obj in selectionObject:
        if obj.HasSubObjects:
            subobj = obj.SubObjects[0]
            if issubclass(type(subobj),Part.Edge):
                res.append((obj.Object,[obj.SubElementNames[0]]))
        else:
            res.append((obj.Object,["Edge1"]))
    return res

myBirail = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","Birail")
birail(myBirail)
birailVP(myBirail.ViewObject)

s = FreeCADGui.Selection.getSelectionEx()
myBirail.Edge1 = parseSel(s)[0]
myBirail.Edge2 = parseSel(s)[1]
myBirail.Edge1[0].ViewObject.Visibility = False
myBirail.Edge2[0].ViewObject.Visibility = False


#g=FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup","Groupe")

#for m in mm:
    #out = []
    #for p in outpts:
        #out.append(m.multiply(p))
    #c = Part.Compound([Part.Vertex(pt) for pt in out])
    #o = FreeCAD.ActiveDocument.addObject("Part::Feature","pro")
    #o.Shape = c
    #g.addObject(o)




