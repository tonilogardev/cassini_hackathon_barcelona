import numpy as np

def scs_runoff(P, CN):
    CN = CN.astype("float32")
    valid = np.isfinite(CN)

    out = np.full(CN.shape, np.nan, dtype="float32")
    if not np.any(valid):
        return out

    CN_clip = np.clip(CN[valid], 1, 100)
    S = (25400.0 / CN_clip) - 254.0
    Ia = 0.2 * S

    Q = np.zeros(CN_clip.shape, dtype="float32")
    runoff_mask = P > Ia
    Q[runoff_mask] = ((P - Ia[runoff_mask]) ** 2) / (P + 0.8 * S[runoff_mask])

    out[valid] = Q
    return out
