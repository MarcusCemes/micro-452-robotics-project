from dataclasses import dataclass
from enum import Enum
from typing import Callable

import cv2
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
from scipy.signal import convolve2d

from app.config import *
from app.context import Context
from app.path_finding.types import Map
from app.utils.console import *
from app.utils.math import clamp
from app.utils.types import Coords, Vec2

# == Types == #

Image = cv2.Mat
Colour = tuple[int, int, int]
ColourRange = tuple[Colour, Colour]

# == Constants == #
BILATERAL_SIGMA = 75  # Denoise filter strength
CALIBRATE_NAMED_WINDOW = "Vision calibration"  # GUI window name
COLOUR_DELTA = 32  # Colour range tolerance
LANDMARK_DETECTION_THRESHOLD = 10  # Minimum number of landmarks pixels
TEST_IMAGE_PATH = "assets/test_frame_01.jpg"  # Test image path
THRESHOLD = 128  # Colour threshold for binarisation
WAIT_KEY_INTERVAL_MS = 100  # GUI wait key interval
ISOLATION_SIZE = 3  # size of isolate kernel
ISOLATE_THRESHOLD = 3  # number of neighbours required to consider a pixel isolated

PIXEL_MIN = 0  # Minimum pixel value
PIXEL_MAX = 255  # Maximum pixel value

# The dimensions of the image processing frame
IMAGE_PROCESSING_DIM = PIXELS_PER_CM * TABLE_LEN

# The mean colour of an obstacle (black)
COLOUR_OBSTACLE = (35, 35, 35)


@dataclass
class Observation:
    """A class to hold the observation of the environment by vision."""

    obstacles: Map
    back: Vec2
    front: Vec2


class Step(Enum):
    Perspective = 0
    Back = 1
    Front = 2
    Done = 3


class KeyCodes(Enum):
    Q = ord("q")
    N = ord("n")


