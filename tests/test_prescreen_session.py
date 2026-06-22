import importlib
import json
import sys
import types
from pathlib import Path


def import_app_module():
    sys.modules.setdefault("imagehash", types.SimpleNamespace(phash=lambda *args, **kwargs: "0" * 16))
    if "flask" not in sys.modules:
        class FakeFlask:
            def __init__(self, *args, **kwargs):
                self.static_folder = kwargs.get("static_folder", "static")

            def route(self, *args, **kwargs):
                return lambda fn: fn

            def after_request(self, fn):
                return fn

            def before_request(self, fn):
                return fn

            def run(self, *args, **kwargs):
                return None

        sys.modules["flask"] = types.SimpleNamespace(
            Flask=FakeFlask,
            Response=lambda *args, **kwargs: types.SimpleNamespace(headers={}, *args, **kwargs),
            abort=lambda *args, **kwargs: None,
            jsonify=lambda *args, **kwargs: args[0] if args else kwargs,
            request=types.SimpleNamespace(path="/", host="localhost:5057", headers={}, method="GET", args={}),
            send_file=lambda *args, **kwargs: None,
            send_from_directory=lambda *args, **kwargs: None,
        )
    sys.modules.pop("app", None)
    return importlib.import_module("app")


def make_info(path: Path, score=80.0, auto_reject=False, reason=None):
    app = import_app_module()
    path.write_bytes(b"fake")
    return app.ImageInfo(
        path=str(path),
        phash="0" * 16,
        size=path.stat().st_size,
        mtime=path.stat().st_mtime,
        exif_summary={"width": 1000, "height": 800, "file_size": path.stat().st_size},
        quality={
            "quality_score": score,
            "flags": ["very_blurry"] if auto_reject else [],
            "auto_reject": auto_reject,
            "reject_reason": reason,
        },
    )


def build_session(tmp_path, raw_groups, enabled=True, strength="standard"):
    app = import_app_module()
    return app.build_session_from_groups(
        str(tmp_path),
        dry_run=True,
        mode="copy",
        raw_groups=raw_groups,
        infos=[info for group in raw_groups for info in group],
        threshold_near=10,
        threshold_far=6,
        near_seconds=300,
        prescreen_enabled=enabled,
        prescreen_strength=strength,
    )


def test_single_auto_rejected_image_goes_to_losers_not_winners(tmp_path):
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")

    sess = build_session(tmp_path, [[bad]])

    group = sess.groups[0]
    assert group.finished is True
    assert group.winner is None
    assert group.losers == [bad.path]
    assert group.auto_rejected == [bad.path]
    assert group.auto_reject_reasons[bad.path] == "严重模糊"


def test_prescreen_removes_bad_photos_before_tournament(tmp_path):
    bad = make_info(tmp_path / "bad.jpg", score=5, auto_reject=True, reason="曝光过低")
    good1 = make_info(tmp_path / "good1.jpg", score=72)
    good2 = make_info(tmp_path / "good2.jpg", score=74)

    sess = build_session(tmp_path, [[bad, good1, good2]])

    group = sess.groups[0]
    assert group.finished is False
    assert group.losers == [bad.path]
    assert group.auto_rejected == [bad.path]
    assert group.left == good1.path
    assert group.right == good2.path


def test_standard_prescreen_auto_selects_clear_group_winner(tmp_path):
    best = make_info(tmp_path / "best.jpg", score=94)
    ok = make_info(tmp_path / "ok.jpg", score=62)
    weak = make_info(tmp_path / "weak.jpg", score=55)

    sess = build_session(tmp_path, [[best, ok, weak]], enabled=True, strength="standard")

    group = sess.groups[0]
    assert group.finished is True
    assert group.winner == best.path
    assert group.losers == [ok.path, weak.path]
    assert group.auto_selected is True


def test_disabled_prescreen_keeps_original_multi_group_flow(tmp_path):
    bad = make_info(tmp_path / "bad.jpg", score=5, auto_reject=True, reason="严重模糊")
    good = make_info(tmp_path / "good.jpg", score=90)

    sess = build_session(tmp_path, [[bad, good]], enabled=False)

    group = sess.groups[0]
    assert group.finished is False
    assert group.left == bad.path
    assert group.right == good.path
    assert group.losers == []
    assert group.auto_rejected == []


