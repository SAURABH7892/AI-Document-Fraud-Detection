"""Pillar 2: Advanced pixel forensics, Copy-Move detection, and GenAI FFT spectral traces."""
import numpy as np
import cv2
from typing import Dict, Any, List, Tuple

class AdvancedPixelForensics:
    """Detects Copy-Move forgery and frequency domain Generative AI / diffusion traces."""

    @classmethod
    def detect_genai_spectral_traces(cls, image: np.ndarray) -> Tuple[Dict[str, Any], float]:
        """
        Analyze 2D Fast Fourier Transform (FFT) power spectrum for periodic high-frequency grid artifacts
        characteristic of diffusion models (Stable Diffusion, Midjourney, DALL-E) and GAN upsamplers.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Resize to standard power-of-two patch for stable FFT
        h, w = gray.shape
        target_size = 512
        resized = cv2.resize(gray, (target_size, target_size), interpolation=cv2.INTER_AREA)

        # 2D FFT
        dft = np.fft.fft2(resized)
        dft_shift = np.fft.fftshift(dft)
        magnitude_spectrum = np.log(1 + np.abs(dft_shift))

        # Measure high-frequency peripheral energy vs low-frequency center energy
        center = target_size // 2
        r_inner = 40
        r_outer = 180

        y, x = np.ogrid[:target_size, :target_size]
        dist_from_center = np.sqrt((x - center)**2 + (y - center)**2)

        # High-frequency ring mask excluding horizontal & vertical cross axes
        # (Horizontal and vertical axes reflect normal rectangular document margins and text lines)
        ring_mask = (dist_from_center >= r_inner) & (dist_from_center <= r_outer)
        cross_mask = (np.abs(x - center) > 14) & (np.abs(y - center) > 14)
        off_axis_mask = ring_mask & cross_mask
        
        high_freq_vals = magnitude_spectrum[off_axis_mask]
        if len(high_freq_vals) == 0:
            return None, 0.0

        # Calculate azimuthal variance & peak-to-average ratio in off-axis high frequencies
        mean_hf = float(np.mean(high_freq_vals))
        std_hf = float(np.std(high_freq_vals))
        peak_hf = float(np.max(high_freq_vals))
        spectral_skew = float(peak_hf / (mean_hf + 1e-5))

        # Diffusion/GAN upsampling layers introduce periodic off-axis checkerboard spikes
        # resulting in high peak-to-average ratio and abnormal variance in diagonal quadrants
        is_synthetic = spectral_skew > 3.4 and std_hf > 2.2

        finding = None
        if is_synthetic:
            finding = {
                "signal": "genai_spectral_grid_artifacts",
                "severity": "HIGH",
                "category": "SYNTHETIC_GENAI",
                "finding": f"2D Fourier frequency spectrum reveals periodic diagonal checkerboard spikes (Skew: {spectral_skew:.2f}, Std: {std_hf:.2f}). Characteristic trace of diffusion/GAN generative upsamplers."
            }

        return finding, spectral_skew

    @classmethod
    def detect_copy_move(cls, image: np.ndarray) -> Tuple[Dict[str, Any], int]:
        """
        Detect duplicated regions (copy-move manipulation) such as cloned signatures,
        duplicated rubber stamps, or altered serial numbers using keypoint matching
        with translation vector clustering (to ignore random font character repeats).
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Initialize ORB detector
        orb = cv2.ORB_create(nfeatures=1200)
        keypoints, descriptors = orb.detectAndCompute(gray, None)

        if descriptors is None or len(keypoints) < 50:
            return None, 0

        # BFMatcher with Hamming distance
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        matches = bf.knnMatch(descriptors, descriptors, k=3)

        # Filter matches: ignore self-matches (k=0), test distance ratio and minimum spatial separation
        clone_pairs = []
        min_spatial_distance = 60.0  # pixels apart to avoid adjacent text characters

        for m in matches:
            if len(m) >= 3:
                # m[0] is self match. Check m[1]
                match1 = m[1]
                if match1.distance < 32:  # High descriptor similarity
                    pt1 = np.array(keypoints[match1.queryIdx].pt)
                    pt2 = np.array(keypoints[match1.trainIdx].pt)
                    dist = np.linalg.norm(pt1 - pt2)
                    if dist >= min_spatial_distance:
                        clone_pairs.append((pt1, pt2))

        # Perform translation vector clustering:
        # In a genuine copy-move manipulation (cloned stamp, forged signature, duplicated patch),
        # all matched keypoints undergo the exact same spatial translation vector (dx, dy).
        # Normal repeated typography letters ('e', 'o', '0') across sentences have random
        # scattered translation vectors with at most 1-2 matches per bin.
        translation_bins: Dict[Tuple[int, int], int] = {}
        for pt1, pt2 in clone_pairs:
            # Quantize displacement into 30px spatial bins
            dx_bin = int(round((pt2[0] - pt1[0]) / 30.0) * 30)
            dy_bin = int(round((pt2[1] - pt1[1]) / 30.0) * 30)
            bin_key = (dx_bin, dy_bin)
            translation_bins[bin_key] = translation_bins.get(bin_key, 0) + 1

        # The coherent clone count is the size of the largest single translation cluster
        coherent_clone_count = max(translation_bins.values()) if translation_bins else 0
        finding = None

        if coherent_clone_count >= 7:
            finding = {
                "signal": "copy_move_cloning",
                "severity": "HIGH",
                "category": "ALTERATION",
                "finding": f"Detected coherent cloned feature cluster ({coherent_clone_count} keypoints sharing identical displacement vector). Indicates duplicated rubber stamps, signatures, or replicated document patches."
            }

        return finding, coherent_clone_count
