# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.0.2] - 2023-05-17

### Added

- Project setup, build, test, publish framework
- Added environemnt variables for circlci publish test/publish ci workflow

## [0.0.3] - 2023-05-17

### Added

- Continuing testing ci workflow issues.  In this commit we test correctly
  updating the version and using a pull request.  We will pull this
  code to a develop branch.  Whenever a commit is made/pulled to this branch,
  it should invoke the ci workflow that does a build_test and
  then does the test_pypi_publish.  We hopefully now have our password
  issues worked out for twine.

## [0.0.4] - 2023-05-17

### Added

- Added basic function to load time series and joint graph information.
- These function currently perform some basic parsing and error checking.
- Added test of goot parses of these files, still should add additional
  testing of error conditions on bad file inputs.

## [0.0.5] - 2023-05-17

### Added

- Added skeleton of plot functions meant to plot a single frame and/or plot a
  motion track as a figure at some point in time
- Added skeleton of render functions.  These return an animation object that can be
  saved as a movie file or other video type.  NOTE: not sure if the animation
  uses ffmpeg on back end or that is not a dependency anymore.

## [0.1.0] - 2023-05-17

### Added

- First significant milestone, minimal functionality for the module.  Mark
  and label as version 0.1