def test_auto_rejected_api_lists_rejected_items(tmp_path):
    app = import_app_module()
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")
    app.SESSION = build_session(tmp_path, [[bad]])

    payload = app.api_auto_rejected()

    assert payload["items"][0]["path"] == bad.path
    assert payload["items"][0]["reason"] == "严重模糊"
    assert payload["items"][0]["restored"] is False


def test_restore_rejected_adds_photo_to_winners_once(tmp_path):
    app = import_app_module()
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")
    app.SESSION = build_session(tmp_path, [[bad]])
    app.request.get_json = lambda *args, **kwargs: {"group_id": app.SESSION.groups[0].id, "path": bad.path}

    first = app.api_restore_rejected()
    second = app.api_restore_rejected()

    group = app.SESSION.groups[0]
    assert first["ok"] is True
    assert second["ok"] is True
    assert group.manual_restored == [bad.path]
    assert bad.path in group.extra_winners


def test_confirm_prescreen_marks_session_reviewed(tmp_path):
    app = import_app_module()
    bad = make_info(tmp_path / "bad.jpg", score=8, auto_reject=True, reason="严重模糊")
    app.SESSION = build_session(tmp_path, [[bad]])

    payload = app.api_confirm_prescreen()

    assert payload["ok"] is True
    assert app.SESSION.prescreen_reviewed is True


def test_confirm_prescreen_groups_only_passed_and_restored_photos(tmp_path):
    app = import_app_module()
    bad_drop = make_info(tmp_path / "drop.jpg", score=8, auto_reject=True, reason="严重模糊")
    bad_restore = make_info(tmp_path / "restore.jpg", score=9, auto_reject=True, reason="曝光过低")
    good = make_info(tmp_path / "good.jpg", score=88)
    infos = [bad_drop, bad_restore, good]
    app.LAST_INFOS = infos
    app.SESSION = app.build_prescreen_session_from_infos(
        str(tmp_path),
        dry_run=True,
        mode="copy",
        infos=infos,
        threshold_near=10,
        threshold_far=6,
        near_seconds=300,
        prescreen_enabled=True,
        prescreen_strength="standard",
    )
    app.request.get_json = lambda *args, **kwargs: {"group_id": "__prescreen__", "path": bad_restore.path}

    restored = app.api_restore_rejected()
    confirmed = app.api_confirm_prescreen()

    assert restored["ok"] is True
    assert confirmed["ok"] is True
    all_group_images = [p for group in app.SESSION.groups for p in group.images]
    assert good.path in all_group_images
    assert bad_restore.path in all_group_images
    assert bad_drop.path in all_group_images  # kept only as an auto-rejected loser record
    tournament_images = [
        p
        for group in app.SESSION.groups
        if not group.auto_rejected
        for p in group.images
    ]
    assert good.path in tournament_images
    assert bad_restore.path in tournament_images
    assert bad_drop.path not in tournament_images
    assert app.SESSION.prescreen_reviewed is True


def _make_info_for_app(app, path: Path, score=80.0):
    path.write_bytes(b"fake")
    return app.ImageInfo(
        path=str(path),
        phash="0" * 16,
        size=path.stat().st_size,
        mtime=path.stat().st_mtime,
        exif_summary={"width": 1000, "height": 800, "file_size": path.stat().st_size},
        quality={"quality_score": score, "flags": []},
    )


def test_state_saved_under_workspace_not_photo_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("PIC_SELECTER_WORKSPACE", str(tmp_path / "workspace"))
    app = import_app_module()
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    infos = [
        _make_info_for_app(app, photo_dir / "a.jpg", score=80),
        _make_info_for_app(app, photo_dir / "b.jpg", score=78),
    ]

    app.build_session_from_groups(
        str(photo_dir),
        dry_run=True,
        mode="copy",
        raw_groups=[infos],
        infos=infos,
        threshold_near=10,
        threshold_far=6,
        near_seconds=300,
        prescreen_enabled=False,
        prescreen_strength="standard",
    )

    state_file = app.state_path(str(photo_dir))
    progress_file = app.progress_path(str(photo_dir))
    assert state_file.exists()
    assert progress_file.exists()
    assert str(state_file).startswith(str(tmp_path / "workspace"))
    assert not (photo_dir / app.STATE_FILENAME).exists()
    assert not (photo_dir / app.PIC_DIR).exists()

    progress = json.loads(progress_file.read_text(encoding="utf-8"))
    assert progress["folder"] == str(photo_dir)
    assert progress["total_groups"] == 1
    assert progress["unfinished_groups"] == 1
    assert progress["unfinished_group_details"][0]["pending_count"] == 0


