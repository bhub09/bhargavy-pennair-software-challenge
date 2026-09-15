# Failure Analysis Report

## 1. Contour problem
Running the initial pipeline yielded 7,000 contours for a single image, which consisted of large blobs that didn't cover the desired markers. Arranging the contours by area was considered, but ultimately didn't work because it removed contours of real shapes (with one having an area of 28750). 

## 2. Resolution issue
The static image has a resolution of 960x540, while the videos have a resolution of 1920x1080. Initially, the kernel size was hardcoded at 5, but this represented two different scales on these inputs, thus yielding different results. One fix was made by by computing kernel dimension as a fraction of frame width (`VAR_FRACTION`, `SMOOTH_FRACTION`, `MIN_AREA_FRACTION`). 

## 3. False positives
There were false positives marked on the video with the gray background, as large portions of the background were read as smooth at a smaller k. This yielded large, connected contours.

## 4. Two-window split
Variance grows as k^2 on a gradient, but converges on stationary texture. Noisy estimates result in many pixels being falsely labeled as 'smooth' (hence the 7000 contours). Essentially, measuring variance on a large window, along with smaller-window variances requires two separate kernels. The cost of this, however, is that averaging the map across the larger kernel causes for the mask boundary to be pulled in (i.e. eroded boundaries). This is what the dilation at the end of `_build_shape_mask` compensates for.

## 5. Solidity filter
This filter determines the convexity of the shape by dividing its area by the area of its hull. Real shapes have a solidity of over 0.9, while other regions have lower solidity values. This filter was essential in filtering out contours that weren't shapes.

## 6. Dilation
The dilation from #4 restores eroded boundaries, but also bridges the gap between adjacent shapes. The two shapes are fused into one contour with a concave notch.

## 7. Constraints
The constraint for this algorithm is to keep one configuration for all three parts of the challenge, as specifically stated in the challenge doc.

## 8. Limitations
The recovery dilation widens the separation at which two shapes fuse into a single contour with one centroid.