class Vision:
    """A class to handle vision image processing and calibration."""

    def __init__(
        self,
        ctx: Context,
        external=USE_EXTERNAL_CAMERA,
        live=USE_LIVE_CAMERA,
        image_path=TEST_IMAGE_PATH,
    ):
        self.ctx = ctx
        self.external = external
        self.live = live
        self.image_path = image_path

        self.ax = None

    def __enter__(self):
        """Initialise the vision system."""

        if self.live:
            source = 1 if self.external else 0  # 0 = webcam, 1 = external
            self.camera = cv2.VideoCapture(source, cv2.CAP_DSHOW)

            if not self.camera.isOpened():
                raise RuntimeError("Could not open capture source!")

    def __exit__(self, *_):
        """Clean up the vision system."""

        if self.live:
            self.camera.release()

    # === Calibration === #

    def calibrate(self):
        """
        Runs the calibration process. This will open a GUI window and allow
        the user to select various calibration points on the image.
        """

        self.calibration_step = Step.Perspective
        self.pts_src: list[Coords] = []

        image = self._read_image()

        if not Image:
            raise RuntimeError("Could not read image!")

        info("A GUI window will open to calibrate the vision system")
        info("Select 4 points to correct perspective (TL, TR, BR, BL)")
        info("Then select the back landmark, then the front landmark")
        info("Press N to take a new frame, or Q to exit")

        # Show the captured frame in a GUI window
        def handler(event, x, y, *_):
            return self._handle_click(event, x, y, image)

        cv2.imshow(CALIBRATE_NAMED_WINDOW, image)
        cv2.setMouseCallback(CALIBRATE_NAMED_WINDOW, handler)

        # Allow OpenCV to process GUI events
        while self.calibration_step != Step.Done:
            match cv2.waitKey(WAIT_KEY_INTERVAL_MS):

                case KeyCodes.Q.value:
                    cv2.destroyWindow(CALIBRATE_NAMED_WINDOW)
                    return False

                case KeyCodes.N.value:
                    self.pts_src = []
                    self.calibration_step = Step.Perspective
                    image = self._read_image()
                    cv2.imshow(CALIBRATE_NAMED_WINDOW, image)

            # Check if the GUI window has been closed
            if cv2.getWindowProperty(CALIBRATE_NAMED_WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                info("Calibration window closed, exiting...")
                cv2.destroyWindow(CALIBRATE_NAMED_WINDOW)
                return False

        # Close the GUI window
        cv2.destroyWindow(CALIBRATE_NAMED_WINDOW)
        self.calibration_image = None

        # Generate the perspective transform
        src = np.array(self.pts_src)
        dst = np.array(self._homoDstPoints())
        self.perspective_correction, _ = cv2.findHomography(src, dst)

        info("Calibration complete!")
        return True

    def _handle_click(self, event, x, y, image):
        """Callback for mouse clicks on the calibration GUI window."""

        match event:

            case cv2.EVENT_RBUTTONDOWN:
                colours = tuple(image[y, x])
                info(f"Sampled pixel: (x,y) = {(x,y)}, (B,G,R) = {colours}")

            case cv2.EVENT_LBUTTONDOWN:
                match self.calibration_step:
                    case Step.Perspective:
                        self.pts_src.append((x, y))
                        if len(self.pts_src) == 4:
                            self.calibration_step = Step.Back

                    case Step.Back:
                        self.back_colour = image[y, x]
                        self.calibration_step = Step.Front

                    case Step.Front:
                        self.front_colour = image[y, x]
                        self.calibration_step = Step.Done

                    case Step.Done:
                        pass

                    case _:
                        raise RuntimeError(f"Unexpected calibration step!")

    def _homoDstPoints(self):
        """Returns the destination points for the perspective transform."""

        l = IMAGE_PROCESSING_DIM - 1
        return [[0, 0], [l, 0], [l, l], [0, l]]

    # === Updates === #

    def next(self) -> Observation | None:
        """Returns the next observation from the vision system."""

        image = self._read_image()

        if image is None:
            return None

        # If debug is set, create a new figure for other methods
        if self.ctx.debug_update:
            _, self.ax = plt.subplots(2, 3)

        # Apply image processing filters
        map = self._process_image(image)
        obstacles = self._find_obstacles(map)
        back, front = self._find_landmarks(map)

        if back == None or front == None:
            debug("Could not find landmarks!")
            return None

        # If debug is set, show various stages of the image processing
        if self.ax is not None:
            self.ax[0][0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            self.ax[1][0].imshow(cv2.cvtColor(map, cv2.COLOR_BGR2RGB))
            self.ax[1][0].plot(*back, "ro")
            self.ax[1][0].plot(*front, "bo")

            plt.show()
            self.ax = None

        return Observation(
            obstacles,  # type: ignore
            self._to_physical_space(back),
            self._to_physical_space(front),
        )

    def _read_image(self) -> Image | None:
        """Reads an image from the camera or file."""

        if self.live:
            ret, image = self.camera.read()
            return image if ret else None

        else:
            return cv2.imread(self.image_path)  # type: ignore

    # == Image processing == #

    def _process_image(self, image: Image) -> Image:
        """Applies image processing functions to the image."""

        return self._apply_functions(
            image,
            [
                self._map_image,
                self._denoise,
                self._remove_borders,
            ],
        )

    def _find_obstacles(self, map: Image) -> Image:
        """Identifies obstacles in the image."""

        return self._apply_functions(
            map,
            [
                self._isolate_obstacles,
                self._generate_obstacle_grid,
                self._normalise,
                self._remove_isolated_pixels,
            ],
        )

    def _find_landmarks(self, map: Image) -> tuple[Coords | None, Coords | None]:
        """Locates the Thymio's landmarks in the image."""

        # Debug visualisation
        if self.ax is not None:
            ax = self.ax[:, 1:3]  # type: ignore
        else:
            ax = (None, None)

        # Find the landmarks
        back = self._find_landmark(map, self.back_colour, LM_BACK, ax[0])
        front = self._find_landmark(map, self.front_colour, LM_FRONT, ax[1])

        return (back, front)

    def _find_landmark(
        self,
        convolution: Image,
        colour: Colour,
        size: float,
        axs: list[plt.Axes] | None,
    ) -> Coords | None:
        """Finds a given landmark in the image, given a colour."""

        convolution = self._isolate_landmark(convolution, colour, size, axs)
        (x, y) = self._get_maximum(convolution)

        if convolution[y, x] < LANDMARK_DETECTION_THRESHOLD:
            return None

        offset = int(0.35 * size * PIXELS_PER_CM)
        return (x + offset, y + offset)

    # == Image processing functions == #

    def _map_image(self, image: Image) -> Image:
        """
        Corrects the perspective of the image, resizing it to the
        desired image processing dimensions.
        """

        return cv2.warpPerspective(
            image,
            self.perspective_correction,
            (IMAGE_PROCESSING_DIM, IMAGE_PROCESSING_DIM),
        )

    def _denoise(self, image: Image) -> Image:
        """Simple denoising using a bilateral filter."""

        return cv2.bilateralFilter(
            image, PIXELS_PER_CM, BILATERAL_SIGMA, BILATERAL_SIGMA
        )

    def _remove_borders(self, image: Image) -> Image:
        """Removes the border pixels from the image."""

        size = PIXELS_PER_CM
        image[0:size, :] = PIXEL_MAX, PIXEL_MAX, PIXEL_MAX
        image[-size:, :] = PIXEL_MAX, PIXEL_MAX, PIXEL_MAX
        image[:, 0:size] = PIXEL_MAX, PIXEL_MAX, PIXEL_MAX
        image[:, -size:] = PIXEL_MAX, PIXEL_MAX, PIXEL_MAX
        return image

    def _isolate_obstacles(self, image: Image) -> Image:
        """Extracts pixels that are within the obstacle colour range."""

        dark, light = self._colour_range(COLOUR_OBSTACLE)
        return cv2.inRange(image, np.array(dark), np.array(light))

    def _generate_obstacle_grid(self, obstacles: Image) -> Image:
        """Resizes the image to the desired final size and referential."""
        resized = cv2.resize(obstacles, dsize=(SUBDIVISIONS, SUBDIVISIONS))

        # Flip the image vertically to match the robot's coordinate system
        return cv2.flip(resized, 0)

    def _remove_isolated_pixels(self, image: Image) -> Image:
        """Removes isolated pixels from the image."""

        convolution = convolve2d(
            image,
            self._isolation_kernel(),
            mode="same",
            boundary="fill",
            fillvalue=0,
        )

        mask = np.where(convolution > ISOLATE_THRESHOLD, 1, 0)  # type: ignore

        return np.multiply(image, mask)  # type: ignore

    def _isolation_kernel(self, size: int = ISOLATION_SIZE) -> npt.NDArray[np.uint64]:
        """Generates a kernel for removing isolated pixels."""

        return np.ones((size, size), np.uint64)

    def _normalise(self, image: Image, threshold=THRESHOLD) -> Image:
        """Normalises the image to 0 and 1 values, based on a threshold level."""
        return np.where(image > threshold, 1, 0)  # type: ignore

    def _isolate_landmark(
        self, map: Image, colour: Colour, size: float, axs: list[plt.Axes] | None
    ) -> Image:
        """Attempts to isolate a landmark of a given colour and size."""

        dark, light = self._colour_range(colour)
        threshold = cv2.inRange(map, np.array(dark), np.array(light))

        # 8-bit space can overflow when convolving, so we use 64-bit
        threshold_64 = threshold.astype(np.int64)

        convolution = convolve2d(
            threshold_64,
            self._landmark_kernel(size),
            mode="same",
            boundary="fill",
            fillvalue=0,
        )

        # Debug visualisation
        if axs is not None:
            axs[0].imshow(threshold, cmap="gray")
            axs[1].imshow(convolution, cmap="gray")

        return convolution

    def _landmark_kernel(self, size: float) -> npt.NDArray[np.uint64]:
        """Generates a circular kernel for the given landmark size."""

        disc_radius = int(size * PIXELS_PER_CM)
        kernal_dim = 2 * disc_radius + 1
        R2 = disc_radius**2

        kernel = np.zeros((kernal_dim, kernal_dim), np.uint64)

        for i in range(kernal_dim):
            for j in range(kernal_dim):
                if (disc_radius - i) ** 2 + (disc_radius - j) ** 2 <= R2:
                    kernel[i, j] = 1

        return kernel

    def _get_maximum(self, map: Image) -> Coords:
        """Finds the indices of the maximum value of an image."""

        max = np.argmax(map, axis=None)
        (y, x) = np.unravel_index(max, map.shape)  # type: ignore
        return (x, y)  # type: ignore

    def _to_physical_space(self, coords: Coords) -> Vec2:
        """Converts image coordinates to physical coordinates."""

        x, y = coords

        # Flip the y axis
        y = IMAGE_PROCESSING_DIM - y

        factor = float(PHYSICAL_SIZE_CM) / float(IMAGE_PROCESSING_DIM)
        return x * factor, y * factor

    # == Utilities == #

    def _colour_range(self, colour: Colour, delta: int = COLOUR_DELTA) -> ColourRange:
        """Returns a range of colours around a given colour."""
        return (self._shift_colour(colour, -delta), self._shift_colour(colour, delta))

    def _shift_colour(self, colour: Colour, delta: int) -> Colour:
        """Shifts a colour and clamps it to the pixel range."""
        return tuple(map(lambda x: clamp(x + delta, PIXEL_MIN, PIXEL_MAX), colour))

    def _apply_functions(self, image: Image, functions: list[Callable[[Image], Image]]):
        """Applies a list of functions to an image in order (pipe operator)."""

        for function in functions:
            image = function(image)

        return image
