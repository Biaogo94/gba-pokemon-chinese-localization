"""Self-contained regressions; no game corpus or ROM is bundled."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from tools.i18n.extractor import extract_strings_from_c, extract_strings_from_inc
from tools.i18n.injector import inject_into_file, wrap_chinese

spec = importlib.util.spec_from_file_location("public_guard", SCRIPTS / "format_guard.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ToolkitTests(unittest.TestCase):
    def test_shared_scripts_cli_and_relative_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "data/scripts/common.inc"
            target.parent.mkdir(parents=True)
            target.write_text('Common:\n\t.string "Hello$"\n', encoding="utf-8")
            output = root / "corpus.json"
            subprocess.run([sys.executable, str(SCRIPTS / "extractor.py"),
                            "--root", str(root), "--output", str(output)], check=True)
            entry = json.loads(output.read_text(encoding="utf-8"))[0]
            self.assertEqual(entry["file"], "data/scripts/common.inc")
            self.assertEqual(entry["source"], "Hello$")

    def test_c_adjacent_literals_and_item_macro(self):
        text = 'const u8 greeting[] = _("Hello " "there!");\n'
        entries = extract_strings_from_c("src/strings.c", text, "engine_c")
        self.assertEqual(entries[0].source, "Hello there!")

    def test_conditional_blocks_are_not_merged(self):
        text = '#if IS_HNS\nText:\n.string "Johto$"\n#else\nText:\n.string "Hoenn$"\n#endif\n'
        entries = extract_strings_from_inc("data/text/test.inc", text)
        self.assertEqual([entry.source for entry in entries], ["Johto$", "Hoenn$"])

    def test_guard_keeps_placeholder_multiplicity(self):
        self.assertIn("PLACEHOLDER_MISMATCH", guard.validate_translation(
            "{PLAYER} and {PLAYER}$", "{PLAYER}来了。$"))

    def test_guard_rejects_extra_terminator_and_raw_newline(self):
        self.assertIn("TERMINATOR_MISMATCH", guard.validate_translation("Hi$", "你好$$"))
        self.assertIn("PHYSICAL_NEWLINE", guard.validate_translation("Hi$", "你\n好$"))

    def test_punctuation_page_and_placeholder(self):
        text = "宝" * 16 + "，继续。\\p{PLAYER}，你好！$"
        wrapped = wrap_chinese(text)
        self.assertEqual(wrapped.count("\\p"), 1)
        self.assertEqual(wrapped.count("{PLAYER}"), 1)
        self.assertNotIn("\\n，", wrapped)
        self.assertNotIn("\\l，", wrapped)
        self.assertEqual(wrap_chinese(wrapped), wrapped)

    def test_dry_run_stale_source_and_safe_reinjection(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "scripts.inc"
            original = 'Text:\n\t.string "Hello$"\n'
            target.write_text(original, encoding="utf-8")
            update = {"label": "Text", "index": 0, "source": "Hello$",
                      "translation": "你好！$", "match_type": "exact"}
            result = inject_into_file(str(target), [update], dry_run=True)
            self.assertEqual(result.applied, 1)
            self.assertEqual(target.read_text(encoding="utf-8"), original)
            stale = dict(update, source="Different$")
            self.assertEqual(inject_into_file(str(target), [stale]).skipped, 1)
            inject_into_file(str(target), [update])
            self.assertFalse(inject_into_file(str(target), [update]).changed)

    def test_control_guard_and_injector_cli_help(self):
        self.assertEqual(guard.validate_translation("Hi\\pBye$", "你好\\p再见$"), [])
        subprocess.run([sys.executable, str(SCRIPTS / "injector.py"), "--help"],
                       stdout=subprocess.DEVNULL, check=True)


if __name__ == "__main__":
    unittest.main()
