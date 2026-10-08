"""Cel + ink stylisation of real footage: edge-preserving smoothing, palette quantisation in LAB, ink edges from luminance."""
import cv2, numpy as np, sys
def celify(img, k=10, ink=0.9, line=2, paper=None, warm=0.0, soft=False):
    sm = img.copy()
    for _ in range(2): sm = cv2.bilateralFilter(sm, 9, 60, 7)
    lab = cv2.cvtColor(sm, cv2.COLOR_BGR2LAB).astype(np.float32)
    # quantise lightness into bands (cel steps), keep chroma smooth
    L = lab[..., 0]; steps = np.array([28, 70, 120, 175, 225] if not soft else [20, 55, 90, 125, 160, 195, 235], np.float32)
    w = 0.85 if not soft else 0.6
    idx = np.abs(L[..., None] - steps).argmin(-1); lab[..., 0] = steps[idx] * w + L * (1 - w)
    lab[..., 1:] = (lab[..., 1:] - 128) * 1.12 + 128
    out = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    g = cv2.cvtColor(cv2.GaussianBlur(img, (3, 3), 0), cv2.COLOR_BGR2GRAY)
    e = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 5)
    ed = cv2.Canny(cv2.bilateralFilter(img, 7, 50, 7), 60, 140)
    ed = cv2.dilate(ed, np.ones((line, line), np.uint8))
    mask = ((255 - e) / 255.0 * (0.35 if not soft else 0.15) + ed / 255.0).clip(0, 1) * ink
    inkc = np.array([40, 22, 18], np.float32)  # deep navy ink (BGR)
    out = out.astype(np.float32) * (1 - mask[..., None]) + inkc * mask[..., None]
    return out.clip(0, 255).astype(np.uint8)
if __name__ == "__main__":
    im = cv2.imread(sys.argv[1]); s = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    if s != 1: im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(sys.argv[2], celify(im))
