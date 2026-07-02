from insightface.app import FaceAnalysis

_app = None

def get_model():
    global _app
    if _app is None:
        _app = FaceAnalysis(name='buffalo_sc')
        _app.prepare(ctx_id=-1, det_size=(320, 320))
    return _app