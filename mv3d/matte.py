"""Salient-object matte (IS-Net general use, ONNX, as packaged by rembg) -> alpha in [0,1]."""
import cv2, numpy as np, onnxruntime as ort, os
_S = None
def matte(img_bgr, size=1024):
    global _S
    if _S is None: _S = ort.InferenceSession(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "isnet-general-use.onnx"), providers=["CPUExecutionProvider"])
    h, w = img_bgr.shape[:2]
    x = cv2.resize(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), (size, size), interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255.0
    x = (x - 0.5) / 1.0
    p = _S.run(None, {_S.get_inputs()[0].name: x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0]
    p = (p - p.min()) / (p.max() - p.min() + 1e-6)
    return cv2.resize(p, (w, h), interpolation=cv2.INTER_CUBIC).clip(0, 1).astype(np.float32)
