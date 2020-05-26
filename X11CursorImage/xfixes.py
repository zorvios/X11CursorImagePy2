# Calling libXfixes.so by using Python's ctypes modules.
# By: Osmo (moma) Antero M.
import sys
import ctypes
import gtk

# Note: I downloaded x.py and xlib.py from http://code.google.com/p/pyxlib-ctypes/
# It has some predefined data types.
# I will later cut & paste only those things this module needs.
from x import *
from xlib import *

# Load libXfixes.so library
libXFixes = CDLL('libXfixes.so.3')

# A helper function to convert data from Xlib to byte array, suitable for gdk.Pixbuf.
import struct, array
def argbdata_to_pixdata(data,  len):
	if data == None or len < 1: return None

	# Create byte array
	# Ref: http://docs.python.org/library/array.html
	b = array.array('b', '\0'* len*4)	

	offset = 0
	i = 0
	offset = 0
	while i < len:
		argb = data[i] & 0xffffffff
		rgba = (argb << 8) | (argb >> 24)
		b1 = (rgba >> 24)  & 0xff
		b2 = (rgba >> 16) & 0xff
		b3 = (rgba >> 8) & 0xff
		b4 = rgba & 0xff

		# Ref: http://docs.python.org/dev/3.0/library/struct.html
		struct.pack_into("=BBBB", b, offset, b1, b2, b3, b4)
		offset = offset + 4
		i = i + 1

	return b 


# Define ctypes version of XFixesCursorImage structure.
PIXEL_DATA_PTR = POINTER(c_ulong)

class XFixesCursorImage (ctypes.Structure):
    """ 
    See /usr/include/X11/extensions/Xfixes.h

    typedef struct {
        short	    x, y;
        unsigned short  width, height;
        unsigned short  xhot, yhot;
        unsigned long   cursor_serial;
        unsigned long   *pixels;
    if XFIXES_MAJOR >= 2
        Atom	    atom;	/* Version >= 2 only */
        const char	*name;	/* Version >= 2 only */
    endif
    } XFixesCursorImage;
    """
    _fields_ = [('x', ctypes.c_short),
                ('y', ctypes.c_short),
                ('width', ctypes.c_ushort),
                ('height', ctypes.c_ushort),
                ('xhot', ctypes.c_ushort),
                ('yhot', ctypes.c_ushort),
                ('cursor_serial', ctypes.c_ulong),
                ('pixels', PIXEL_DATA_PTR),
                ('atom', Atom),
                ('name', ctypes.c_char_p)]

# Define ctypes' version of XFixesGetCursorImage function
XFixesGetCursorImage = libXFixes.XFixesGetCursorImage
XFixesGetCursorImage.restype = ctypes.POINTER(XFixesCursorImage)
XFixesGetCursorImage.argtypes = [ctypes.POINTER(Display)]


XFixesHideCursor = libXFixes.XFixesHideCursor
XFixesHideCursor.restype = None
XFixesHideCursor.argtypes = [ctypes.POINTER(Display), Window]

XFixesShowCursor = libXFixes.XFixesShowCursor
XFixesShowCursor.restype = None
XFixesShowCursor.argtypes = [ctypes.POINTER(Display), Window]



