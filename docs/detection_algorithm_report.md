# Detection Algorithm Report

## 1. No Color
Initially the approach was to use thresholding for color data (BGR). This was not chosen because it would require re-tuning for the background-agnostic detection part of the challenge (Part 3). However, it was noted that the background and shapes differed in texture, with the former having high frequency (differing pixel values) while the latter are smoother.

## 2. Grayscale
The image/video files were converted to gray scale to reduce the number of channels from three to one, requiring fewer maps to be computed (and also the fact that color is irrelevant in my methodology).

## 3. Variance computation
The formula used for variance is as follows:
$$\text{Var}(X) = E[X^2] - (E[X])^2$$

Additional notes:
* float32 casting was used, as uint8 has a maximum of 255, which is easily exceeded when pixel values are squared.
* A box blur was used instead of a Gaussian blur for faster computation, which is important as the kernel size scales with resolution. Box blur is O(1) regardless of k, while Gaussian blur is O(N*k^2), where N is the number of pixels.

## 4. Dynamic threshold
The threshold was made dynamic using Otsu in order to account for images with different resolutions, backgrounds, and lighting.

## 5. Issues with Otsu & fixes
Otsu's method maximizes class variance ($$σ_B² = ω_0ω_1(μ_0−μ_1)^2$$), which represents how far apart the background and shapes are. The weights $$ω_0ω_1$$ specifically peak at a 50/50 split, favoring balanced splits. The shapes cover 6% of the frame, far below this partition. Additionally, the variance map has three categories instead of the two assumed by Otsu: shape interior, background, and the shape boundary (which has high variance). This issue was fixed with `np.log1p`, which uses log transform to compress the background's variance spread relative to the gap between the background and shapes. The log transform changes which data partition would maximize Otsu's objective. Values above the 99th percentile were then clipped to remove high variance boundary outliers. The resulting map is then rescaled to 0-255 and cast to uint8, as  `cv2.threshold` with `THRESH_OTSU` only accepts 8-bit input. The threshold `THRESH_BINARY_INV` is used for shapes, which have low-variance. This improved results drastically, from having the whole frame covered to only the 5 shapes.

## 6. Two window split
Two k values: small (0.004 * frame width) and large (0.010 * frame width) are used for the measurement window and smoothing window, respectively. Variance over a large window would include drifts of local means, which grows as k^2 on a gradient area. By averaging smaller-window variances, we will only keep the within-window texture. 

## 7. Mask to detections
Nested contours are not wanted, only outer boundaries, so the constant `CHAIN_APPROX_SIMPLE` was used as input in the `findContours` function to collapse collinear runs. Other configs include setting area filter at 0.5% of the frame (image) area. Centroid, calculated for center point, was found using the following moments: m00 is the zeroth moment (area), m10 is equal to the summation of x, m01 is equal to the summation of y. The centroid in terms of these moments is `(m10/m00, m01/m00)`. There is a guard to prevent dividing by zero in case `m00 = 0`. The centroids are kept as float values to avoid quantization errors. Finally, OpenCV naturally returns contours as `(N, 1, 2)`, but this was reshaped to `(N, 2)` before it is packaged with the other data points for the shape labels. It is then reshaped back for the `drawContours` function.

## 8. ShapeDetection dictionary
The data points for the label, center, outline points, and area, are kept in a TypedDict object known as ShapeDetection. Using a TypedDict made it easier to detect KeyErrors during development.

## 9. Video performance
The video frames last roughly 56 ms each, for 18 frames per seconds, measured using tqdm for local rendering and `ros2 topic hz` for Part 5. This allows for a more accurate measurement of rendering progress.

## 10. Improvements
Some improvements that could be made include subsampling for `np.percentile`, which sorts the full frame. Additionally, writing the video data as h264 insread of mp4 could prevent the need of manually compressing the videos before committing. Some other changes could be made to dynamically alter parameters (i.e. dimensions of variance and smoothing kernels) for different images/videos so a compromise would not have to be made for media of different textures/gradients.