def test_resume_session_restores_workspace_state(tmp_path, monkeypatch):
    monkeypatch.setenv("PIC_SELECTER_WORKSPACE", str(tmp_path / "workspace"))
    app = import_app_module()
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    left = _make_info_for_app(app, photo_dir / "left.jpg", score=80)
    right = _make_info_for_app(app, photo_dir / "right.jpg", score=78)
    group = app.GroupState(images=[left.path, right.path], left=left.path, right=right.path)
    sess = app.SessionState(
        folder=str(photo_dir),
        dry_run=True,
        mode="copy",
        engine="fast",
        groups=[group],
        prescreen_reviewed=True,
        meta={left.path: {"quality_score": 80}, right.path: {"quality_score": 78}},
    )
    app.save_state(sess)
    app.SESSION = None
    app.LAST_INFOS = None
    app.JOB = None
    app.request.get_json = lambda *args, **kwargs: {"folder": str(photo_dir)}

    payload = app.api_resume_session()

    assert payload["ok"] is True
    assert payload["resumed"] is True
    assert app.SESSION is not None
    assert app.SESSION.folder == str(photo_dir)
    assert app.SESSION.groups[0].left == left.path
    assert payload["summary"]["unfinished_groups"] == 1


def test_load_state_migrates_legacy_photo_folder_state(tmp_path, monkeypatch):
    monkeypatch.setenv("PIC_SELECTER_WORKSPACE", str(tmp_path / "workspace"))
    app = import_app_module()
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    left = str(photo_dir / "legacy-left.jpg")
    right = str(photo_dir / "legacy-right.jpg")
    legacy_state = {
        "schema": 6,
        "folder": str(photo_dir),
        "dry_run": True,
        "mode": "copy",
        "engine": "fast",
        "current_group": 0,
        "threshold_near": 10,
        "threshold_far": 6,
        "near_seconds": 300,
        "prescreen_enabled": True,
        "prescreen_strength": "standard",
        "prescreen_reviewed": True,
        "prescreen_rejected": [],
        "prescreen_reject_reasons": {},
        "prescreen_restored": [],
        "companions": {},
        "meta": {left: {"quality_score": 80}, right: {"quality_score": 78}},
        "groups": [{
            "images": [left, right],
            "pending": [],
            "left": left,
            "right": right,
            "losers": [],
            "winner": None,
            "extra_winners": [],
            "finished": False,
            "applied": False,
        }],
    }
    (photo_dir / app.STATE_FILENAME).write_text(
        json.dumps(legacy_state, ensure_ascii=False),
        encoding="utf-8",
    )

    loaded = app.load_state(str(photo_dir))

    assert loaded is not None
    assert loaded.groups[0].left == left
    assert loaded.meta[left]["quality_score"] == 80
    assert app.state_path(str(photo_dir)).exists()
    assert str(app.state_path(str(photo_dir))).startswith(str(tmp_path / "workspace"))


def test_saved_session_meta_and_delete_do_not_touch_photo_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("PIC_SELECTER_WORKSPACE", str(tmp_path / "workspace"))
    app = import_app_module()
    photo_dir = tmp_path / "photos"
    photo_dir.mkdir()
    left = _make_info_for_app(app, photo_dir / "left.jpg", score=80)
    right = _make_info_for_app(app, photo_dir / "right.jpg", score=78)
    sess = app.SessionState(
        folder=str(photo_dir),
        dry_run=True,
        mode="copy",
        engine="fast",
        groups=[app.GroupState(images=[left.path, right.path], left=left.path, right=right.path)],
        prescreen_reviewed=True,
    )
    app.save_state(sess)

    app.request.get_json = lambda *args, **kwargs: {
        "folder": str(photo_dir),
        "note": "鱼妹第一轮",
        "archived": True,
    }
    updated = app.api_saved_session_meta()
    assert updated["ok"] is True
    summary = app.saved_progress_summary(str(photo_dir))
    assert summary["note"] == "鱼妹第一轮"
    assert summary["archived"] is True
    assert not (photo_dir / "task_meta.json").exists()

    task_dir = app.workspace_task_dir(str(photo_dir))
    assert task_dir.exists()
    app.request.get_json = lambda *args, **kwargs: {"folder": str(photo_dir)}
    deleted = app.api_delete_saved_session()
    assert deleted["ok"] is True
    assert not task_dir.exists()
    assert left.path and right.path
    assert Path(left.path).exists()
    assert Path(right.path).exists()
