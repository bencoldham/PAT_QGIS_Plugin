import shutil
import tempfile
import traceback
import unittest
import warnings
from pathlib import Path
from qgis.PyQt.QtTest import QTest
from qgis.PyQt.QtCore import Qt, QEvent, QPoint, QTimer
from qgis.PyQt.QtWidgets import QPushButton, QDialogButtonBox, QMessageBox, QApplication
from qgis.gui import QgsMapCanvas, QgsMapMouseEvent
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRectangle, QgsVectorLayer, QgsFeature, \
    QgsFeatureIterator

from pat.tests.utilities import get_qgis_app  #, warn_with_traceback
from pat.gui.calcImageIndices_dialog import CalculateImageIndicesDialog

QGISAPP, CANVAS, IFACE, PARENT = get_qgis_app()

TEMP_FOLD = Path(tempfile.gettempdir()).joinpath(Path(__file__).stem)

class TestBlockGrid(unittest.TestCase):
    failedTests = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # open up a QGIS instance
        self.project = QgsProject.instance()
    # def tearDown(self) -> None:
    #     """tearDown() is run after every test function"""
    #     project = QgsProject.instance()
    #     project.removeAllMapLayers()


    @classmethod
    def setUpClass(cls) -> None:
        """run once before all its tests are executed"""
        if TEMP_FOLD.exists():
            shutil.rmtree(str(TEMP_FOLD))
        TEMP_FOLD.mkdir()

    @classmethod
    def tearDownClass(cls):
        IFACE.newProject()
        if len(cls.failedTests) == 0:
            print('Tests Passed .. Deleting {}'.format(TEMP_FOLD))
            shutil.rmtree(TEMP_FOLD)

    def test_defaults(self):
        """ Using default settings."""

        # Load a project
        self.project.read(str(Path(__file__).resolve().parent.joinpath('data', 'testing.qgz')))

        # Create and open the dialog
        dlg = CalculateImageIndicesDialog(IFACE)
        dlg.open()
        self.assertTrue(dlg.isVisible())

        self.assertEqual(1,   dlg.mcboRasterLayer.count())
        dlg.mcboRasterLayer.setCurrentIndex(0)
        dlg.mcboPolygonLayer.setCurrentIndex(0)

        # check auto crs detection
        self.assertEqual('EPSG:28354', dlg.mCRSoutput.crs().authid())

        #dlg.dsbPixelSize.setValue(5.0)
        #BandMapping(red=3, green=2, infrared=4, rededge=1, mask=5)

        dlg.cboBandRed.setCurrentIndex(2)
        dlg.cboBandGreen.setCurrentIndex(1)
        dlg.cboBandRedEdge.setCurrentIndex(0)
        dlg.cboBandIR.setCurrentIndex(3)
        dlg.cboBandNonVine.setCurrentIndex(4)

        print(dir(dlg))
        #for x in self.chkgrpIndices.buttons() :
        for x in dlg.chkgrpIndices.buttons() :
            x.setChecked(True)
        #
        # dlg.chkNDVI.setChecked(True)
        # dlg.chkPCD.setChecked(True)
        # dlg.chkNDRE.setCheccked(True)
        dlg.lneOutputFolder.setText(str(TEMP_FOLD))
        QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)



        #self.assertTrue(Path(out_file).exists())

        #layer = self.project.mapLayersByName('BlockGrid_5m')
        #self.assertEqual(1,len(layer))
        #self.assertEqual(QgsRectangle(300330, 6181420, 301005, 6181760), layer[0].extent())

    # def test_feature_selection(self):
    #     """ poly selection """
    #
    #     self.project.read(str(Path(__file__).resolve().parent.joinpath('data', 'testing.qgz')))
    #
    #     # Create and open the dialog
    #     dlg = CalculateImageIndicesDialog(IFACE)
    #     dlg.open()
    #     self.assertTrue(dlg.isVisible())
    #
    #     ply_lyr = self.project.mapLayersByName('Polygons')[0]
    #     ply_lyr.selectByExpression('"Id" = 0')
    #     self.assertEqual(1,ply_lyr.selectedFeatureCount())
    #
    #     dlg.mcboTargetLayer.setLayer(ply_lyr)
    #     self.assertTrue(dlg.chkUseSelected.isEnabled())
    #
    #     dlg.chkUseSelected.setChecked(True)
    #
    #     # check auto crs detection
    #     self.assertEqual('EPSG:28354',dlg.mCRSoutput.crs().authid())
    #
    #     out_file = str(TEMP_FOLD.joinpath(f'BlockGrid.tif'))
    #
    #     dlg.lneSaveRasterFile.setText(out_file)
    #     QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)
    #
    #     self.assertTrue(Path(out_file).exists())
    #
    #     layer = self.project.mapLayersByName('BlockGrid')
    #     self.assertEqual(1,len(layer))
    #     self.assertEqual(QgsRectangle(300392, 6181480, 300610, 6181694), layer[0].extent())
    #
    # def test_user_chosen_crs(self):
    #     """ user_coord system - 2.5m pixels """
    #
    #     # Load a project
    #     self.project.read(str(Path(__file__).resolve().parent.joinpath('data', 'testing.qgz')))
    #
    #     # Create and open the dialog
    #     dlg = CalculateImageIndicesDialog(IFACE)
    #     dlg.open()
    #     self.assertTrue(dlg.isVisible())
    #
    #     ply_lyr = self.project.mapLayersByName('Polygons')[0]
    #     ply_lyr.selectByExpression('"Id" = 1')
    #     self.assertEqual(1, ply_lyr.selectedFeatureCount())
    #
    #     dlg.mcboTargetLayer.setLayer(ply_lyr)
    #
    #     self.assertTrue(dlg.chkUseSelected.isEnabled())
    #     dlg.chkUseSelected.setChecked(True)
    #
    #     dlg.mCRSoutput.setCrs(QgsCoordinateReferenceSystem().fromEpsgId(28355))
    #     # check auto crs detection
    #     self.assertEqual('EPSG:28355', dlg.mCRSoutput.crs().authid())
    #
    #     dlg.dsbPixelSize.setValue(2.5)
    #     dlg.chkSnapExtent.setChecked(False)
    #     out_file = str(TEMP_FOLD.joinpath(f'BlockGrid_250cm.tif'))
    #
    #     dlg.lneSaveRasterFile.setText(out_file)
    #     QTest.mouseClick(dlg.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)
    #
    #     self.assertTrue(Path(out_file).exists())
    #
    #     layer = self.project.mapLayersByName('BlockGrid_250cm')
    #     self.assertEqual(1,len(layer))
    #     self.assertEqual(QgsRectangle(-251240.56515504419803619, 6153156.21100474148988724,
    #                                   -250850.56515504419803619, 6153408.71100474148988724),
    #                      layer[0].extent())
    #
    #     self.assertEqual(2.5,layer[0].rasterUnitsPerPixelX())
    #     self.assertEqual(2.5, layer[0].rasterUnitsPerPixelY())

if __name__ == "__main__":
    suite = unittest.makeSuite(TestBlockGrid)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)