"""Monocular depth (MiDaS v2.1 small, ONNX) -> relative inverse depth in [0,1] (1 = near)."""
import cv2, numpy as np, onnxruntime as ort, os
_S = None
def depth(img_bgr):
    global _S
    if _S is None: _S = ort.InferenceSession(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "midas_small.onnx"), providers=["CPUExecutionProvider"])
    h, w = img_bgr.shape[:2]
    x = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), (256, 256), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    x = x.transpose(2, 0, 1)[None].astype(np.float32)
    d = _S.run(None, {_S.get_inputs()[0].name: x})[0][0]
    d = cv2.resize(d, (w, h), interpolation=cv2.INTER_CUBIC)
    d = (d - np.percentile(d, 1)) / (np.percentile(d, 99) - np.percentile(d, 1) + 1e-6)
    return np.clip(d, 0, 1).astype(np.float32)
