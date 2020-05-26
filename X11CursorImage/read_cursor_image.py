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

# libX11 = CDLL('libX11.so')
# Load libXfixes.so library
libXFixes = CDLL('libXfixes.so')

# X display
display = XOpenDisplay(None)

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

# Call the function. Read data of cursor/mouse-pointer.
cursor_data = XFixesGetCursorImage(display)

# Success?
if not (cursor_data and cursor_data[0]):
    print "Cannot read XFixesGetCursorImage()"
    sys.exit(0)

# Note: cursor_data is a pointer, take cursor_data[0]
cursor_data = cursor_data[0]

# Check fields
print "cursor x=", cursor_data.x
print "cursor y=", cursor_data.y
print "cursor width=", cursor_data.width
print "cursor height=", cursor_data.height

# Convert array (of type long) to byte array suitable for gtk.gdk.Pixbuf.
bytearr = argbdata_to_pixdata(cursor_data.pixels, cursor_data.width * cursor_data.height)

# Create a pixbuf image from bytearr
cursor_image = gtk.gdk.pixbuf_new_from_data(bytearr, gtk.gdk.COLORSPACE_RGB, True, 8, cursor_data.width, cursor_data.height, cursor_data.width * 4)
del bytearr

if cursor_image == None:
    print "Cannot create cursor image"
    sys.exit(0)

# Save the cursor image to cursor1.png
cursor_image.save("cursor1.png", "png")

print "Done. gimp cursor1.png"


