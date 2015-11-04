#!/usr/bin/python

#===============================================================================
# Copyright 2015 Geoscience Australia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

# Purpose: This program builds a PQA for Datacube from Landsat 7 surface reflectance products
# Usage: python build_pqa.py <sceneID>
# Example: python build_pqa.py LE71130802015092ASA00
# Input: Requires 5 surface reflectance masks
# Output: PQA file
# Tested: On LS5 surface reflectance products

import sys
import subprocess
import os, errno
import os.path
import numpy as np
from osgeo import gdal, gdal_array

if len(sys.argv) < 2:
	print 'SceneId not entered'
	print 'Usage: python build_pqa.py <sceneID>'
	print 'Example: python build_pqa.py LE71130802015092ASA00'
	sys.exit(0)
else:
	sceneID = str(sys.argv[1])
	sr_band1 = sceneID+'_sr_band1.tif'
	fill_qa = sceneID+'_sr_fill_qa.tif'
	land_water_qa = sceneID+'_sr_land_water_qa.tif'
	cloud_qa = sceneID+'_sr_cloud_qa.tif'
	cfmask = sceneID+'_cfmask.tif'
	cloud_shadow_qa = sceneID+'_sr_cloud_shadow_qa.tif'
	vrt_stack = sceneID+'_stack.vrt'
	pqa = sceneID+'_PQA_1111111111111100.tif'

	if os.path.exists(sr_band1) & os.path.exists(fill_qa) & os.path.exists(land_water_qa) & os.path.exists(cloud_qa) & os.path.exists(cfmask) & os.path.exists(cloud_shadow_qa):
		print 'Started creating PQA for sceneID', sceneID

		# Create a stack of all the required masks
		print 'Building VRT from surface reflectance masks'
		subprocess.call(["gdalbuildvrt", "-separate", "-overwrite", vrt_stack, fill_qa, land_water_qa,cloud_qa, cfmask, cloud_shadow_qa])

		# Read data from the VRT stack
		print 'Reading data from the VRT'
		ds = gdal.Open(vrt_stack)

		# Bit#8: Contiguity. Non-contiguous =0; Clear=1
		# In sr_fill_qa, Fill is 255, Not Fill is 0
		b08 = np.array(ds.GetRasterBand(1).ReadAsArray())
		b08[b08==0]=1
		b08[b08==255]=0

		# Bit#9: Land/Water. Water =0; Land=1
		# In sr_land_water_qa, Water is 255, Land is 0
		b09 = np.array(ds.GetRasterBand(2).ReadAsArray())
		b09[b09==0]=1
		b09[b09==255]=0

		# Bit#10: ACCA. Cloud =0; Clear=1
		# In sr_cloud_qa, Cloud is 255, Clear is 0
		b10 = np.array(ds.GetRasterBand(3).ReadAsArray())
		b10[b10==0]=1
		b10[b10==255]=0

		# Bit#11: FMASK. Cloud =0; Clear=1
		# In CFMASK, Cloud is 4.
		b11 = np.array(ds.GetRasterBand(4).ReadAsArray())
		b11[b11==255]=1
		b11[b11==0]=1
		b11[b11==2]=1
		b11[b11==3]=1
		b11[b11==4]=0

		# Bit#12: Cloud Shadow (ACCA). Cloud Shadow =0; Clear=1
		# In sr_cloud_shadow_qa, Cloud Shadow is 255, Clear is 0
		b12 = np.array(ds.GetRasterBand(5).ReadAsArray())
		b12[b12==0]=1
		b12[b12==255]=0

		# Bit#13: Cloud Shadow (FMASK). Cloud Shadow =0; Clear=1
		# In CFMASK, Cloud Shadow is 2.
		b13 = np.array(ds.GetRasterBand(4).ReadAsArray())
		b13[b13==255]=1
		b13[b13==0]=1
		b13[b13==3]=1
		b13[b13==4]=1
		b13[b13==2]=0

		# Compute PQA values
		print 'Computing PQA values'
		# Surface Reflectance products do not have any saturated pixel
		# Therefore, the bits 0 through 7 are set to 1
		# The binary of 11111111 is 255, which is added in the pqa_array below
		# Bit 14 and bit 15 are unused

		pqa_array = 255 + 256*b08 + 512*b09 + 1024*b10 + 2048*b11 + 4096*b12 + 8192*b13

		# Remove any previous PQA file
		try:
		    os.remove(pqa)
		except OSError:
		    pass

		# Save the PQA file
		print 'Saving the PQA file'
		gdal_array.SaveArray(pqa_array.astype("int"), pqa , "GTiff", sr_band1)

		# Perform clean-up
		print 'Cleaning-up before exiting'
		try:
		    os.remove(vrt_stack)
		except OSError:
		    pass
	else:
		print 'One or more Surface Reflectance mask(s) are missing for sceneID', sceneID
		
