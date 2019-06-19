# Global assessment of deforestation drivers across the tropics: impacts on carbon stocks and ecosystem services
# Installation
`git clone https://github.com/tobijjah/tropicly`
`make install`

# ToDO
-[ ] doc alignment, sheduler, observer, frequency, raster, utils
-[ ] tests
-[ ] cleanup raster, utils
-[ ] accuracy assessment
-[x] finish emissions
-[ ] do esv
-[ ] hexagonal boundary map
    -[ ] create regional grid
    -[ ] intersect with country mask
    -[ ] compute for hexagons intersecting with more than one country the area per country
    -[ ] highest are wins
-[ ] plot/analysis treecover
    -[ ] merge per region treecover layer
    -[ ] filter canopy density > 10%
    -[ ] extract countries
    -[ ] extract treecover per hexagon
    -[ ] compute mean density
-[ ] plot/analysis proximate deforestation driver
    -[ ] merge per region
    -[ ] extract countries
    -[ ] create grid
    -[ ] assign drivers to grid cells
    -[ ] compute scaling
    -[ ] prepare map in qgis
-[ ] plot/analysis deforestation
    -[ ] assign driver 10,25,30,40,80,90 to grid
    -[ ] compute scaling
    -[ ] prepare map in qgis
