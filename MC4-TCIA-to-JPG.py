# this script uses the TCIA Pancreas DICOM data plus hand tracings
# it outputs zipped (and original) JPEG images with non-zero masks for pancreas

import pydicom
import numpy as np
#import PIL
import os
from scipy.misc import imread, imresize, imsave
import imageio

import math
import nibabel as nib

TYPE = '.jpg'
MAX_IMAGES = 10000


def nifti_to_img(f, mask_f, out_dir, subject_ID):
    try:
        nifti = nib.load(f)
        nif_header = nifti.header
        image = nifti.get_fdata()
        # Now load mask
        nif_mask = nib.load(mask_f)
        mask_image = nif_mask.get_fdata()
    except:
        return 0

#    image = slope * image + intercept
# Now apply Abd Window / Level = -40 to +350
    image += 40
    image *= 255.0/350.0
    np.clip(image, 0., 255.0, out=image)
# Convert to Bytes
    image = image.astype(np.uint8)
    if np.max(mask_image) < 2:
        mask_image = mask_image * 255.0
    mask_image = mask_image.astype(np.uint8)
    image = np.rot90(image)
    mask_image = np.rot90(mask_image)
    
    dims = np.shape(image)
    xd = dims[0]
    yd = dims[1]
    zd = dims[2]
    # mask image seems to be z-zflipped, so flip it back
    mask_image = mask_image[:, :, ::-1]
    for z in range(0, zd):
        image_2d = image[:,:,z]
        mask_2d = mask_image[:,:,z]
        if not np.all(mask_2d==0):  # see if any non-zero values
            outname = subject_ID + "-{0:05d}".format(z) + TYPE
            outname = os.path.join(out_dir, outname)
            imageio.imwrite(outname, image_2d)
            outname = subject_ID + "-{0:05d}-Mask".format(z) + TYPE
            outname = os.path.join(out_dir, outname)
            imageio.imwrite(outname, mask_2d)
    return

cmd = '/Users/bje01/anaconda3/envs/keras/bin/dicom2nifti'

def convert_files(subjDir):
    list = []
    for dirName, subdirList, fileList in os.walk(subjDir, topdown=False):
        if '000000.dcm' in fileList:  # find the first dicom in this dir
            full_command = cmd + ' ' + dirName + ' ' + subjDir
            os.system (full_command)
    return True

in_dir = '/Users/bje01/Desktop/TCIA-Pancreas/DICOM/'

# First convert all the DICOMs to NIfTI
for subj in os.listdir(in_dir):
    convert_files (os.path.join(in_dir, subj))

# Now load each NIfTI and corresponding mask file
# and write out JPGs for the image and mask that have pancreas
# filename is Subj-Slc.jpg and Subj-Slc-Mask.jpg
out_dir = '/Users/bje01/Desktop/TCIA-Pancreas/Prepped/'
for subj in os.listdir(in_dir):
    ID = subj[-4:]
    print (ID)
    img_f = in_dir + subj + "/_pancreas.nii.gz"
    mask_f = "/Users/bje01/Desktop/TCIA-Pancreas/Masks/label{}.nii.gz".format(ID)
    nifti_to_img(img_f, mask_f, out_dir, ID)
    os.chdir('/Users/bje01/Desktop/TCIA-Pancreas/Prepped/')
    cmd = 'zip Subj'+ID+'.zip '+ID+'*'
    os.system (cmd)
    
    
print ("Done")
