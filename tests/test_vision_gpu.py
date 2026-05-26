import importlib.util
from pathlib import Path

import torch

from pic_selecter import vision


def _fake_device(kind: str):
    return type("FakeDevice", (), {"type": kind})()


def test_select_onnx_providers_prefers_cuda(monkeypatch):
    monkeypatch.delenv("PIC_SELECTER_RUNTIME", raising=False)
    monkeypatch.setattr(vision, "_device", lambda: _fake_device("cuda"))
    assert vision._select_onnx_providers(["CUDAExecutionProvider", "CPUExecutionProvider"]) == (
        ["CUDAExecutionProvider", "CPUExecutionProvider"],
        0,
    )


def test_select_onnx_providers_falls_back_to_cpu(monkeypatch):
    monkeypatch.delenv("PIC_SELECTER_RUNTIME", raising=False)
    monkeypatch.setattr(vision, "_device", lambda: _fake_device("cuda"))
    assert vision._select_onnx_providers(["CPUExecutionProvider"]) == (
        ["CPUExecutionProvider"],
        -1,
    )


def test_pyiqa_device_keeps_mps_on_cpu(monkeypatch):
    monkeypatch.delenv("PIC_SELECTER_PYIQA_DEVICE", raising=False)
    monkeypatch.delenv("PIC_SELECTER_RUNTIME", raising=False)
    monkeypatch.setattr(vision, "_device", lambda: _fake_device("mps"))
    assert vision._pyiqa_device() == torch.device("cpu")


def test_runtime_cpu_forces_cpu_onnx(monkeypatch):
    monkeypatch.setenv("PIC_SELECTER_RUNTIME", "cpu")
    assert vision._select_onnx_providers(["CUDAExecutionProvider", "CPUExecutionProvider"]) == (
        ["CPUExecutionProvider"],
        -1,
    )


def test_runtime_gpu_requires_accelerator(monkeypatch):
    monkeypatch.setenv("PIC_SELECTER_RUNTIME", "gpu")
    monkeypatch.delenv("PIC_SELECTER_DEVICE", raising=False)
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(torch.backends.mps, "is_available", lambda: False)
    vision._DEVICE = None
    try:
        try:
            vision._device()
        except vision.VisionUnavailable:
            pass
        else:
            raise AssertionError("expected VisionUnavailable")
    finally:
        vision._DEVICE = None


def test_reset_runtime_state_clears_cached_models():
    vision._DEVICE = "sentinel"
    vision._models["demo"] = object()
    vision.reset_runtime_state()
    assert vision._DEVICE is None
    assert vision._models == {}


def test_launcher_tycoon_includes_local_vision_stack():
    launcher_path = Path(__file__).resolve().parent.parent / "scripts" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher_for_test", launcher_path)
    launcher = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(launcher)

    packages = set(launcher.packages_for_modes(["tycoon"]))
    assert "openai>=1.40" in packages
    assert "transformers>=4.40" in packages
    assert "insightface>=0.7" in packages
    assert "pyiqa>=0.1.10" not in packages


def test_launcher_cuda_torch_install_uses_pytorch_index_only(monkeypatch):
    launcher_path = Path(__file__).resolve().parent.parent / "scripts" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher_for_test_cuda", launcher_path)
    launcher = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(launcher)

    calls = []

    monkeypatch.setattr(launcher, "wants_cuda_backend", lambda modes: True)
    monkeypatch.setattr(launcher, "pip_uninstall", lambda packages: calls.append(("uninstall", packages, {})))
    monkeypatch.setattr(launcher, "info", lambda text: None)

    def _record_install(packages, **kwargs):
        calls.append(("install", list(packages), kwargs))

    monkeypatch.setattr(launcher, "pip_install", _record_install)

    backend = launcher.ensure_runtime_backends(["expert"])

    assert backend.startswith("cuda:")
    torch_call = calls[1]
    ort_call = calls[2]
    assert torch_call[0] == "install"
    assert torch_call[1] == launcher.TORCH_CUDA_PACKAGES
    assert torch_call[2]["index_url"] == launcher.PYTORCH_CUDA_INDEX
    assert "extra_index_urls" not in torch_call[2]
    assert ort_call[2]["index_url"] == "https://pypi.org/simple/"
