"""Генерирует простую тестовую модель Rhino (test_model.3dm).

Запуск:  pip install rhino3dm && python make_test_model.py
"""
import rhino3dm as r3d

model = r3d.File3dm()
model.Settings.ModelUnitSystem = r3d.UnitSystem.Millimeters


def add_layer(name, rgb):
    layer = r3d.Layer()
    layer.Name = name
    layer.Color = (*rgb, 255)
    return model.Layers.Add(layer)


def attrs(layer_index, name):
    a = r3d.ObjectAttributes()
    a.LayerIndex = layer_index
    a.Name = name
    return a


solids = add_layer("Solids", (200, 80, 60))
curves = add_layer("Curves", (40, 120, 220))
points = add_layer("Points", (30, 160, 70))

# Куб 100x100x100
box = r3d.Box(r3d.BoundingBox(r3d.Point3d(0, 0, 0), r3d.Point3d(100, 100, 100)))
model.Objects.AddBrep(r3d.Brep.CreateFromBox(box), attrs(solids, "Box"))

# Сфера R=50 рядом с кубом
sphere = r3d.Sphere(r3d.Point3d(200, 50, 50), 50)
model.Objects.AddBrep(sphere.ToBrep(), attrs(solids, "Sphere"))

# Цилиндр R=30, H=120
circle = r3d.Circle(r3d.Point3d(320, 50, 0), 30)
cyl = r3d.Cylinder(circle, 120)
model.Objects.AddBrep(cyl.ToBrep(True, True), attrs(solids, "Cylinder"))

# Опорная окружность и прямоугольная рамка вокруг всех объектов
model.Objects.AddCircle(r3d.Circle(r3d.Point3d(200, 50, 0), 80), attrs(curves, "BaseCircle"))
frame = r3d.Polyline([
    r3d.Point3d(-20, -40, 0), r3d.Point3d(370, -40, 0),
    r3d.Point3d(370, 140, 0), r3d.Point3d(-20, 140, 0), r3d.Point3d(-20, -40, 0),
])
model.Objects.AddPolyline(frame, attrs(curves, "Frame"))

# Точка в начале координат
model.Objects.AddPoint(r3d.Point3d(0, 0, 0), attrs(points, "Origin"))

model.Write("test_model.3dm", 7)
print(f"Saved test_model.3dm: {len(model.Objects)} objects, {len(model.Layers)} layers")
