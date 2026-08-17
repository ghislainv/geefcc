<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology" version="3.44.7-Solothurn">
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option name="name" type="QString" value=""/>
      <Option name="properties"/>
      <Option name="type" type="QString" value="collection"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling zoomedOutResamplingMethod="nearestNeighbour" enabled="false" zoomedInResamplingMethod="nearestNeighbour" maxOversampling="2"/>
    </provider>
    <rasterrenderer classificationMin="1" opacity="1" nodataColor="" classificationMax="6" type="singlebandpseudocolor" alphaBand="-1" band="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader colorRampType="EXACT" classificationMode="1" clip="0" labelPrecision="0" maximumValue="6" minimumValue="1">
          <colorramp name="[source]" type="gradient">
            <Option type="Map">
              <Option name="color1" type="QString" value="34,139,34,255,rgb:0.1333333,0.545098,0.1333333,1"/>
              <Option name="color2" type="QString" value="255,140,0,255,rgb:1,0.5490196,0,1"/>
              <Option name="direction" type="QString" value="ccw"/>
              <Option name="discrete" type="QString" value="0"/>
              <Option name="rampType" type="QString" value="gradient"/>
              <Option name="spec" type="QString" value="rgb"/>
              <Option name="stops" type="QString" value="0.2;227,26,28,255,rgb:0.8901961,0.1019608,0.1098039,1;rgb;ccw:0.4;30,100,200,255,rgb:0.1176471,0.3921569,0.7843137,1;rgb;ccw:0.55;100,160,230,255,rgb:0.3921569,0.627451,0.9019608,1;rgb;ccw:0.8;150,190,140,255,rgb:0.5882353,0.745098,0.5490196,1;rgb;ccw"/>
            </Option>
          </colorramp>
          <item label="1" color="#228b22" value="1" alpha="255"/>
          <item label="2" color="#e31a1c" value="2" alpha="255"/>
          <item label="3" color="#1e64c8" value="3" alpha="255"/>
          <item label="4" color="#64a0e6" value="3.75" alpha="255"/>
          <item label="5" color="#96be8c" value="5" alpha="255"/>
          <item label="6" color="#ff8c00" value="6" alpha="255"/>
          <rampLegendSettings minimumLabel="" prefix="" suffix="" maximumLabel="" direction="0" orientation="2" useContinuousLegend="1">
            <numericFormat id="basic">
              <Option type="Map">
                <Option name="decimal_separator" type="invalid"/>
                <Option name="decimals" type="int" value="6"/>
                <Option name="rounding_type" type="int" value="0"/>
                <Option name="show_plus" type="bool" value="false"/>
                <Option name="show_thousand_separator" type="bool" value="true"/>
                <Option name="show_trailing_zeros" type="bool" value="false"/>
                <Option name="thousand_separator" type="invalid"/>
              </Option>
            </numericFormat>
          </rampLegendSettings>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0" gamma="1"/>
    <huesaturation colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeOn="0" colorizeGreen="128" colorizeRed="255" invertColors="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
