import numpy as np
from rasterio import open
from rasterio.features import rasterize
from rasterio.features import shapes
from shapely.geometry import Polygon

from tropicly.distance import Distance
from tropicly.frequency import most_common_class
from tropicly.raster import write


# TODO doc
# TODO refactor exceptions


def worker(landcover, treecover, gain, loss, filename):
    """
    Worker function for parallel execution.

    :param landcover: str
        Path to GL30 landcover image.
    :param treecover: str
        Path to GFC treecover image.
    :param gain: str
        Path to GFC gain image.
    :param loss: str
        Path to GFC annual loss image.
    :param filename: str
        Out path.
    """
    with open(landcover, 'r') as h1, open(treecover, 'r') as h2,\
            open(gain, 'r') as h3, open(loss, 'r') as h4:
        landcover_data = h1.read(1)
        treecover_data = h2.read(1)
        gain_data = h3.read(1)
        loss_data = h4.read(1)

        transform = h1.transform
        profile = h1.profile

    haversine = Distance('hav')
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))

    driver = superimpose(landcover_data, treecover_data, gain_data, loss_data)

    reclassified = reclassify(driver, res=(x, y))

    np.copyto(driver, reclassified, where=reclassified > 0)

    write(driver, filename, **profile)


def superimpose(landcover, treecover, gain, loss, years=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), canopy_density=10):
    """
    Determines the proximate drivers of deforestation. Superimposes GL30 with
    filtered GFC annual losses.

    :param landcover: np.array
        Gl30 image data
    :param treecover: np.array
        GFC treecover data
    :param gain: np.array
        GFC gain data
    :param loss: np.array
        GFC annual loss data
    :param years: list, tuple of int
        Years to consider for superimposing.
        Default is (1, 2, 3, 4, 5, 6, 7, 8, 9, 10).
    :param canopy_density: int
        Canopy density to consider.
        Selects all densities >canopy_density, so
        it is a exclusive selection
    :return: np.array
        Proximate driver of deforestation image
    """
    shape = [landcover.shape, treecover.shape, gain.shape, loss.shape]

    if len(set(shape)) > 1:
        raise ValueError

    losses = (treecover > canopy_density) & np.isin(loss, years)

    driver = losses * landcover
    driver[(losses & gain) == 1] = 25

    return driver


def reclassify(driver, clustering=(20,), reject=(0, 20, 255), side_length=500, res=(1, 1)):
    """
    Reclassify pixels in a raster image by the following approach:
    - Cluster pixels, parameter clustering determines which pixels should be interpreted as occupied
    - Create square shaped buffer of parameter side_length size around cluster centroid
    - Count most frequent class within buffer under exclusion of values in parameter reject
    - Reassign cluster to most frequent class
    - Parameter res defines the real world - image coordinates conversion (side_length / res)
        Example: res=1,1, side_length=500
                 buffer=500 pixel * 500 pixel

    :param driver: np.array
        A 2-dimensional integer numpy array.
    :param clustering: tuple, list of int
        Values to cluster.
    :param reject: tuple, list of int
        Values to reject for reclassification.
    :param side_length: int
        Square buffer side length.
    :param res: int or tuple(int, int)
        Real world pixel resolution.
    :return: np.array
        A array of reclassified clusters in
        dimension of input array.
    """
    mask = np.isin(driver, clustering)

    clusters = []
    for cluster, _ in shapes(driver, mask=mask):
        polygon = Polygon(cluster['coordinates'][0])
        point = polygon.centroid
        center = int(point.y), int(point.x)

        LOGGER.debug('Cluster centroid at (%s, %s)', int(point.x), int(point.y))

        buffer = extract_square(driver, center, side_length, res)

        LOGGER.debug('Buffer size (%s, %s)', buffer.shape[0], buffer.shape[1])

        mc = most_common_class(buffer, reject)

        if mc:
            cls, count = mc
            clusters.append((cluster, cls))

    if clusters:
        return rasterize(clusters, out_shape=driver.shape, dtype=driver.dtype)

    return np.zeros(shape=driver.shape, dtype=driver.dtype)


def extract_square(data, center, side_length=None, res=None):
    """
    Extracts a square from a numpy array around a center point.

    :param data: 2D np.array
        Square is extracted from this array.
    :param center: 2D tuple of int
        Center row and column coordinate of the square.
    :param side_length: int
        Side length in cell scaling or side length in real world
        distance.
    :param res: numeric or 2D tuple of int
        Real world resolution of the pixels. Must be in the same
        scaling as block length. Can be a single int or float for
        square sized pixels or a tuple of x and y length of the pixel.
    :return: np.array
        Numpy array in extent of side_length or block_length.
    """
    if side_length and res:
        if isinstance(res, (int, float)):
            x_res, y_res = res, res
        else:
            x_res, y_res = res

        # convert real world length to image length
        x_block_size = round(side_length / x_res)
        y_block_size = round(side_length / y_res)

        x_edge = round(0.5 * (x_block_size - 1))
        y_edge = round(0.5 * (y_block_size - 1))

    elif side_length:
        x_edge = int(0.5 * (side_length - 1))
        y_edge = int(0.5 * (side_length - 1))

    else:
        raise ValueError

    LOGGER.debug('Edge length (%s, %s)', x_edge, y_edge)

    row, col = center
    max_row, max_col = data.shape

    row_start = 0 if row - y_edge < 0 else row - y_edge
    row_end = max_row if row + y_edge > max_row else row + y_edge + 1

    col_start = 0 if col - x_edge < 0 else col - x_edge
    col_end = max_col if col + x_edge > max_col else col + x_edge + 1

    return data[row_start:row_end, col_start:col_end]
