from PySide2 import QtCore,QtGui,QtWidgets
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

def maya_main_window():
    main_window_ptr= omui.MQtUtil.mainWindow()
    return wrapInstance (int(main_window_ptr), QtWidgets.QWidget)
    
class ArrangeDialog(QtWidgets.QDialog):
    attr_role_widget1 = QtCore.Qt.UserRole
    value_role_widget1 = QtCore.Qt.UserRole +1
    attr_role_widget2 = QtCore.Qt.UserRole +2
    value_role_widget2 = QtCore.Qt.UserRole +3
    
    selected_obj=[]
    selected_obj_tochange =[]
    
    FILE_FILTERS = "Maya (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"

    selected_filter = "Maya (*ma *.mb)"
    def __init__(self,parent=maya_main_window()):
        super().__init__(parent)
        self.setWindowTitle('Copy to Objects')
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.create_widgets()
        self.create_layout()
        self.connections()
        
    def create_widgets(self):
        self.filepath_le = QtWidgets.QLineEdit()
        self.select_file_path_btn = QtWidgets.QPushButton()
        self.select_file_path_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.select_file_path_btn.setToolTip("Select File")
        self.add_import = QtWidgets.QPushButton('Add')
        self.import_btn= QtWidgets.QPushButton('Import')
        
        self.apply_btn = QtWidgets.QPushButton('Apply')
        self.refresh_btn = QtWidgets.QPushButton('Refresh')
        self.close_btn = QtWidgets.QPushButton('Close')
        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget2 = QtWidgets.QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget2.setColumnCount(2)
        self.table_widget.setColumnWidth(0,22)
        self.table_widget2.setColumnWidth(0,22)
        self.table_widget.setHorizontalHeaderLabels(['','Name'])
        self.table_widget2.setHorizontalHeaderLabels(['','Name'])
        self.label_center = QtWidgets.QLabel('change')
        
        header_view=self.table_widget.horizontalHeader()
        header_view.setSectionResizeMode(1,QtWidgets.QHeaderView.Stretch)
        header_view2=self.table_widget2.horizontalHeader()
        header_view2.setSectionResizeMode(1,QtWidgets.QHeaderView.Stretch)
        
        
    def create_layout(self):
        
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.filepath_le)
        file_path_layout.addWidget(self.select_file_path_btn)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.setSpacing(2)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.close_btn)
        
        table_layout = QtWidgets.QHBoxLayout()
        table_layout.setSpacing(6)
        table_layout.addWidget(self.table_widget)
        table_layout.addWidget(self.label_center)
        table_layout.addWidget(self.table_widget2)
        
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(file_path_layout)
        main_layout.addWidget(self.add_import)
        main_layout.addWidget(self.import_btn)
        main_layout.addLayout(table_layout)
        main_layout.setSpacing(10)
        
        main_layout.addLayout(btn_layout) 
        
    def connections(self):
        self.select_file_path_btn.clicked.connect(self.show_file_select_dialog)
        self.import_btn.clicked.connect(self.load_file)
    
        self.apply_btn.clicked.connect(self.copy_to_objects)
        self.set_cell_change_enabled(True)
        self.set_cell_change_enabled2(True)
        self.refresh_btn.clicked.connect(self.refresh_table)
        self.close_btn.clicked.connect(self.close) 
        
    
    def show_file_select_dialog(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, "Select File", "", self.FILE_FILTERS, self.selected_filter)
        if file_path:
            self.filepath_le.setText(file_path)
            
    def load_file(self):
        file_path = self.filepath_le.text()
        if not file_path:
            return

        file_info = QtCore.QFileInfo(file_path)
        if not file_info.exists():
            om.MGlobal.displayError("File does not exist: {0}".format(file_path))
            return
            
        else:
            self.import_file(file_path)
            
    def import_file(self, file_path):
        cmds.file(file_path, i=True, ignoreVersion=True)


    def set_cell_change_enabled(self,enabled):
        
        if enabled:
             self.table_widget.cellChanged.connect(self.on_cell_changed_widget1)
        else:
             self.table_widget.cellChanged.disconnect(self.on_cell_changed_widget1)


    def set_cell_change_enabled2(self,enabled):
        
        if enabled:
             self.table_widget2.cellChanged.connect(self.on_cell_changed_widget2)
        else:
             self.table_widget2.cellChanged.disconnect(self.on_cell_changed_widget2)

    def refresh_table(self):
        self.set_cell_change_enabled(False)
        self.set_cell_change_enabled2(False)
        self.table_widget.setRowCount(0)
        self.table_widget2.setRowCount(0)
        meshes = cmds.ls(type='mesh')
        for i in range(len(meshes)):
            transform_node = cmds.listRelatives(meshes[i], parent=True)[0]
            translation = cmds.getAttr(f"{transform_node}.translate")[0]
            selected =cmds.ls(sl=True)
            selected_value = False
            if transform_node in selected:
                selected_value = True
            
            self.table_widget.insertRow(i) 
            self.table_widget2.insertRow(i)    
            
            self.insert_item(i,1,transform_node,None, transform_node,False)
            self.insert_item(i,0,'', 'visibility', selected_value, True)
            self.insert_item2(i,1,transform_node,None, transform_node,False)
            self.insert_item2(i,0,'', 'visibility',None, True)

        self.set_cell_change_enabled(True)
        self.set_cell_change_enabled2(True)

    def showEvent (self,e):
        super().showEvent(e)
        self.refresh_table()
            
    def keyPressEvent (self,e):
        super().keyPressEvent(e)
        e.accept()
                
    def insert_item(self, row, column, text, attr, value, isboolean):
        item = QtWidgets.QTableWidgetItem(text)
        self.set_item_attr(item,attr)
        self.set_item_val(item,value)
        if isboolean:
            item.setFlags(QtCore.Qt.ItemIsUserCheckable| QtCore.Qt.ItemIsEnabled)
            self.set_item_checked(item,value)
        
        self.table_widget.setItem(row,column,item)
       
        
    def insert_item2(self, row, column, text, attr, value, isboolean):
        item = QtWidgets.QTableWidgetItem(text)
        self.set_item_attr_w2(item,attr)
        self.set_item_val_w2(item,value)
        if isboolean:
            item.setFlags(QtCore.Qt.ItemIsUserCheckable| QtCore.Qt.ItemIsEnabled)
            self.set_item_checked(item,value)
        
        self.table_widget2.setItem(row,column,item)

    def duplicate_object (self, objectname, newname):
        cmds.duplicate('objectname', n='newname')

    def on_cell_changed_widget1(self,row,column):
        self.set_cell_change_enabled(False)
        item = self.table_widget.item(row,column)
        if column == 1:
            self.name_rename(item)
        else:
            isboolean=column==0
            self.select_widget1(row)
        self.set_cell_change_enabled(True)
      
    def select_widget1 (self,row):
        transform_node = self.table_widget.item(row,1).data(self.value_role_widget1)
        cmds.select(f'{transform_node}')
        self.selected_obj.append(f'{transform_node}')
        
    def on_cell_changed_widget2(self,row,column):
        self.set_cell_change_enabled2(False)
        item = self.table_widget2.item(row,column)
        if column == 1:
            self.name_rename(item)
        else:
            isboolean=column==0
            self.get_transform_details_widget(row)
            
        self.set_cell_change_enabled2(True)
        
    def get_transform_details_widget(self,row):
        item = self.table_widget2.item(row,0)
        value = self.is_item_checked(item)
        if value:
            node_name = self.table_widget2.item(row,1).data(self.value_role_widget2)
            self.selected_obj_tochange.append(f'{node_name}')        
    
    def copy_to_objects (self):
        a = 1
        for obj in self.selected_obj_tochange:
            translation = cmds.getAttr(f"{obj}.translate")[0]
            tx = translation[0]
            ty = translation[1]
            tz = translation[2]
            
           
            for i in self.selected_obj:
    
                cmds.duplicate(f'{i}', n= f'{i}_{a}')
                cmds.delete(f'{obj}')
                cmds.setAttr( f'{i}_{a}.translateX', tx )
                cmds.setAttr( f'{i}_{a}.translateY', ty )
                cmds.setAttr( f'{i}_{a}.translateZ', tz )
                a+=1
                self.refresh_table()
            
        self.selected_obj = []
        self.selected_obj_tochange = []
        print(self.selected_obj)
        print (self.selected_obj_tochange)
        
    def get_item_attr (self,item):
        return item.data(self.attr_role_widget1)
        
    def set_item_attr(self,item,attr):
        item.setData(self.attr_role_widget1,attr)
        
    def get_item_val (self,item):
        return item.data(self.value_role_widget1)
    
    def set_item_val(self,item,value):
        item.setData(self.value_role_widget1,value)
    
    def get_item_attr_w2 (self,item):
        return item.data(self.attr_role_widget2)
        
    def set_item_attr_w2(self,item,attr):
        item.setData(self.attr_role_widget2,attr)
        
    def get_item_val_w2 (self,item):
        return item.data(self.value_role_widget2)
    
    def set_item_val_w2(self,item,value):
        item.setData(self.value_role_widget2,value)
    

    def name_rename (self,item):
        old_name = self.get_item_val(item)
        new_name = self.get_item_text(item)
        
        if old_name != new_name:
            actual_new_name = cmds.rename(old_name,new_name)
            if actual_new_name != new_name:
                self.set_item_text(item,actual_new_name)
            self.set_item_val(item, actual_new_name)
    
    def set_item_text(self, item, text):
        item.setText(text)
    def get_item_text(self,item):
        return item.text()
    def set_item_checked(self,item,checked):
        if checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)
        
    def is_item_checked(self,item):
        return item.checkState()==QtCore.Qt.Checked
   
    def float_to_string(self,value):
        return f'{value:4f}'
        
    def revert_original_value(self,item,isboolean):
        original_value = self.get_item_value(item)
        if isboolean:
            self.set_item_checked(item,original_value)
        else:
            self.set_item_text(item, self.float_to_string(original_value))
            
    def get_full_attr (self, row, item):
        node_name = self.table_widget.item(row,1).data(self.value_role)
        attr_name = self.get_item_attr(item)
        return f'{node_name}.{attr_name}'
        
    def closeEvent(self, e):
        self.selected_obj = []
        self.selected_obj_tochange = []

if __name__ == '__main__':
    try:
        arrangedialog.close()
        arrangedialog.Deletelater()
    except:
        pass
            
    arrangedialog = ArrangeDialog()
    arrangedialog.show()