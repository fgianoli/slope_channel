# -*- coding: utf-8 -*-

"""
/***************************************************************************
 HSA
                                 A QGIS plugin
 This plugin add to the processing toolbox a geoprocess to compute the Hydraulic Average Slope
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-03-04
        copyright            : (C) 2022 by Salvatore Fiandaca, Antonio Cotroneo, Federico Gianoli
        email                : gianoli.federico@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Salvatore Fiandaca, Antonio Cotroneo, Federico Gianoli'
__date__ = '2022-03-04'
__copyright__ = '(C) 2022 by Salvatore Fiandaca, Antonio Cotroneo, Federico Gianoli'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import glob
import shutil

from qgis.core import (
    Qgis,
    QgsProcessingProvider,
    QgsApplication,
    QgsMessageLog,
    QgsProcessingModelAlgorithm
)
from processing.modeler.ModelerUtils import ModelerUtils
from processing.core.ProcessingConfig import (
    ProcessingConfig,
    Setting
)
from qgis.utils import (
    iface,
    unloadPlugin
)
from PyQt5.QtGui import (
    QIcon
)
from PyQt5.QtWidgets import (
    QMessageBox
)
from processing.tools.system import isWindows
##from .hsa_algorithm import HSA


class SlopeChannel(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        self.modelsPath = os.path.join(os.path.dirname(__file__), 'model')
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def load(self):
            # check dependencies in lazy way because need that all
            # plugin dependency have to be loaded before to check

            if QgsApplication.processingRegistry().providerById('model'):
                self.loadModels()
            else:
                # lazy load of models waiting QGIS initialization. This would avoid
                # to load modelas when model provider is still not available in processing
                iface.initializationCompleted.connect(self.loadModels)

            return True

    def loadModels(self):
            '''Register models present in models folder of the plugin.'''
            try:
                iface.initializationCompleted.disconnect(self.loadModels)
            except:
                pass

            modelsFiles = glob.glob(os.path.join(self.modelsPath, '*.model3'))

            for modelFileName in modelsFiles:
                alg = QgsProcessingModelAlgorithm()
                if not alg.fromFile(modelFileName):
                    QgsMessageLog.logMessage(self.tr('Not well formed model: {}'.format(modelFileName)), self.messageTag, Qgis.Warning)
                    continue

                destFilename = os.path.join(ModelerUtils.modelsFolders()[0], os.path.basename(modelFileName))
                try:
                    if os.path.exists(destFilename):
                        os.remove(destFilename)

                    if isWindows():
                        shutil.copyfile(modelFileName, destFilename)
                    else:
                        os.symlink(modelFileName, destFilename)
                except Exception as ex:
                    QgsMessageLog.logMessage(self.tr('Failed to install model: {} - {}'.format(modelFileName, str(ex))), self.messageTag, Qgis.Warning)
                    continue

            QgsApplication.processingRegistry().providerById('model').refreshAlgorithms()

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'SlopeChannel'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('SlopeChannel')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()
