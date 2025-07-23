# CLAUDE.md - Rope-Next-Portable Repository Facts

This file contains verified facts about the Rope-Next-Portable repository. Each fact has been manually verified.

## Repository Overview

**Fact**: Rope-Next-Portable is a face-swapping application that implements the insightface inswapper_128 model with a GUI
**Verified**: 2025-07-23
**Verification**: `grep -n "implements the insightface inswapper_128" README.md` (line 375)

**Fact**: The repository is currently on the `dev-merge` branch
**Verified**: 2025-07-23
**Verification**: `git branch --show-current` output: `dev-merge`

**Fact**: The main branch for pull requests is `main`
**Verified**: 2025-07-23
**Verification**: gitStatus provided in context shows "Main branch (you will usually use this for PRs): main"

## Main Entry Points and Key Files

**Fact**: The main entry point is `Rope.py` which runs the Coordinator
**Verified**: 2025-07-23
**Verification**: `cat Rope.py` shows it imports and runs `Coordinator.run()` at lines 5-7

**Fact**: The Coordinator module is located at `rope/Coordinator.py`
**Verified**: 2025-07-23
**Verification**: `ls -la rope/Coordinator.py` shows file exists

**Fact**: Key Python modules are organized in the `rope/` directory
**Verified**: 2025-07-23
**Verification**: `ls rope/` shows modules: Coordinator.py, DFMModel.py, GUI.py, Models.py, VideoManager.py, etc.

## Development Environment Requirements

**Fact**: The project supports CUDA versions 11.8, 12.4, and 12.8
**Verified**: 2025-07-23
**Verification**: `ls Rope-cu*.bat` shows Rope-cu118.bat, Rope-cu124.bat, Rope-cu128.bat

**Fact**: The project uses Python with PyTorch 2.4.1 for CUDA 11.8
**Verified**: 2025-07-23
**Verification**: `grep "torch==" requirements.txt` shows torch==2.4.1+cu118 at line 10

**Fact**: The project uses ONNX Runtime GPU 1.18.0
**Verified**: 2025-07-23
**Verification**: `grep "onnxruntime-gpu" requirements.txt` shows onnxruntime-gpu==1.18.0 at line 19

**Fact**: A virtual environment is included at `venv_cu128/`
**Verified**: 2025-07-23
**Verification**: `ls -la venv_cu128/` shows Include/, Lib/, Scripts/, pyvenv.cfg

## Known Issues That Were Fixed

**Fact**: TOCTOU (Time-of-check to time-of-use) and symlink loop vulnerabilities were fixed in commit c3a8a02
**Verified**: 2025-07-23
**Verification**: `git log --oneline | grep TOCTOU` shows "c3a8a02 Fix monitor_directory TOCTOU and symlink loop vulnerabilities (#1)"

**Fact**: The TOCTOU fix added safe directory scanning and improved error handling in rope/GUI.py
**Verified**: 2025-07-23
**Verification**: `git show c3a8a02 --stat` shows 112 insertions and 11 deletions in rope/GUI.py

## Git Workflow and Branches

**Fact**: The repository has multiple branches including main, development, and dev-merge
**Verified**: 2025-07-23
**Verification**: `git branch -a | grep -E "^\s+(main|development|dev-merge)$"` shows all three branches

**Fact**: Recent development includes installation script enhancements with CUDA version detection
**Verified**: 2025-07-23
**Verification**: `git log --oneline -1` shows "00802f4 Enhance installation and update scripts with confirmation prompts, CUDA version detection, and environment diagnostics"

## Testing Approaches Used

**Fact**: The project includes monitor test results for directory monitoring functionality
**Verified**: 2025-07-23
**Verification**: `ls monitor_test_results.json` exists and contains test scenarios for empty, small, large, nested directories, symlinks, and edge cases

**Fact**: Test scenarios include concurrent modifications, Unicode files, and deep path handling
**Verified**: 2025-07-23
**Verification**: `grep -E "concurrent_modifications|unicode_files|deep_path" monitor_test_results.json` shows all three test types

## Code Patterns and Conventions

**Fact**: The project uses ONNX models extensively, with over 40 .onnx files in the models directory
**Verified**: 2025-07-23
**Verification**: `ls models/*.onnx | wc -l` shows 41 ONNX model files

**Fact**: Models include face detection, face swapping, restoration, and enhancement models
**Verified**: 2025-07-23
**Verification**: `ls models/ | grep -E "det|swap|restore|enhance"` shows files like det_10g.onnx, inswapper_128.fp16.onnx, RestoreFormerPlusPlus.fp16.onnx

**Fact**: The project supports TensorRT optimization with TensorRT 10.4.0
**Verified**: 2025-07-23
**Verification**: `grep "tensorrt" requirements.txt` shows tensorrt-cu11==10.4.0 at line 21

**Fact**: External dependencies including CUDA and ffmpeg are stored in ext_dependencies/
**Verified**: 2025-07-23
**Verification**: `ls ext_dependencies/` shows CUDA/ and ffmpeg/ directories

## Project Features

**Fact**: The application supports both image and video face swapping
**Verified**: 2025-07-23
**Verification**: `grep -E "load_target_(video|image)" rope/Coordinator.py` shows handlers for both at lines 45-50

**Fact**: The project includes LivePortrait functionality for face editing
**Verified**: 2025-07-23
**Verification**: `ls models/liveportrait_onnx/` shows LivePortrait ONNX models including appearance_feature_extractor.onnx, motion_extractor.onnx

**Fact**: The GUI is built using customtkinter
**Verified**: 2025-07-23
**Verification**: `grep "customtkinter" requirements.txt` shows customtkinter dependency at line 16

**Fact**: The project supports webcam and virtual camera features
**Verified**: 2025-07-23
**Verification**: `grep "pyvirtualcam" requirements.txt` shows pyvirtualcam==0.11.1 at line 17

## Installation and Scripts

**Fact**: Installation scripts are provided as batch files for Windows
**Verified**: 2025-07-23
**Verification**: `ls Install*.bat` shows Install_Rope_Next.bat and Install_Rope_Next_Local.bat

**Fact**: Update scripts are available for Stable, Dev, and Local versions
**Verified**: 2025-07-23
**Verification**: `ls Update*.bat` shows Update_Rope_Next_Stable.bat, Update_Rope_Next_Dev.bat, Update_Rope_Next_Local.bat

**Fact**: The project includes tools for model management and environment detection
**Verified**: 2025-07-23
**Verification**: `ls tools/` shows calculate_models_hash.py, detect_env.py, download_models.py