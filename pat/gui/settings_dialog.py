# -*- coding: utf-8 -*-"""/*************************************************************************** CSIRO Precision Agriculture Tools (PAT) Plugin SettingsDialog - Dialog used for setting default paths for use with PAT.        These will only get used on first run. Each separate tool will then        store it's own sets of defaults.           -------------------        begin      : 2018-03-13        git sha    : $Format:%H$        copyright  : (c) 2018, Commonwealth Scientific and Industrial Research Organisation (CSIRO)        email      : PAT@csiro.au ***************************************************************************//*************************************************************************** *                                                                         * *   This program is free software; you can redistribute it and/or modify  * *   it under the terms of the associated CSIRO Open Source Software       * *   License Agreement (GPLv3) provided with this plugin.                  * *                                                                         * ***************************************************************************/"""import loggingimport osimport pandas as pdimport sysimport platformfrom qgis.core import QgsProjectfrom pat.util.check_dependencies import check_vesper_dependencytry:    import configparser as configparserexcept ImportError:    import configparserfrom pkg_resources import get_distributionimport qgisimport webbrowserfrom pat import PLUGIN_NAME, TEMPDIR, PLUGIN_DIRfrom qgis.PyQt import uicfrom qgis.PyQt.QtWidgets import QMessageBoxfrom qgis.PyQt import QtCore, QtGuifrom qgis.core import Qgisfrom qgis.PyQt.QtWidgets import QFileDialogfrom util.check_dependencies import  plugin_statusfrom util.custom_logging import stop_logging, setup_logger, set_log_filefrom util.settings import read_setting, write_setting, update_elementfrom pyprecag import configpluginPath = os.path.split(os.path.dirname(__file__))[0]WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, 'gui', 'settings_dialog_base.ui'))LOGGER = logging.getLogger(__name__)LOGGER.addHandler(logging.NullHandler())  # logging.StreamHandler()class SettingsDialog(BASE, WIDGET):    """Dialog for managing plugin settings."""    def __init__(self, iface, parent=None):        super(SettingsDialog, self).__init__(parent)        # Set up the user interface from Designer.        self.setupUi(self)        self.iface = iface        self.lneInDataDirectory.setText(read_setting(PLUGIN_NAME + '/BASE_IN_FOLDER'))        self.lneOutDataDirectory.setText(read_setting(PLUGIN_NAME + '/BASE_OUT_FOLDER'))        self.chkDisplayTempLayers.setChecked(read_setting(PLUGIN_NAME + '/DISP_TEMP_LAYERS', bool))        self.chkDebug.setChecked(read_setting(PLUGIN_NAME + '/DEBUG', bool))        self.chkSaveLogToProjectFolder.setChecked(read_setting(PLUGIN_NAME + '/PROJECT_LOG', bool))        self.chkUseProjectName.setChecked(read_setting(PLUGIN_NAME + '/USE_PROJECT_NAME', bool))        self.vesper_exe = check_vesper_dependency()        if not os.path.exists(self.vesper_exe):            self.vesper_exe = read_setting(PLUGIN_NAME + '/VESPER_EXE')        self.lneVesperExe.setText(self.vesper_exe)        # Add text to plain text box ------------        self.update_versions(level='advanced')        self.pteVersions.setOpenExternalLinks(True)                self.setWindowIcon(QtGui.QIcon(':/plugins/pat/icons/icon_settings.svg'))    def update_versions(self,level='basic'):                df_dep = plugin_status(level=level).reset_index()        df_dep = pd.melt(df_dep, id_vars=['name','type'], value_vars= ['current','folder'], var_name='source', value_name='value').dropna()        df_dep.loc[df_dep['source']=='folder','name']= df_dep['name'] + ' Folder'                df_dep['type'] = df_dep['type'] + ':'        df_dep['name'] = df_dep['name'] + ':   '        pat_info=''        with pd.option_context("display.max_colwidth", 999):            for n,df in df_dep.groupby('type',sort=False):                pat_info+=f'<b>{n}</b>'                pat_info +=  df[['name','value']].to_html(index=False,header=False,border=0)  + '<br><br>'        self.pteVersions.setText(pat_info)    @QtCore.pyqtSlot(int)    def on_chkDisplayTempLayers_stateChanged(self, state):        if read_setting(PLUGIN_NAME + '/DISP_TEMP_LAYERS', bool) != self.chkDisplayTempLayers.isChecked():            write_setting(PLUGIN_NAME + '/DISP_TEMP_LAYERS', self.chkDisplayTempLayers.isChecked())    @QtCore.pyqtSlot(int)    def on_chkDebug_stateChanged(self, state):        if config.get_debug_mode() != self.chkDebug.isChecked():            write_setting(PLUGIN_NAME + '/DEBUG', self.chkDebug.isChecked())            config.set_debug_mode(self.chkDebug.isChecked())    @QtCore.pyqtSlot(int)    def on_chkSaveLogToProjectFolder_stateChanged(self, state):        write_setting(PLUGIN_NAME + '/PROJECT_LOG', self.chkSaveLogToProjectFolder.isChecked())    @QtCore.pyqtSlot(int)    def on_chkUseProjectName_stateChanged(self, state):        write_setting(PLUGIN_NAME + '/USE_PROJECT_NAME', self.chkUseProjectName.isChecked())    @QtCore.pyqtSlot(name='on_cmdCheckUpdates_clicked')    def on_cmdCheckUpdates_clicked(self):        df_dep =  plugin_status(level='basic', check_for_updates=True,forced_update=True).reset_index()                if not read_setting(PLUGIN_NAME + '/UPDATE AVAILALBE', object_type=bool,default=False):            QMessageBox.information(self, 'Settings', 'No updates available!')            @QtCore.pyqtSlot(name='on_cmdInBrowse_clicked')    def on_cmdInBrowse_clicked(self):        s = QFileDialog.getExistingDirectory(self, self.tr("Open Source Data From"),                                             self.lneInDataDirectory.text(),                                             QFileDialog.ShowDirsOnly)        if s == '':            return        s = os.path.normpath(s)        self.lneInDataDirectory.setText(s)        write_setting(PLUGIN_NAME + '/BASE_IN_FOLDER', s)        reply = QMessageBox.question(self, 'Settings', 'Do you want to change individual tools input paths?',                                     QMessageBox.Yes, QMessageBox.No)        if reply == QMessageBox.Yes:            update_element("LastInFolder",s)    @QtCore.pyqtSlot(name='on_cmdViewLog_clicked')    def on_cmdViewLog_clicked(self):        log_file = read_setting(PLUGIN_NAME + '/LOG_FILE')        if os.path.exists(log_file):            webbrowser.open(log_file)        @QtCore.pyqtSlot(name='on_cmdOpenFolder_clicked')                def on_cmdOpenFolder_clicked(self):        """Run method that performs all the real work"""        # show the dialog        log_file = read_setting(PLUGIN_NAME + '/LOG_FILE')        if os.path.exists(log_file):                 from urllib.request import pathname2url             url = 'file:{}'.format(pathname2url(os.path.dirname(log_file)))            webbrowser.open(url)    @QtCore.pyqtSlot(name='on_cmdOutBrowse_clicked')    def on_cmdOutBrowse_clicked(self):        s = QFileDialog.getExistingDirectory(self, self.tr("Save Output Data To"),                                                   self.lneOutDataDirectory.text(),                                                    QFileDialog.ShowDirsOnly)        if s == '':            return        s = os.path.normpath(s)        self.lneOutDataDirectory.setText(s)        write_setting(PLUGIN_NAME + '/BASE_OUT_FOLDER', s)                reply = QMessageBox.question(self, 'Settings', 'Do you want to change individual tools output path?',                                     QMessageBox.Yes, QMessageBox.No)        if reply == QMessageBox.Yes:            update_element("LastOutFolder",s)    @QtCore.pyqtSlot(name='on_cmdVesperExe_clicked')    def on_cmdVesperExe_clicked(self):        default_dir = os.path.dirname(self.lneVesperExe.text())        if default_dir == '' or default_dir is None:            default_dir = r'C:\Program Files (x86)'        s = QFileDialog.getOpenFileName(self, self.tr("Select Vesper Executable"),                                              directory=default_dir,                                              filter=self.tr("Vesper Executable") + " (Vesper*.exe);;"                                                     + self.tr("All Exe Files") + " (*.exe);;")        if type(s) == tuple:            s = s[0]        if s == '':  # ie nothing entered            return        s = os.path.normpath(s)        self.lneVesperExe.setText(s)        try:            config.set_config_key('vesperEXE', s)        except:            LOGGER.warning('Could not write to config.json')        self.vesper_exe = s        write_setting(PLUGIN_NAME + '/VESPER_EXE', s)        self.update_versions()            def accept(self, *args, **kwargs):        # Stop and start logging to setup the new log level        log_file = set_log_file()        return super(SettingsDialog, self).accept(*args, **kwargs)