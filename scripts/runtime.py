"""
Compute runtime dispatcher.

Ported from `Deep Learning and Computer Vision/utils/runtime.py` (same
workspace, Week 11 transfer-learning practical) and extended with detection
for a free hosted GPU notebook service, since this project's proven GPU path
is that kind of service, not Colab (see docs/ekegusii_transfer_learning.md
for why: the cloud VM GPU path available to this project is blocked by a
subscription region-allowlist, and a remote-GPU-platform alternative was
untested for this workload at the time).

Detects the execution environment (hosted-notebook GPU/CPU, Colab GPU/TPU/CPU,
local CPU) and returns a unified device handle + strategy object so scripts
stay environment-agnostic.

Usage:
    from runtime import get_runtime
    rt = get_runtime()
    model = rt.prepare(model)
    x = rt.to_device(tensor)
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Literal, Optional

RuntimeKind = Literal[
    "hosted_notebook_gpu", "hosted_notebook_cpu", "colab_gpu", "colab_tpu", "colab_cpu", "local_cpu",
]


@dataclass
class RuntimeInfo:
    kind: RuntimeKind
    device_str: str
    n_devices: int
    device_label: str
    notes: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Convenience helpers                                                  #
    # ------------------------------------------------------------------ #

    def to_device(self, tensor):
        """Move a torch tensor to the runtime device."""
        return tensor.to(self.device_str)

    def prepare(self, model):
        """Wrap a torch nn.Module for the detected device / strategy."""
        import torch

        model = model.to(self.device_str)

        if self.kind == "colab_tpu":
            try:
                import torch_xla.core.xla_model as xm  # type: ignore
                # XLA models should already be on xla device; nothing extra needed
            except ImportError:
                pass

        elif self.kind in ("colab_gpu", "hosted_notebook_gpu") and self.n_devices > 1:
            import torch.nn as nn
            model = nn.DataParallel(model)

        return model

    def dataloader_kwargs(self) -> dict:
        """
        Extra kwargs to pass to torch DataLoader so prefetch / pinning
        match the runtime.
        """
        if self.kind in ("colab_gpu", "hosted_notebook_gpu"):
            return {"num_workers": 2, "pin_memory": True}
        if self.kind == "colab_tpu":
            return {"num_workers": 4}
        return {"num_workers": 0, "pin_memory": False}

    @property
    def recommended_batch_size(self) -> int:
        if self.kind in ("colab_gpu", "hosted_notebook_gpu"):
            try:
                import torch
                vram = torch.cuda.get_device_properties(0).total_memory // (1024 ** 2)
                if vram >= 15000: return 64
                if vram >= 10000: return 32
                return 16
            except Exception:
                return 16
        if self.kind == "colab_tpu":
            return 128
        # local/hosted-notebook CPU: this project fine-tunes seq2seq MT models
        # (mT5-small / NLLB-200-distilled), which need a smaller CPU batch
        # than the DLCV image-classification source this was ported from.
        return 4

    @property
    def recommended_precision(self) -> str:
        if self.kind in ("colab_gpu", "hosted_notebook_gpu"):
            try:
                import torch
                major = torch.cuda.get_device_capability(0)[0]
                if major >= 8: return "bf16"
                if major >= 7: return "fp16"
            except Exception:
                pass
            return "fp32"
        if self.kind == "colab_tpu":
            return "bf16"
        return "fp32"

    @property
    def has_gpu(self) -> bool:
        return self.kind in ("colab_gpu", "hosted_notebook_gpu")

    @property
    def has_tpu(self) -> bool:
        return self.kind == "colab_tpu"

    def summary(self) -> str:
        lines = [
            f"Runtime : {self.kind}",
            f"Device  : {self.device_str}  ({self.device_label})",
            f"N dev   : {self.n_devices}",
        ]
        lines += [f"Note    : {n}" for n in self.notes]
        return "\n".join(lines)


# ------------------------------------------------------------------ #
# Detection logic                                                      #
# ------------------------------------------------------------------ #

def _is_hosted_notebook() -> bool:
    # This free hosted GPU notebook service sets its own kernel-run-type env
    # var for every notebook/script run -- checked directly rather than via a
    # path-existence fallback, since the env var alone is the reliable signal.
    return os.environ.get("KAGGLE_KERNEL_RUN_TYPE") is not None


def _is_colab() -> bool:
    return "google.colab" in sys.modules or os.path.exists("/usr/local/lib/python3.10/dist-packages/google/colab")


def _gpu_info() -> tuple[bool, int]:
    """Returns (has_gpu, n_gpus). Same check works for the hosted notebook service and Colab."""
    try:
        import torch
        if torch.cuda.is_available():
            return True, torch.cuda.device_count()
    except ImportError:
        pass
    return False, 0


def _colab_tpu_info() -> tuple[bool, int]:
    """Returns (has_tpu, n_cores)."""
    try:
        import torch_xla.core.xla_model as xm  # type: ignore
        devices = xm.get_xla_supported_devices()
        return True, len(devices)
    except (ImportError, Exception):
        pass
    if os.environ.get("COLAB_TPU_ADDR"):
        return True, 8
    return False, 0


def get_runtime(prefer: Optional[Literal["gpu", "tpu", "cpu"]] = None) -> RuntimeInfo:
    """
    Auto-detect and return a RuntimeInfo.

    Args:
        prefer: Force a specific backend when multiple are available.
                Useful to pin a script to CPU for local debugging even when
                (in principle) a GPU driver is present.
    """
    in_hosted_notebook = _is_hosted_notebook()
    in_colab = _is_colab()

    has_gpu, n_gpu = _gpu_info()
    has_tpu, n_tpu = _colab_tpu_info() if in_colab else (False, 0)

    if prefer == "cpu":
        if in_hosted_notebook:
            kind: RuntimeKind = "hosted_notebook_cpu"
        elif in_colab:
            kind = "colab_cpu"
        else:
            kind = "local_cpu"
        return RuntimeInfo(kind=kind, device_str="cpu", n_devices=1,
                           device_label="CPU (forced)", notes=["prefer=cpu override active"])

    if in_hosted_notebook:
        if (prefer in (None, "gpu")) and has_gpu:
            import torch
            label = torch.cuda.get_device_name(0)
            notes = [f"{n_gpu} GPU(s) detected"]
            # This hosted notebook service has repeatedly ignored the
            # requested machine_shape and handed out an older Pascal-
            # generation P100 instead of the requested T4 -- flag this so a
            # script can defensively re-pin torch (see the private kernel
            # wrapper) rather than assume the requested shape was honoured.
            if torch.cuda.get_device_capability(0)[0] < 7:
                notes.append(
                    "compute capability < 7.0 (Pascal-era) -- current preinstalled "
                    "torch may have dropped support for this GPU; pin "
                    "torch==2.7.1+cu118 as the FIRST import if generate()/train() "
                    "fails with a CUDA capability error"
                )
            return RuntimeInfo("hosted_notebook_gpu", "cuda", n_gpu, label, notes=notes)
        return RuntimeInfo("hosted_notebook_cpu", "cpu", 1, "Hosted notebook CPU",
                           notes=["no GPU detected or prefer='cpu'/'tpu' requested"])

    if in_colab:
        if prefer == "tpu" and has_tpu:
            try:
                import torch_xla.core.xla_model as xm  # type: ignore
                xla_device = xm.xla_device()
                return RuntimeInfo("colab_tpu", str(xla_device), n_tpu,
                                   f"TPU v2/v3 ({n_tpu} cores)")
            except ImportError:
                pass

        if (prefer in (None, "gpu")) and has_gpu:
            import torch
            label = torch.cuda.get_device_name(0)
            return RuntimeInfo("colab_gpu", "cuda", n_gpu,
                               label, notes=[f"{n_gpu} GPU(s) detected"])

        if has_tpu and prefer != "gpu":
            try:
                import torch_xla.core.xla_model as xm  # type: ignore
                xla_device = xm.xla_device()
                return RuntimeInfo("colab_tpu", str(xla_device), n_tpu,
                                   f"TPU ({n_tpu} cores)")
            except ImportError:
                pass

        return RuntimeInfo("colab_cpu", "cpu", 1, "Colab CPU")

    # Local machine (this workspace's own container, or any other bare host)
    return RuntimeInfo("local_cpu", "cpu", 1, "Local CPU",
                       notes=["Local environment: CPU only (torch+cpu build)"])


# ------------------------------------------------------------------ #
# Task routing helper                                                  #
# ------------------------------------------------------------------ #

TASK_PROFILES: dict[str, dict] = {
    "finetune_mt":          {"prefer": "gpu", "note": "Seq2seq fine-tuning (mT5/NLLB) -- GPU strongly preferred, a free hosted GPU notebook service is this project's proven path"},
    "smoke_test":           {"prefer": "cpu", "note": "Tiny-batch pipeline check -- always run on local CPU, never spend GPU quota on this"},
    "translate_batch":      {"prefer": "gpu", "note": "Bulk zero-shot translation over thousands of rows -- GPU ideal, CPU tractable but slow"},
    "translate_small":      {"prefer": "cpu", "note": "A handful of rows -- CPU is fine, not worth a hosted-GPU session"},
    "eval_metrics":         {"prefer": "cpu", "note": "BLEU/chrF/COMET scoring -- all CPU-tractable, no GPU needed"},
    "data_preprocessing":   {"prefer": "cpu", "note": "I/O bound, CPU is fine"},
    "hyperparameter_search":{"prefer": "gpu", "note": "Multiple fine-tune configs -- batch into one hosted-GPU session"},
}


def get_runtime_for_task(task: str) -> RuntimeInfo:
    """
    Return a RuntimeInfo tuned for a named task profile.

    Example:
        rt = get_runtime_for_task("finetune_mt")
    """
    profile = TASK_PROFILES.get(task)
    if profile is None:
        known = ", ".join(TASK_PROFILES.keys())
        raise ValueError(f"Unknown task '{task}'. Known tasks: {known}")
    rt = get_runtime(prefer=profile["prefer"])
    rt.notes.append(f"Task profile '{task}': {profile['note']}")
    return rt


if __name__ == "__main__":
    rt = get_runtime()
    print(rt.summary())
