---
name: rhino-model
description: Создаёт 3D-модели для Rhino (.3dm) — тестовые сцены, простые тела, кривые, слои. Используй, когда просят «сделай модель в Rhino / рино», «.3dm», «через Rhino MCP», «скрипт для Rhino», rhino3dm, rhinoscriptsyntax. Сам выбирает путь — Rhino MCP, если он подключён, иначе генерация .3dm через rhino3dm или готовый скрипт для запуска в Rhino.
---

# Модели для Rhino

Цель: пользователь получает модель, которую можно открыть в Rhino, и способ её пересобрать.

## 1. Выбери путь (по порядку)

1. **Rhino MCP.** Если в списке инструментов есть инструменты Rhino (ищи через ToolSearch `rhino`), строй геометрию прямо в открытом Rhino через них. После построения запроси список объектов или их ограничивающие рамки и сверь с заданием.
2. **Нет MCP → `rhino3dm` (Python).** Это вариант по умолчанию в облаке и без Rhino: `pip install rhino3dm`, скрипт пишет `.3dm`.
3. **Нужна операция, которой нет в rhino3dm** (булевы операции, скругления, сдвиг поверхностей, лофт по многим сечениям, Grasshopper) → напиши скрипт `rhinoscriptsyntax` для запуска внутри Rhino (`ScriptEditor` в Rhino 8 или `EditPythonScript` в Rhino 7). Честно скажи, что ты его не запускал.

Если просят именно MCP, а его нет: не изображай работу через MCP. Объясни, что Rhino MCP управляет локально запущенным Rhino через плагин на localhost, поэтому из облачной сессии он недоступен. Кратко дай шаги подключения: установить плагин, выполнить `mcpstart` в Rhino, добавить сервер в локальный Claude (`claude mcp add rhino -- uvx rhinomcp`; точная команда — в README выбранной реализации). Затем предложи пути 2 или 3.

## 2. Структура результата (путь 2)

```
rhino/
  make_<name>.py   # генератор, запускается без аргументов
  <name>.3dm       # результат
```

Правила для модели:
- Задай единицы явно: `model.Settings.ModelUnitSystem = r3d.UnitSystem.Millimeters` (если не просили другие).
- Раскладывай по слоям по типу (`Solids`, `Curves`, `Points` …), у каждого слоя свой цвет.
- Давай каждому объекту имя через `ObjectAttributes.Name`.
- Не накладывай объекты друг на друга без причины: разноси их по X, чтобы в Rhino всё было видно сразу.
- Сохраняй с `model.Write(path, 7)`: такой файл откроется в Rhino 7 и 8.

## 3. Шаблон rhino3dm

```python
import rhino3dm as r3d

model = r3d.File3dm()
model.Settings.ModelUnitSystem = r3d.UnitSystem.Millimeters

def add_layer(name, rgb):
    layer = r3d.Layer(); layer.Name = name; layer.Color = (*rgb, 255)
    return model.Layers.Add(layer)

def attrs(layer_index, name):
    a = r3d.ObjectAttributes(); a.LayerIndex = layer_index; a.Name = name
    return a

solids = add_layer("Solids", (200, 80, 60))

box = r3d.Box(r3d.BoundingBox(r3d.Point3d(0, 0, 0), r3d.Point3d(100, 100, 100)))
model.Objects.AddBrep(r3d.Brep.CreateFromBox(box), attrs(solids, "Box"))

model.Write("model.3dm", 7)
```

## 4. Известные подвохи rhino3dm

- `r3d.Circle(plane, r)` **не существует**. Используй `r3d.Circle(center_point3d, r)` или `r3d.Circle(r)`.
- Цилиндр: `r3d.Cylinder(circle, height).ToBrep(True, True)`, где флаги означают крышки снизу и сверху. Без них получится открытая труба.
- Сфера: `r3d.Sphere(center, r).ToBrep()`.
- Кривые: `AddCircle`, `AddLine`, `AddPolyline` (чтобы контур был замкнут, повтори первую точку в конце).
- В rhino3dm нет булевых операций, скруглений и пересечений: это путь 3.
- Сначала проверь сигнатуру незнакомого конструктора (`help(r3d.X)`), потом пиши код.

## 5. Проверка (обязательно)

После генерации перечитай файл и выведи состав:

```python
m = r3d.File3dm.Read("model.3dm")
for o in m.Objects:
    print(o.Attributes.Name, type(o.Geometry).__name__,
          m.Layers[o.Attributes.LayerIndex].Name, o.Geometry.GetBoundingBox().Max)
```

Сверь количество объектов, слои и габариты с заданием. В отчёте разделяй то, что проверено (файл прочитан через rhino3dm), и то, что не проверено (файл не открывался в самом Rhino).

## 6. Отчёт пользователю

- Отправь `.3dm` через SendUserFile (`display: attach`).
- Дай таблицу «Слой | Объект | Параметры», указав единицы.
- Покажи команду для пересборки: `pip install rhino3dm && python make_<name>.py`.
- Предложи одно-два естественных продолжения (другая геометрия, скрипт для Rhino, Grasshopper).
- Если работа идёт в репозитории, закоммить скрипт и `.3dm` в рабочую ветку.
