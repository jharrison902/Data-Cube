# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 12:52:42 2015

@author: jdh
"""

import os
import logging
from glob import glob
import re
import gdal
from gdal import gdalconst
import osr
from datetime import datetime
import numpy

from EOtools.DatasetDrivers import SceneDataset
from EOtools.execute import execute

import xml.etree.ElementTree as ET

from agdc.cube_util import DatasetError
from agdc.abstract_ingester import AbstractDataset
from agdc.landsat_ingester.landsat_bandstack import LandsatBandstack

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class LS8Dataset(AbstractDataset):
    def __init__(self, dataset_path):
        """Opens the dataset and extracts metadata.

        Most of the metadata is kept in self._ds which is
        a EOtools.DatasetDrivers.SceneDataset object. Some extra metadata is
        extracted and kept the instance attributes.
        """

        self._dataset_path = dataset_path
        LOGGER.info('Opening Dataset %s', self._dataset_path)
        
        #self._ds = SceneDataset(default_metadata_required=False, utm_fix=True)
        self._Open(self.get_dataset_path())

        #
        # Cache extra metadata in instance attributes.
        #

        self._dataset_size = 0
        
        #get the rest of our metadata for implementing abstracted methods
        
        self._Collect_Metadata(self.get_dataset_path())
        


        if self.get_processing_level() in ['ORTHO', 'L1T', 'MAP']:
            LOGGER.debug('Dataset %s is Level 1', self.get_dataset_path())
            self._gcp_count = self._get_gcp_count()
            self._mtl_text = self._get_mtl_text()
        else:
            self._gcp_count = None
            self._mtl_text = None

        self._xml_text = self.get_xml_text()

        AbstractDataset.__init__(self)
        
    def _Open(self, dataset_path,eAccessLevel=gdalconst.GA_ReadOnly):
        
        """Determine if this is pqa or nbar data.
        
        """
        self.band_dict = {}
        self._eAccess=eAccessLevel
        filelist = [filename for filename in os.listdir(self._dataset_path)
                    if re.match('\w*_PQA_\w*.tif', filename)]
        nodata_value = -9999 #TODO: Make this pull from database
        if len(filelist) > 0:
            #this is a pqa dataset
            print "PQA dataset found."
            self._isPQA = True
            self._eAccess = eAccessLevel
            #self.band_dict = {'file': filelist[0], 'band_file_number':1,'type':'Derived','dataset':dataset_path,'rasterIndex':1}
            self.band_dict[0] = {'file_pattern':filelist[0],'nodata_value':nodata_value,'tile_layer':1, 'band_name':'Pixel Quality Assurance','resampling_method':'near'}
            return
        self._isPQA=False
        """Open the directory and get the info we need
        this info is bands, scene start time, scene end time, scene center time, bounds
        """
        
        #find files matching *B#.tif
        file_number = 0
        band_names = ['Coastal Aerosol','Visible Blue', 'Visible Green', 'Visible Red', 'Near Infrared', 'Short-wave Infrared 1','Short-wave Infrared 2']
        for bandNumber in [1,2,3,4,5,6,7]:
            print file_number
            filePattern = '\w*[B]'+str(bandNumber)+'.TIF'
            
            tilelayer = 1 #I have no idea
            bandinfo = {'file_pattern':filePattern,'nodata_value':nodata_value,'tile_layer':tilelayer, 'band_name':band_names[file_number],'resampling_method':'bilinear'}
            self.band_dict[file_number]=bandinfo
            print "band added"
            file_number+=1
        
    def _Collect_Metadata(self, dataset_path):
        """
        This method collects the various pieces of information needed to ingest the dataset
        """
        RootBand = None
        #open the first band and get size
       # if self._isPQA == False:
        RootBand = gdal.Open(self.find_band_file(self.band_dict[0]['file_pattern']),self._eAccess)
        #else:
        #    RootBand = gdal.Open(self.find_band_file(self.band_dict['file']),self._eAccess)
        
        self._x_size = RootBand.RasterXSize
        self._y_size = RootBand.RasterYSize
        #get the width and height
        self._geo_transform = RootBand.GetGeoTransform()
        self._projection = RootBand.GetProjection()
        self._projectionRef = RootBand.GetProjectionRef()
        self._spatial_ref = osr.SpatialReference()
        self._spatial_ref.ImportFromWkt(RootBand.GetProjection())
        
        #read in the xml file
        filelist = [filename for filename in os.listdir(self._dataset_path)
                    if re.match('\w*.xml', filename)]
        print "XML File: "+os.path.join(self._dataset_path,filelist[0])
        xmlRoot = ET.parse(os.path.join(self._dataset_path,filelist[0])).getroot()
        print "Root element: "+xmlRoot.tag
        for child in xmlRoot:
            print child.tag, child.attrib
        self._global_metadata = xmlRoot[0]
        print "Child node: "+self._global_metadata.tag
        
        
        #get the relevant info. Note: global metadata must also have scene_Start_time and scene_end_time
        satellite_tag_list = {'LANDSAT_7':'LS7','LANDSAT_8':'LS8'}
        sensor_tag_list = {'ETM':'ETM+','OLI_TIRS':'OLI_TIRS'}
        satellite_name = self._global_metadata.findall('{http://espa.cr.usgs.gov/v1.2}satellite')[0].text
        self._satellite_tag = satellite_tag_list[satellite_name]
        satellite_sensor = self._global_metadata.find('{http://espa.cr.usgs.gov/v1.2}instrument').text
        self._sensor_tag = sensor_tag_list[satellite_sensor]
        self._acquisition_date = self._global_metadata.find('{http://espa.cr.usgs.gov/v1.2}acquisition_date').text
        self._scene_center_time = datetime.strptime(self._acquisition_date+'T'+self._global_metadata.find('{http://espa.cr.usgs.gov/v1.2}scene_center_time').text,"%Y-%m-%dT%H:%M:%S.%fZ")
        #self._scene_start_time = datetime.strptime(self._global_metadata.find('{http://espa.cr.usgs.gov/v1.1}scene_start_time').text,"%Y-%m-%d\\T%H:%M:%S\\Z")
        #self._scene_end_time = datetime.strptime(self._global_metadata.find('{http://espa.cr.usgs.gov/v1.1}scene_end_time').text,"%Y-%m-%d\\T%H:%M:%S\\Z")
        self._scene_start_time = self._scene_center_time
        self._scene_end_time = self._scene_center_time
        self._scene_processed_time = datetime.now()
        self._bounding_box = self._global_metadata.find('{http://espa.cr.usgs.gov/v1.2}bounding_coordinates')
        self._north = float(self._bounding_box.find('{http://espa.cr.usgs.gov/v1.2}north').text)
        self._south = float(self._bounding_box.find('{http://espa.cr.usgs.gov/v1.2}south').text)
        self._east = float(self._bounding_box.find('{http://espa.cr.usgs.gov/v1.2}east').text)
        self._west = float(self._bounding_box.find('{http://espa.cr.usgs.gov/v1.2}west').text)
        self._wrs = self._global_metadata.find('{http://espa.cr.usgs.gov/v1.2}wrs').attrib
        self._path = int(self._wrs['path'])
        self._row = int(self._wrs['row'])
        if self._satellite_tag == 'LS8' and self._isPQA==False:
            self._processing_level = 'NBAR' #placeholder
        elif self._isPQA == True:
            self._processing_level = 'PQA'
        
        #get lon lat box
        self._ll_lon = self._west
        self._ll_lat = self._south
        self._ul_lon = self._west
        self._ul_lat = self._north
        self._lr_lon = self._east
        self._lr_lat = self._south
        self._ur_lon = self._east
        self._ur_lat = self._north
        
        
        
        #get x y box
        self._ll_x=None
        self._ll_y=None
        self._lr_x=None
        self._lr_y=None
        self._ul_x=None
        self._ul_y=None
        self._ur_x=None
        self._ur_y=None
        
        self._spatial_ref_geo = self._spatial_ref.CloneGeogCS()
        self._cxform_to_geo = osr.CoordinateTransformation(self._spatial_ref, self._spatial_ref_geo)
        self._cxform_from_geo = osr.CoordinateTransformation(self._spatial_ref_geo, self._spatial_ref)
        
        extents        = self.GetExtent()
        array_extents  = numpy.array(extents)
        centre_x       = float(numpy.mean(array_extents[:,0]))
        centre_y       = float(numpy.mean(array_extents[:,1]))
        extents.append([centre_x,centre_y])
        if self._spatial_ref.IsGeographic():
            self._lonlats = {
                'CENTRE' : (extents[4][0], extents[4][1]),
                'UL'     : (extents[0][0], extents[0][1]),
                'UR'     : (extents[2][0], extents[2][1]),
                'LL'     : (extents[1][0], extents[1][1]),
                'LR'     : (extents[3][0], extents[3][1])
                           }
            # If the scene is natively in geographics, we shouldn't need to 
            # project the co-ordinates to UTM.

            # Set the georeferenced coordinates of the corner points if we don't already have them.
            # These generally only get set when the product is FAST-EQR when they're forced to None
            if not (self._ul_x and self._ul_y):
                self._ul_x, self._ul_y = self._lonlats['UL']
            if not (self._ur_x and self._ur_y):
                self._ur_x, self._ur_y = self._lonlats['UR']
            if not (self._ll_x and self._ll_y):
                self._ll_x, self._ll_y = self._lonlats['LL']
            if not (self._lr_x and self._lr_y):
                self._lr_x, self._lr_y = self._lonlats['LR']
                
            self._scene_centre_x, self._scene_centre_y = self._lonlats['CENTRE']
            
        else:
            self._coords = {
                'CENTRE' : (extents[4][0], extents[4][1]),
                'UL'     : (extents[0][0], extents[0][1]),
                'UR'     : (extents[2][0], extents[2][1]),
                'LL'     : (extents[1][0], extents[1][1]),
                'LR'     : (extents[3][0], extents[3][1])
                          }

            re_prj_extents=[]
            for x,y in extents:
                new_x, new_y, new_z = self._cxform_to_geo.TransformPoint(x,y)
                re_prj_extents.append([new_x,new_y])

            self._lonlats = {
                'CENTRE' : (re_prj_extents[4][0], re_prj_extents[4][1]),
                'UL'     : (re_prj_extents[0][0], re_prj_extents[0][1]),
                'UR'     : (re_prj_extents[2][0], re_prj_extents[2][1]),
                'LL'     : (re_prj_extents[1][0], re_prj_extents[1][1]),
                'LR'     : (re_prj_extents[3][0], re_prj_extents[3][1])
                           }
            if not (self._ul_x and self._ul_y):
                self._ul_x, self._ul_y = self._lonlats['UL']
            if not (self._ur_x and self._ur_y):
                self._ur_x, self._ur_y = self._lonlats['UR']
            if not (self._ll_x and self._ll_y):
                self._ll_x, self._ll_y = self._lonlats['LL']
            if not (self._lr_x and self._lr_y):
                self._lr_x, self._lr_y = self._lonlats['LR']
                
            self._scene_centre_x, self._scene_centre_y = self._lonlats['CENTRE']
            
            self.metadata_dict = {}
            self.metadata_dict['x-ref']=self.get_x_ref()
            self.metadata_dict['y-ref']=self.get_y_ref()
        
        
    def GetExtent(self):
        """Better optimized than the gdal one
        """
        gt = self._geo_transform
        extents = []
        x_array = [0,self._x_size]
        y_array = [0,self._y_size]

        for px in x_array:
            for py in y_array:
                x = gt[0]+(px*gt[1])+(py*gt[2])
                y = gt[3]+(px*gt[4])+(py*gt[5])
                extents.append([x,y])
        return extents
        
    def find_band_file(self, file_pattern):
        print "Looking for file based on file pattern"
        """Find the file in dataset_dir matching file_pattern and check
        uniqueness.

        Returns the path to the file if found, raises a DatasetError
        otherwise."""

        dataset_dir = self._dataset_path
        if not os.path.isdir(dataset_dir):
            
            raise DatasetError('%s is not a valid directory' % dataset_dir)
        print "File pattern: "+file_pattern
        filelist = [filename for filename in os.listdir(dataset_dir)
                    if re.match(file_pattern, filename)]
        if not len(filelist) == 1:
            raise DatasetError('Unable to find unique match ' +
                               'for file pattern %s' % file_pattern)

        return os.path.join(dataset_dir, filelist[0])    
    
    
    def get_dataset_path(self):
        """The path to the dataset on disk."""
        return self._dataset_path

    
    def get_satellite_tag(self):
        """A short unique string identifying the satellite."""
        return self._satellite_tag

    
    def get_sensor_name(self):
        """A short string identifying the sensor.

        The combination of satellite_tag and sensor_name must be unique.
        """
        return self._sensor_tag

    
    def get_processing_level(self):
        """A short string identifying the processing level or product.

        The processing level must be unique for each satellite and sensor
        combination.
        """
        return self._processing_level

    
    def get_x_ref(self):
        """The x (East-West axis) reference number for the dataset.

        In whatever numbering scheme is used for this satellite.
        """
        return self._path

    
    def get_y_ref(self):
        """The y (North-South axis) reference number for the dataset.

        In whatever numbering scheme is used for this satellite.
        """
        return self._row

    
    def get_start_datetime(self):
        """The start of the acquisition.

        This is a datetime without timezone in UTC.
        """
        return self._scene_start_time

    
    def get_end_datetime(self):
        """The end of the acquisition.

        This is a datatime without timezone in UTC.
        """
        return self._scene_end_time


    
    def get_datetime_processed(self):
        """The date and time when the dataset was processed or created.

        This is used to determine if that dataset is newer than one
        already in the database, and so should replace it.

        It is a datetime without timezone in UTC.
        """
        return self._scene_processed_time

    
    def get_dataset_size(self):
        """The size of the dataset in kilobytes as an integer."""
        command = "du -sk %s | cut -f1" % self.get_dataset_path()
        LOGGER.debug('executing "%s"', command)
        result = execute(command)

        if result['returncode'] != 0:
            raise DatasetError('Unable to calculate directory size: ' +
                               '"%s" failed: %s' % (command, result['stderr']))

        LOGGER.debug('stdout = %s', result['stdout'])

        return int(result['stdout'])

    
    def get_ll_lon(self):
        """The longitude of the lower left corner of the coverage area."""
        return self._ll_lon

    
    def get_ll_lat(self):
        """The lattitude of the lower left corner of the coverage area."""
        return self._ll_lat

    
    def get_lr_lon(self):
        """The longitude of the lower right corner of the coverage area."""
        return self._lr_lon

    
    def get_lr_lat(self):
        """The lattitude of the lower right corner of the coverage area."""
        return self._lr_lat

    
    def get_ul_lon(self):
        """The longitude of the upper left corner of the coverage area."""
        return self._ul_lon

    
    def get_ul_lat(self):
        """The lattitude of the upper left corner of the coverage area."""
        return self._ul_lat

    
    def get_ur_lon(self):
        """The longitude of the upper right corner of the coverage area."""
        return self._ur_lon

    
    def get_ur_lat(self):
        """The lattitude of the upper right corner of the coverage area."""
        return self._ur_lat

    
    def get_projection(self):
        """The coordinate refererence system of the image data."""
        return self._projection
        
    def GetProjectionRef(self):
        return self._projectionRef

    
    def get_ll_x(self):
        """The x coordinate of the lower left corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._ll_x

    
    def get_ll_y(self):
        """The y coordinate of the lower left corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._ll_y

    
    def get_lr_x(self):
        """The x coordinate of the lower right corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._lr_x

    
    def get_lr_y(self):
        """The y coordinate of the lower right corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._lr_y

    
    def get_ul_x(self):
        """The x coordinate of the upper left corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._ul_x

    
    def get_ul_y(self):
        """The y coordinate of the upper left corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._ul_y

    
    def get_ur_x(self):
        """The x coordinate of the upper right corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._ur_x

    
    def get_ur_y(self):
        """The y coordinate of the upper right corner of the coverage area.

        This is according to the projection returned by get_projection.
        """
        return self._ur_y

    
    def get_x_pixels(self):
        """The width of the dataset in pixels."""
        return self._x_size

    
    def get_y_pixels(self):
        """The height of the dataset in pixels."""
        return self._y_size

    
    def get_gcp_count(self):
        """The number of ground control points?"""
        return 0

    
    def get_mtl_text(self):
        """Text information?"""
        return ''

    
    def get_cloud_cover(self):
        """Percentage cloud cover of the aquisition if available."""
        return 0.0

    
    def get_xml_text(self):
        """XML metadata text for the dataset if available."""
        return ''

    #
    # Methods used for tiling
    #

    
    def get_geo_transform(self):
        """The affine transform between pixel and geographic coordinates.

        This is a list of six numbers describing a transformation between
        the pixel x and y coordinates and the geographic x and y coordinates
        in dataset's coordinate reference system.

        See http://www.gdal.org/gdal_datamodel for details.
        """
        return self._geo_transform


    
    def stack_bands(self, band_list):
        """Creates and returns a band_stack object from the dataset.

        band_list: a list of band numbers describing the bands to
        be included in the stack.

        PRE: The numbers in the band list must refer to bands present
        in the dataset. This method (or things that it calls) should
        raise an exception otherwise.

        POST: The object returned supports the band_stack interface
        (described below), allowing the datacube to chop the relevent
        bands into tiles.
        """

        return LandsatBandstack(self, self.band_dict)

        
        
