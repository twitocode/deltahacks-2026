
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from app.dem.dem_loader import MeritDEMLoader, CachedTile, DEMData

class TestDEMEdgeClipping(unittest.TestCase):
    def setUp(self):
        self.loader = MeritDEMLoader(data_dir=None, auto_download=False, cleanup_on_exit=False)
        
    @patch('app.dem.dem_loader.MeritDEMLoader.load_tile')
    def test_search_clipping_at_north_edge(self, mock_load_tile):
        """
        Test that a search extending past the north edge of a tile is clipped.
        """
        # Setup a mock tile at lat=50, lon=-116 (Bounds: 50.0 to 51.0)
        tile_lat, tile_lon = 50, -116
        
        # Create fake tile data (1 degree x 1 degree, 100x100 pixels for simplicity)
        data = np.zeros((100, 100), dtype=np.float32)
        transform = from_bounds(-116.0, 50.0, -115.0, 51.0, 100, 100)
        crs = CRS.from_epsg(4326)
        bounds = (-116.0, 50.0, -115.0, 51.0)
        
        mock_tile = CachedTile(data=data, transform=transform, crs=crs, bounds=bounds)
        mock_load_tile.return_value = mock_tile
        
        # Define a center point very close to the north edge (51.0)
        # Center at 50.99, Radius 2km (~0.018 deg lat)
        # Search would extend to ~51.008 (crossing the boundary)
        center_lat = 50.99
        center_lon = -115.5
        radius_km = 2.0
        
        # Execute search
        # This calls validate_single_tile -> we expect it to NOT raise ValueError now, 
        # but the loader's get_elevation_for_search handles the clipping.
        # Note: validate_single_tile checks if the RADIUS fits in a tile generally, 
        # but get_elevation_for_search handles the specific boundary logic now.
        # Actually, let's check if validate_single_tile raises. 
        # The previous implementation of validate_single_tile raised if it spanned tiles.
        # We modified get_elevation_for_search to handle this, but did we modify validate_single_tile?
        # Let's check the code: get_elevation_for_search calls validate_single_tile NO MORE.
        # Wait, I removed the call to validate_single_tile in the previous turn?
        # Let's re-verify the code change I made.
        
        result = self.loader.get_elevation_for_search(center_lat, center_lon, radius_km)
        
        # Assertions
        west, south, east, north = result.metadata.bounds
        
        # The north bound should be <= 51.0 (the tile edge)
        self.assertLessEqual(north, 51.0)
        
        # It should be close to 51.0 (clipped)
        self.assertAlmostEqual(north, 51.0, places=3)
        
        # Verify that we got data
        self.assertIsNotNone(result.elevation)
        print(f"\nTest passed: Bounds clipped to {north} (<= 51.0)")

    @patch('app.dem.dem_loader.MeritDEMLoader.load_tile')
    def test_search_clipping_at_east_edge(self, mock_load_tile):
        """Test clipping at east edge (-115.0)."""
        # Tile: 50, -116 (East edge is -115.0)
        tile_lat, tile_lon = 50, -116
        
        data = np.zeros((100, 100), dtype=np.float32)
        transform = from_bounds(-116.0, 50.0, -115.0, 51.0, 100, 100)
        crs = CRS.from_epsg(4326)
        bounds = (-116.0, 50.0, -115.0, 51.0)
        
        mock_tile = CachedTile(data=data, transform=transform, crs=crs, bounds=bounds)
        mock_load_tile.return_value = mock_tile
        
        # Center close to east edge
        center_lat = 50.5
        center_lon = -115.01 # Very close to -115.0
        radius_km = 5.0 # will definitely cross
        
        result = self.loader.get_elevation_for_search(center_lat, center_lon, radius_km)
        
        west, south, east, north = result.metadata.bounds
        
        self.assertLessEqual(east, -115.0)
        self.assertAlmostEqual(east, -115.0, places=3)
        print(f"Test passed: East bound clipped to {east} (<= -115.0)")

if __name__ == '__main__':
    unittest.main()
