<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.18.26" minimumScale="inf" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <pipe>
    <rasterrenderer opacity="1" alphaBand="-1" classificationMax="100" classificationMinMaxOrigin="User" band="1" classificationMin="0" type="singlebandpseudocolor">
      <rasterTransparency/>
      <rastershader>
        <colorrampshader colorRampType="INTERPOLATED" clip="0">
          <item alpha="255" value="0" label="Nodata" color="#000000"/>
          <item alpha="255" value="10" label="Cropland" color="#ff7f00"/>
          <item alpha="255" value="20" label="Forest" color="#33a02c"/>
          <item alpha="255" value="25" label="Regrowth" color="#52ff46"/>
          <item alpha="255" value="30" label="Grassland" color="#b2df8a"/>
          <item alpha="255" value="40" label="Shrubland" color="#cab2d6"/>
          <item alpha="255" value="50" label="Wetland" color="#a6cee3"/>
          <item alpha="255" value="60" label="Water" color="#1f78b4"/>
          <item alpha="255" value="70" label="Tundra" color="#fb9a99"/>
          <item alpha="255" value="80" label="Artificial" color="#e31a1c"/>
          <item alpha="255" value="90" label="Bareland" color="#fdbf6f"/>
          <item alpha="255" value="100" label="Ice" color="#ffffff"/>
          <item alpha="255" value="255" label="Nodata" color="#000000"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
