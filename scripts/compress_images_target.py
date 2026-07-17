#!/usr/bin/env python3
"""
自适应图片压缩脚本 —— 总大小控制版
将指定目录内所有 JPG 图片压缩，使总体积不超过目标大小。
策略：
  1. 按目标总大小 / 图片数量算出每张的目标文件大小
  2. 对每张图片做二分搜索，找到刚好满足大小要求的 JPEG quality 值
  3. 若质量降到最低仍超出大小，则额外缩小分辨率（降至 50%）
  4. 保留 EXIF 元数据，直接替换原文件
"""

import os
import sys
import io
import tempfile
import shutil
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    os.system(f"{sys.executable} -m pip install Pillow piexif")
    from PIL import Image


# ─── 配置 ────────────────────────────────────────────────────────────────────
TARGET_DIR    = Path(os.environ.get("PIANKE_TEST_TARGET_DIR", "pic_test")).resolve()
TARGET_TOTAL_MB = 100          # 目标总大小（MB）
MIN_QUALITY   = 20             # 最低 JPEG 质量（低于此不再降质量，转为缩放）
MAX_QUALITY   = 95             # 二分上限
SUPPORTED_EXTS = {".jpg", ".jpeg"}
# ─────────────────────────────────────────────────────────────────────────────


def format_size(b: int) -> str:
    if b >= 1024**2:
        return f"{b/1024**2:.2f} MB"
    elif b >= 1024:
        return f"{b/1024:.1f} KB"
    return f"{b} B"


def encode_jpeg(img: Image.Image, quality: int, exif_bytes: bytes | None) -> bytes:
    """将 PIL 图像编码为 JPEG bytes（不落盘）。"""
    buf = io.BytesIO()
    kwargs = {"format": "JPEG", "quality": quality, "optimize": True, "progressive": True}
    if exif_bytes:
        kwargs["exif"] = exif_bytes
    img.save(buf, **kwargs)
    return buf.getvalue()


def find_quality_for_target(img: Image.Image, exif_bytes: bytes | None,
                             target_bytes: int) -> tuple[int, bytes]:
    """
    二分搜索：找到使编码大小 ≤ target_bytes 的最大 quality 值。
    返回 (quality, encoded_bytes)。
    """
    lo, hi = MIN_QUALITY, MAX_QUALITY
    best_quality = MIN_QUALITY
    best_data = encode_jpeg(img, MIN_QUALITY, exif_bytes)

    while lo <= hi:
        mid = (lo + hi) // 2
        data = encode_jpeg(img, mid, exif_bytes)
        if len(data) <= target_bytes:
            best_quality = mid
            best_data = data
            lo = mid + 1        # 尝试更高质量
        else:
            hi = mid - 1        # 质量太高，文件太大

    return best_quality, best_data


def compress_to_target(filepath: Path, target_bytes: int) -> tuple[int, int, int] | None:
    """
    压缩单张图片到 ≤ target_bytes。
    返回 (原始大小, 压缩后大小, 最终 quality)，失败返回 None。
    """
    original_size = filepath.stat().st_size

    try:
        img = Image.open(filepath)
        img.load()  # 确保完全加载

        # 读取 EXIF
        exif_bytes = img.info.get("exif", None)

        # 确保模式兼容
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # ① 先用二分法在原始分辨率找合适 quality
        quality, data = find_quality_for_target(img, exif_bytes, target_bytes)

        # ② 若 MIN_QUALITY 仍超出目标，缩小分辨率再压缩
        if len(data) > target_bytes:
            scale = 0.5
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)
            img_resized = img.resize((new_w, new_h), Image.LANCZOS)
            quality, data = find_quality_for_target(img_resized, exif_bytes, target_bytes)
            img.close()
            img = img_resized

        img.close()

        # 安全写入（临时文件 → 替换）
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=filepath.suffix, dir=filepath.parent)
        os.close(tmp_fd)
        tmp_path_obj = Path(tmp_path)
        try:
            tmp_path_obj.write_bytes(data)
            shutil.move(str(tmp_path_obj), str(filepath))
        except Exception:
            tmp_path_obj.unlink(missing_ok=True)
            raise

        return original_size, len(data), quality

    except Exception as e:
        print(f"  ✗ 失败: {filepath.name} → {e}")
        return None


def main():
    if not TARGET_DIR.exists():
        print(f"错误：目录不存在 → {TARGET_DIR}")
        sys.exit(1)

    image_files = sorted([
        f for f in TARGET_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS
    ])

    if not image_files:
        print("未找到任何 JPG/JPEG 图片。")
        sys.exit(0)

    n = len(image_files)
    target_total_bytes = int(TARGET_TOTAL_MB * 1024 * 1024)
    target_per_file = target_total_bytes // n

    print(f"📁 目标目录  : {TARGET_DIR}")
    print(f"🖼  图片数量  : {n} 张")
    print(f"🎯 目标总大小: {TARGET_TOTAL_MB} MB")
    print(f"📐 每张目标  : {format_size(target_per_file)}")
    print("─" * 65)

    total_original = 0
    total_compressed = 0

    for i, filepath in enumerate(image_files, 1):
        result = compress_to_target(filepath, target_per_file)
        if result is None:
            continue

        orig, comp, q = result
        total_original += orig
        total_compressed += comp
        ratio = (1 - comp / orig) * 100 if orig > 0 else 0

        print(f"[{i:3d}/{n}] {filepath.name}  "
              f"{format_size(orig)} → {format_size(comp)}  "
              f"(节省 {ratio:.0f}%, quality={q})")

    print("─" * 65)
    saved = total_original - total_compressed
    overall_ratio = (1 - total_compressed / total_original) * 100 if total_original else 0
    print(f"✅ 完成！")
    print(f"📊 总计: {format_size(total_original)} → {format_size(total_compressed)}")
    print(f"💾 节省: {format_size(saved)}  ({overall_ratio:.1f}%)")

    if total_compressed > target_total_bytes:
        print(f"⚠️  实际大小 {format_size(total_compressed)} 略超目标 "
              f"{TARGET_TOTAL_MB} MB（部分图片已达最低质量限制）")
    else:
        print(f"✓  已控制在目标 {TARGET_TOTAL_MB} MB 以内 🎉")


if __name__ == "__main__":
    main()
