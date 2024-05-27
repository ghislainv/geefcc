# Adjusted extent
xmin = aoi[0]
xmax = aoi[2]
xmax_tap = xmin + math.ceil((xmax - xmin) / scale) * scale
ymin = aoi[1]
ymax = aoi[3]
ymax_tap = ymin + math.ceil((ymax - ymin) / scale) * scale

# projWin = [ulx, uly, lrx, lry]
gdal.Translate(output_file, vrt_file,
               maskBand=None,
               projWin=[xmin, ymax_tap, xmax_tap, ymin],
               creationOptions=copts,
               callback=cback)
