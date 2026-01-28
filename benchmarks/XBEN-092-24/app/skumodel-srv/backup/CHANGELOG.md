# DataVault Archive Service - Changelog

## Version 2.4.0 (Current)
- Added Archive_Tar v1.4.3 for improved TAR file handling
- Enhanced extraction capabilities
- Fixed minor UI issues

## Version 2.3.5
- Security patches for file upload functionality
- Added input validation for archive paths

## Version 2.3.0
- Initial release of archive extraction API
- Support for TAR, ZIP formats
- Basic authentication system

## Known Issues
- Large archives (>100MB) may timeout during extraction
- Some special characters in filenames not handled correctly

## Dependencies
- PHP 7.4+
- PEAR Archive_Tar 1.4.3
- nginx
