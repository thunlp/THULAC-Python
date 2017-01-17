import sys
import thulac

seg_only = False

if(len(sys.argv) >= 4 and sys.argv[3] == "-seg_only"):
	seg_only = True
lac = thulac.thulac(seg_only=seg_only)
lac.cut_f(sys.argv[1], sys.argv[2])