from Python_Skripts.GUI import UserInterface
import tkinter as tk

"""
This script creates a Draw.io XML file from the widget structure of the GUI.
To update the file simply run this script, then go into the draw io file. 
Under "Arrange" -> "Layout" select "Horizontal Tree".
"""



def get_widget_structure(widget, structure = [], indent=0):    
    structure.append(("  " * indent + f"{widget.winfo_name()}", indent))
    for child in widget.winfo_children():
        get_widget_structure(child, structure = structure,indent = indent + 1)

    return structure

def convert_to_drawio_xml(widget_structure):
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n<mxfile host="app.diagrams.net">\n  <diagram name="Page-1">\n    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">\n      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
    xml_footer = '      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>'
    xml_content = ''
    cell_id = 2
    parent_id = 1
    stack = [(parent_id, 0)]  # (parent_id, indent_level)
    connections = []

    for line, indent in widget_structure:
        while stack and stack[-1][1] >= indent:
            stack.pop()
        parent_id = stack[-1][0] if stack else 1
        xml_content += f'        <mxCell id="{cell_id}" value="{line.strip()}" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">\n          <mxGeometry x="{indent * 200}" y="{len(stack) * 80}" width="120" height="40" as="geometry"/>\n        </mxCell>\n'
        if parent_id != 1:
            connections.append((parent_id, cell_id))
        stack.append((cell_id, indent))
        cell_id += 1

    for parent_id, child_id in connections:
        xml_content += f'        <mxCell id="{cell_id}" style="edgeStyle=elbowEdgeStyle;elbow=horizontal;rounded=1;orthogonalLoop=1;" edge="1" parent="1" source="{parent_id}" target="{child_id}">\n          <mxGeometry relative="1" as="geometry"/>\n        </mxCell>\n'
        cell_id += 1

    xml_file = xml_header + xml_content + xml_footer

    return xml_file




root = tk.Tk()
app = UserInterface(root)

root.camera_object.updating = False
root.stop_update_checkboxes = True


structure = []
get_widget_structure(root, structure)

drawio_xml = convert_to_drawio_xml(structure)


"""
# Example
root = tk.Tk()
panel1 = tk.Frame(root, name="panel1")
panel2 = tk.Frame(root, name="panel2")

button_1_1 = tk.Button(panel1, name="button_1_1")
button_1_2 = tk.Button(panel1, name="button_1_2")
button_2_1 = tk.Button(panel2, name="button_2_1")

structure = get_widget_structure(root)
drawio_xml = convert_to_drawio_xml(structure)
"""

with open("widget_structure.drawio", "w") as file:
    file.write(drawio_xml)

print("Draw.io XML file created")


