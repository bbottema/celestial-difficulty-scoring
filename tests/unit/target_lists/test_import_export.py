"""
Unit tests for target list import/export.

Phase 9.2: CSV import/export functionality.
"""
import pytest
import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime
from unittest.mock import Mock, patch

from app.orm.model.entities import TargetList, TargetListItem
from app.target_lists.import_export import TargetListImportExport


class TestTargetListExport:
    """Tests for CSV export."""

    def test_export_csv_creates_file(self):
        """Test that export_csv creates a CSV file."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_export.csv"
            
            # Create mock target list
            target_list = Mock(spec=TargetList)
            target_list.items = [
                Mock(
                    object_name="M31",
                    canonical_id="NGC0224",
                    object_type="galaxy",
                    ra=10.68,
                    dec=41.27,
                    magnitude=3.44,
                    observed=True,
                    observed_date=datetime(2026, 2, 15, 22, 30),
                    notes="Beautiful spiral arms visible"
                ),
                Mock(
                    object_name="M42",
                    canonical_id="NGC1976",
                    object_type="nebula",
                    ra=83.82,
                    dec=-5.39,
                    magnitude=4.0,
                    observed=False,
                    observed_date=None,
                    notes=None
                )
            ]
            
            # Export
            exporter = TargetListImportExport()
            exporter.export_csv(target_list, filepath)
            
            # Verify file exists
            assert filepath.exists()
            
            # Verify content
            with open(filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 2
            assert rows[0]['Name'] == 'M31'
            assert rows[0]['Type'] == 'galaxy'
            assert rows[0]['Observed'] == 'Yes'
            assert rows[1]['Name'] == 'M42'
            assert rows[1]['Observed'] == 'No'

    def test_export_simple_csv(self):
        """Test simple CSV export with just names."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "simple.csv"
            
            target_list = Mock(spec=TargetList)
            target_list.items = [
                Mock(object_name="M31"),
                Mock(object_name="M42"),
                Mock(object_name="M45")
            ]
            
            exporter = TargetListImportExport()
            exporter.export_simple_csv(target_list, filepath)
            
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 3
            assert rows[0]['Name'] == 'M31'
            assert rows[2]['Name'] == 'M45'


class TestTargetListImport:
    """Tests for CSV import."""

    def test_import_csv_with_name_column(self):
        """Test importing CSV with 'Name' column."""
        with TemporaryDirectory() as tmpdir:
            # Create test CSV
            filepath = Path(tmpdir) / "import.csv"
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Type', 'Magnitude'])
                writer.writerow(['M31', 'galaxy', '3.44'])
                writer.writerow(['M42', 'nebula', '4.0'])
            
            # Mock services
            mock_service = Mock()
            mock_list = Mock(spec=TargetList)
            mock_list.id = 1
            mock_list.object_count = 2
            mock_service.create_list.return_value = mock_list
            mock_service.get_list.return_value = mock_list
            
            mock_catalog = Mock()
            mock_catalog.get_object.return_value = None  # All fail resolution
            
            # Import
            importer = TargetListImportExport(
                target_list_service=mock_service,
                catalog_service=mock_catalog
            )
            
            # Mock the _add_unresolved_item to avoid DB access
            with patch.object(importer, '_add_unresolved_item') as mock_add:
                result, failed = importer.import_csv(filepath, "My Import")
                
                # Verify
                mock_service.create_list.assert_called_once()
                assert len(failed) == 2  # Both failed resolution
                assert mock_add.call_count == 2  # Both added as unresolved

    def test_import_csv_with_object_column(self):
        """Test importing CSV with 'Object' column instead of 'Name'."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "import.csv"
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Object', 'RA', 'Dec'])
                writer.writerow(['NGC 224', '10.68', '41.27'])
            
            mock_service = Mock()
            mock_list = Mock(spec=TargetList)
            mock_list.id = 1
            mock_list.object_count = 1
            mock_service.create_list.return_value = mock_list
            mock_service.get_list.return_value = mock_list
            
            mock_catalog = Mock()
            mock_catalog.get_object.return_value = None
            
            importer = TargetListImportExport(
                target_list_service=mock_service,
                catalog_service=mock_catalog
            )
            
            # Mock the _add_unresolved_item to avoid DB access
            with patch.object(importer, '_add_unresolved_item') as mock_add:
                result, failed = importer.import_csv(filepath, "Test")
                
                # Should work with 'Object' column
                assert mock_service.create_list.called
                assert mock_add.call_count == 1

    def test_import_csv_missing_name_column_raises_error(self):
        """Test that CSV without name column raises ValueError."""
        with TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "bad.csv"
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['RA', 'Dec', 'Magnitude'])
                writer.writerow(['10.68', '41.27', '3.44'])
            
            mock_service = Mock()
            mock_catalog = Mock()
            
            importer = TargetListImportExport(
                target_list_service=mock_service,
                catalog_service=mock_catalog
            )
            
            with pytest.raises(ValueError, match="must have a 'Name'"):
                importer.import_csv(filepath, "Test")
