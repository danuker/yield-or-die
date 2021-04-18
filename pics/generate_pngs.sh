# In order to have high quality graphics, we work with SVG.
# However, Pygame does not support it, so we have to convert to PNG.
# This script takes all SVG files in the current directory, and generates PNGs from them.
# Requires imagemagick (which includes mogrify)
# Note: This is not a runtime dependency. You only need this to regenerate the PNGs after editing.

echo "Generating PNGs in ./pngs/ ..."

# -background none: do not fill with white background
mogrify -path pngs/ -background none -format png *.svg

# Generate tilted versions of the signs
# My right
convert  pngs/*-ahead.png -affine 1,.3,0,1,0,0 -transform -crop 512x512+0+75 -set filename:f "pngs/%[t]-right" "%[filename:f].png"

# My left
convert  pngs/*-ahead.png -affine 1,-.3,0,1,0,0 -transform -crop 512x512+0-75  -set filename:f "pngs/%[t]-left" "%[filename:f].png"

echo "Done!"
