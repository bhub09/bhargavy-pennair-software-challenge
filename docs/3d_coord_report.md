# 3D-Coordinate Report

## 1. Purpose
Given the camera intrinsic matrix, circle radius (10 in.), and focal lengths in x and y direction, calculate X, Y, and Z for every shape.

## 2. Intrinsic Matrix
$$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

The focal lengths `fx` and `fy` are 2564.3187 pixels and 2569.7027 pixels, respectively. The center points `cx` and `cy` are both 0, meaning that the matrix expects pixel coordinates measured from the image center, not top-left like in parts 1-3 (which is the default for OpenCV). The centroid's `x` and `y` coordinates is passed into the formulas $u = x − w/2$ and $v = y − h/2$ as part of calculating the coordinates. 

## 3. Depth from a known size
The perspective projection gives $u = (fx*X) / Z$. Applying it to the circle radius constant `R` at depth `Z` projects to pixel radius `r` with $r = (fx*R) / Z$, so Z can be calculated as: $$Z = (f_x*R)/r$$
The pixel radius comes from the circle area, as `r_eq = sqrt(A/π)` averages over every pixel in the contour, reducing the effect of stray boundary pixels.

## 4. Focal length scales with resolution
K was calibrated at 1920 pixels wide. Focal length is proportional to pixel density, so at width `W`: $fx' = fx × W/1920$. The static image has a factor of 0.5. Without the scaling, the depths would be twice their real value.

## 5. Formulas for coordinates
$$X = \frac{uZ}{f_x},  Y = \frac{vZ}{f_y},  Z = Z$$
X is positive in the right direction, Y is positive in the downward direction, and Z is positive in the forward direction along the optical axis. This is OpenCV's standard, and differs from ROS's REP-103 body convention (which is x forward, y left, and z up).

## 6. Circle identification
Circleness is used to determine a perfect circle, and is calculated by: $\frac{A}{\pi * r_min^2}$, where `r_min` is the minimum enclosing circle's radius. An alternative was considered using perimeter, but was rejected since perimeter is sensitive to boundary ruggedness.

## 7. Clipped-circle bug
When half the circle outside the frame in frame 900 of the first video, its circleness value drops to 0.5. The pentagon, which scores higher, has the highest circleness. The algorithm then computes depth from the pentagon's equivalent radius of 248.3 while other neighbors had a depth of 267.3. After adding a guard that rejects a detection whose bounding rect is within 2 px of an edge, as well as a circleness minimum of 0.85, the frame 900 depth reading went to 266.4 in.

## 8. Flat-surface assumption
Every shape shares the same z-coordinate with the circle, and are perpendicular to the optical axis.

## 9. Error propagation
Z is inversely related to small radius, and since small radius is equal to the square root of A divided by pi, the area error is halved compared to radius error. Essentially the error types are separated. If the large kernel over or under corrects, every radius is biased the same way, which propagates to the depth, as well as X, Y, and Z.

## 10. Limitations
Frame-clipped shapes report the centroid of the visible portion, so X and Y can be off even when depth is correct in this scenario. All Z values are equal from the assumption in #8. When no valid circle is visible, the previous depth is carried forward, making depth outdated for those instances (main bound is how fast the shapes get fully into view).

