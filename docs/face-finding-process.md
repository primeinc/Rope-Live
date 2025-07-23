# Face Finding and Display Process Documentation

## Overview

This document provides a comprehensive technical analysis of the face finding and display process in Rope-Next-Portable. The process involves multiple stages from UI interaction through face detection, recognition, similarity matching, and final display.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Process Flow Overview](#process-flow-overview)
3. [Key Components](#key-components)
4. [Parameter Analysis](#parameter-analysis)
5. [Implementation Details](#implementation-details)
6. [Design Decisions](#design-decisions)
7. [Best Practices](#best-practices)

## System Architecture

The face finding system consists of several interconnected components:

- **GUI Layer** (`rope/GUI.py`): Handles user interactions and display
- **Models Layer** (`rope/Models.py`): Manages AI model inference
- **Video Manager** (`rope/VideoManager.py`): Processes video frames
- **Face Utilities** (`rope/FaceUtil.py`): Face transformation utilities

## Process Flow Overview

### 1. UI Interaction Flow

When a user clicks the "Find Faces" button:

```
User Click → on_click_find_faces_button() → Check AutoSwap State
    ├─ If AutoSwap ON  → clear_target_faces() → auto_swap()
    └─ If AutoSwap OFF → find_faces()
```

### 2. Face Finding Pipeline

The `find_faces()` method executes the following pipeline:

1. **Image Preparation**
   - Convert current frame to PyTorch tensor
   - Remove alpha channel if present
   - Permute dimensions for model input (HWC → CHW)

2. **Face Detection** (`Models.run_detect()`)
   - Apply rotation angles based on AutoRotationSwitch
   - Run selected detection model (Retinaface/SCRDF/Yolov8/Yunet)
   - Return bounding boxes and 5-point landmarks

3. **Face Recognition** (`Models.run_recognize()`)
   - Crop and align faces using landmarks
   - Extract 512-dimensional embeddings
   - Return embeddings and cropped images

4. **Similarity Matching**
   - Compare new faces with existing found faces
   - Apply similarity threshold
   - Group or separate faces based on threshold

5. **Display Update**
   - Create UI buttons for new unique faces
   - Update canvas with face thumbnails

## Key Components

### Face Detection Models

| Model | File | Use Case |
|-------|------|----------|
| Retinaface | `det_10g.onnx` | High accuracy, default option |
| SCRDF | `scrfd_2.5g_bnkps.onnx` | Faster detection |
| Yolov8 | `yoloface_8n.onnx` | Modern architecture |
| Yunet | `yunet_n_640_640.onnx` | Lightweight option |

### Face Recognition Models

| Model | File | Output |
|-------|------|--------|
| ArcFace | `w600k_r50.onnx` | 512-dim embedding |
| SimSwap | `simswap_arcface_model.onnx` | Alternative embedding |
| GhostFace | `ghost_arcface_backbone.onnx` | Ghost model embedding |

### Similarity Calculation

The cosine similarity is calculated as:

```python
def findCosineDistance(self, vector1, vector2):
    vector1 = vector1.ravel()
    vector2 = vector2.ravel()
    cos_dist = 1 - np.dot(vector1, vector2)/(np.linalg.norm(vector1)*np.linalg.norm(vector2))
    return 100 - cos_dist * 50  # Convert to 0-100 scale
```

This converts cosine distance (0-2 range) to a similarity score (0-100 range).

## Parameter Analysis

### 1. Similarity Threshold (`ThresholdSlider`)

**Range**: 0-100 (default: 55)

**Purpose**: Controls face grouping sensitivity

**Effects**:
- **Higher values (>70)**: Stricter matching
  - Treats similar faces as different people
  - Reduces face hopping in videos
  - May create duplicate entries for same person
  
- **Lower values (<40)**: Looser matching
  - Groups similar faces together
  - Better for tracking same person across frames
  - May incorrectly group different people

**Design Rationale**: In video processing, the same person's face can vary significantly between frames due to:
- Lighting changes
- Expression variations
- Angle differences
- Motion blur

The threshold allows users to balance between stability (grouping same person) and accuracy (separating different people).

### 2. Detection Score (`DetectScoreSlider`)

**Range**: 1-100 (default: 50)

**Purpose**: Minimum confidence for face detection

**Effects**:
- **Higher values (>70)**: 
  - Requires clearer, higher quality faces
  - Reduces false positives
  - May miss valid faces at extreme angles
  
- **Lower values (<30)**:
  - Detects more faces including partial/unclear ones
  - Increases false positives
  - Better coverage but less accuracy

**Design Rationale**: Provides quality control to filter out low-confidence detections that often aren't real faces or are too poor quality for reliable swapping.

### 3. Auto Rotation (`AutoRotationSwitch`)

**Values**: On/Off (default: Off)

**Purpose**: Enable multi-angle face detection

**Effects**:
- **ON**: Tries 4 rotations (0°, 90°, 180°, 270°)
  - Finds faces at different orientations
  - 4x processing time
  - Better for photos with rotated faces
  
- **OFF**: Only detects upright faces
  - Faster processing
  - Suitable for standard video content

**Design Rationale**: Many photos/videos contain faces at various angles. Auto-rotation ensures all faces are detected regardless of orientation.

### 4. Max Faces (`MaxFacesSlider`)

**Range**: 1-30 (default: 20)

**Purpose**: Limit faces processed per frame

**Effects**:
- Performance optimization
- Memory management
- Prevents system overload in crowded scenes

**Design Rationale**: Processing many faces is computationally expensive. This limit ensures reasonable performance while handling typical use cases.

### 5. Similarity Type (`SimilarityTypeTextSel`)

**Options**: Default, Optimal, Pearl

**Purpose**: Face alignment algorithm selection

**Effects**:
- **Default**: Standard ArcFace alignment
- **Optimal**: Best quality, uses advanced warping
- **Pearl**: Modified alignment with offset

**Design Rationale**: Different alignment methods work better for different face types and angles. Options allow users to choose based on their content.

## Implementation Details

### Face Detection Process (rope/Models.py:188)

```python
def run_detect(self, img, detect_mode='Retinaface', max_num=1, score=0.5, 
               use_landmark_detection=False, landmark_detect_mode='203', 
               landmark_score=0.5, from_points=False, rotation_angles=[0]):
```

The detection process:
1. Loads appropriate ONNX model based on detect_mode
2. Applies rotation transformations if specified
3. Runs inference with confidence threshold
4. Returns bounding boxes and landmarks

### Face Recognition Process (rope/Models.py:412)

```python
def run_recognize(self, img, kps, similarity_type='Opal', 
                  face_swapper_model='Inswapper128'):
```

The recognition process:
1. Aligns face using 5-point landmarks
2. Normalizes to 112x112 image
3. Runs through recognition model
4. Returns 512-dimensional embedding

### Similarity Matching Logic (rope/GUI.py:2634)

```python
for emb in self.target_faces:
    if self.findCosineDistance(emb['Embedding'], face[1]) >= threshold:
        found = True
        break
```

For each detected face:
1. Compare with all previously found faces
2. If similarity >= threshold, consider same person
3. If no match found, add as new unique face

## Design Decisions

### 1. Why Use Cosine Similarity?

Cosine similarity is ideal for face embeddings because:
- Embeddings are normalized vectors
- Measures angular distance, not magnitude
- Standard metric in face recognition
- Computationally efficient

### 2. Why Convert to 0-100 Scale?

The conversion `100 - cos_dist * 50` provides:
- Intuitive percentage-like values
- 100 = identical faces
- 0 = completely different
- Better UX than raw cosine values

### 3. Why Group Faces by Threshold?

Video processing challenges:
- Same face varies frame-to-frame
- Without grouping, creates duplicate entries
- Threshold balances stability vs accuracy
- Prevents UI clutter

### 4. Why Multiple Detection Models?

Different models offer:
- Accuracy vs speed tradeoffs
- Different strengths for face types
- Compatibility options
- User preference

## Best Practices

### For Video Processing

1. **Similarity Threshold**: 50-65
   - Balances stability and accuracy
   - Adjust based on video quality

2. **Detection Score**: 40-60
   - Filters obvious false positives
   - Maintains good coverage

3. **Auto Rotation**: OFF
   - Most video has upright faces
   - Saves processing time

### For Photo Processing

1. **Similarity Threshold**: 65-80
   - Higher accuracy for static images
   - Less concern about frame variations

2. **Detection Score**: 30-50
   - Catch more faces in group photos
   - Manual verification easier

3. **Auto Rotation**: ON
   - Photos often have varied orientations
   - Worth extra processing time

### Performance Optimization

1. **Limit Max Faces** for real-time processing
2. **Disable Auto Rotation** for video
3. **Use faster detection models** (SCRDF/Yolov8)
4. **Increase Detection Score** to reduce candidates

### Quality Optimization

1. **Use Optimal similarity type** for best alignment
2. **Lower Detection Score** for better coverage
3. **Enable Auto Rotation** for complete detection
4. **Fine-tune Threshold** based on results

## Troubleshooting

### Common Issues

1. **Too many duplicate faces**
   - Increase Similarity Threshold
   - Check if Auto Rotation creating duplicates

2. **Missing faces at angles**
   - Enable Auto Rotation
   - Lower Detection Score
   - Try different detection model

3. **Face hopping in video**
   - Increase Similarity Threshold
   - Ensure consistent lighting
   - Check video quality

4. **False face detections**
   - Increase Detection Score
   - Use Retinaface for accuracy
   - Verify input image quality

## Process Diagrams

For detailed process flow diagrams, see:
- [Overall Flow](diagrams/face-finding-flow.mmd)
- [Detection Process](diagrams/face-detection-flow.mmd)
- [Recognition Process](diagrams/face-recognition-flow.mmd)
- [Similarity Matching](diagrams/similarity-matching-flow.mmd)
- [Threshold Problem Visualization](diagrams/threshold-problem.mmd)
- [Algorithm Failure Demo](diagrams/algorithm-failure-demo.mmd)

## Known Limitations

For a comprehensive analysis of problems with the current approach, see [Problems and Limitations](problems-and-limitations.md). Key issues include:
- Global threshold problem making multiple face swaps unreliable
- Temporal inconsistency in video processing
- Loss of spatial context
- Order-dependent matching

These limitations are fundamental to the current architecture and significantly impact the reliability of multiple face swaps.