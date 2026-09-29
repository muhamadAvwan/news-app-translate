import os
import sys
import threading

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

READY = {"ok": False, "err": "", "model": ""}
LOAD_LOCK = threading.Lock()
MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "60"))
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*")

app = FastAPI(title="Argos Translate en->id", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS.split(",") if ALLOWED_ORIGINS != "*" else ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class TItem(BaseModel):
    id: str
    text: str = Field(default="", max_length=600)
    lang: str = "en"


class TranslateRequest(BaseModel):
    items: list[TItem]


def ensure_model():
    if READY["ok"]:
        return True
    with LOAD_LOCK:
        if READY["ok"]:
            return True
        try:
            import argostranslate.package as apkg
            import argostranslate.translate  # noqa: F401

            installed = apkg.get_installed_packages()
            has = any(p.from_code == "en" and p.to_code == "id" for p in installed)
            if not has:
                print("model en->id belum ada, mengunduh...", flush=True)
                avail = apkg.get_available_packages()
                pkg = next((p for p in avail if p.from_code == "en" and p.to_code == "id"), None)
                if pkg is None:
                    raise RuntimeError("paket en->id tidak tersedia di index Argos")
                apkg.install_from_path(pkg.download())
                print("model en->id terpasang", flush=True)
            READY["ok"] = True
            READY["model"] = "argos-translate en->id"
            return True
        except Exception as e:
            READY["err"] = str(e)[:200]
            print("gagal muat model: " + READY["err"], flush=True)
            return False


@app.on_event("startup")
def _startup():
    threading.Thread(target=ensure_model, daemon=True).start()


@app.get("/")
def root():
    return {
        "service": "argos-translate-en-id",
        "endpoints": {"POST /translate": "translate titles", "GET /health": "status"},
    }


@app.get("/health")
def health():
    return {"ok": READY["ok"], "model": READY["model"], "error": READY["err"] or None}


@app.post("/translate")
def translate(req: TranslateRequest):
    if not req.items:
        return JSONResponse({"items": [], "engine": "argos"})
    if len(req.items) > MAX_ITEMS:
        raise HTTPException(status_code=413, detail="maksimal %d item per permintaan" % MAX_ITEMS)
    if not ensure_model():
        raise HTTPException(status_code=503, detail="model belum siap: " + (READY["err"] or ""))

    import argostranslate.translate as atr

    out = []
    for it in req.items:
        try:
            if (it.lang or "en").lower() == "id" or not it.text.strip():
                out.append({"id": it.id, "text": it.text})
                continue
            tr = atr.translate(it.text, "en", "id").strip()
            out.append({"id": it.id, "text": tr or it.text})
        except Exception:
            out.append({"id": it.id, "text": it.text})
    return JSONResponse({"items": out, "engine": "argos"})


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "7860"))
    ensure_model()
    uvicorn.run(app, host="0.0.0.0", port=port)
